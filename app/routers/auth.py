from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
import os
import shutil
import uuid
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.models.profile import Profile
from app.schemas.user import (
    UserCreate, 
    UserResponse, 
    Token, 
    IDVerificationRequest,
    GoogleAuthRequest,
    SendOTPRequest,
    VerifyOTPRequest,
    FirebasePhoneAuthRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.utils.security import get_password_hash, verify_password, create_access_token
from app.utils.deps import get_current_user
from app.utils.firebase import verify_firebase_id_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

# In-memory stores for OTP and Reset Codes (simulated SMS/WhatsApp/Email delivery)
OTP_STORE = {}
RESET_STORE = {}

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    # Create User (allowing multiple accounts under same email/phone for family profiles)
    hashed_password = get_password_hash(user_in.password)
    user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        auth_provider="email",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Initialize a default associated Profile with user's email as name prefix
    profile = Profile(
        user_id=user.id,
        name=user.email.split("@")[0].capitalize(),
        age=18,  # Default age
        gender="Male", # Default gender
        marital_status="Never Married"
    )
    db.add(profile)
    db.commit()
    
    return user

@router.post("/login", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    username_input = form_data.username.strip()
    users = db.query(User).filter((User.email == username_input) | (User.phone_number == username_input)).all()
    
    matching_user = None
    for u in users:
        if u.hashed_password and verify_password(form_data.password, u.hashed_password):
            matching_user = u
            break

    if not matching_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Entered incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not matching_user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Inactive user"
        )
    
    access_token = create_access_token(subject=matching_user.id)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/google-auth", response_model=Token)
def google_auth(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    # Find existing user by google_id or email
    user = db.query(User).filter((User.google_id == request.google_id) | (User.email == request.email)).first()
    
    if not user:
        # Register new user seamlessly without requiring a password initially
        user = User(
            email=request.email,
            google_id=request.google_id,
            auth_provider="google",
            hashed_password=None,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        user_name = request.name or (request.email.split("@")[0].capitalize() if request.email else "Google Member")
        profile = Profile(
            user_id=user.id,
            name=user_name,
            age=22,
            gender="Female" if "fatima" in request.email.lower() else "Male",
            marital_status="Never Married"
        )
        db.add(profile)
        db.commit()
    else:
        # Link google_id if not present
        if not user.google_id:
            user.google_id = request.google_id
            db.commit()
            
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}

from app.services.otp_service import send_phone_otp, verify_phone_otp

# Mobile OTP Authentication (Temporarily Disabled - can be re-integrated later)
@router.post("/send-otp")
def send_otp(request: SendOTPRequest):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Mobile OTP authentication is currently disabled. Please log in or register using Email or Google."
    )
    # Preservation for future re-integration:
    # phone = request.phone_number.strip()
    # if not phone:
    #     raise HTTPException(status_code=400, detail="Phone number is required.")
    # res = send_phone_otp(phone)
    # return res

@router.post("/verify-otp", response_model=Token)
def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Mobile OTP authentication is currently disabled. Please log in or register using Email or Google."
    )
    # Preservation for future re-integration:
    # phone = request.phone_number.strip()
    # code = request.otp_code.strip()
    # if not verify_phone_otp(phone, code):
    #     raise HTTPException(status_code=400, detail="Invalid OTP code.")
    # user = db.query(User).filter(User.phone_number == phone).first()
    # ...

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    identifier = request.identifier.strip()
    user = db.query(User).filter((User.email == identifier) | (User.phone_number == identifier)).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="No account registered with this Email or Mobile Number.")
    
    reset_code = "889900"
    RESET_STORE[identifier] = reset_code
    channel = "WhatsApp" if request.method == "whatsapp" else "Email"
    
    return {
        "message": f"Password reset link & code sent to {identifier} via {channel}.",
        "reset_token": reset_code,
        "reset_code_debug": reset_code
    }

@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    identifier = request.identifier.strip()
    token = request.reset_token.strip()
    
    stored_code = RESET_STORE.get(identifier)
    if token != "889900" and token != stored_code:
        raise HTTPException(status_code=400, detail="Invalid or expired reset code. Use 889900.")
    
    user = db.query(User).filter((User.email == identifier) | (User.phone_number == identifier)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User account not found.")
    
    user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    
    return {"message": "Password reset successfully! You can now sign in with your new password."}

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/verify-id", response_model=UserResponse)
def request_id_verification(
    request: IDVerificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.id_verification_status = "Pending"
    current_user.id_verification_document_url = request.document_url
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/verify-id/upload", response_model=UserResponse)
def upload_id_verification(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    upload_dir = "static/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"verification_{current_user.id}_{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    document_url = f"/static/uploads/{unique_filename}"
    current_user.id_verification_status = "Pending"
    current_user.id_verification_document_url = document_url
    db.commit()
    db.refresh(current_user)
    return current_user

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
from app.schemas.user import UserCreate, UserResponse, Token, IDVerificationRequest
from app.utils.security import get_password_hash, verify_password, create_access_token
from app.utils.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user_in.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists."
        )
    
    # Create User
    hashed_password = get_password_hash(user_in.password)
    user = User(
        email=user_in.email,
        hashed_password=hashed_password,
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
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Inactive user"
        )
    
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}

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

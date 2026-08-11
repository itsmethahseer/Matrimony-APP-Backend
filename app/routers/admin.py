from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import datetime

from app.database import get_db
from app.models.user import User
from app.models.profile import Profile, Photo
from app.schemas.user import UserResponse
from app.schemas.profile import PhotoResponse
from app.utils.deps import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin Console"])

def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required."
        )
    return current_user

class VerificationAction(BaseModel):
    action: str  # "approve" or "reject"

class PendingDocItem(BaseModel):
    user_id: int
    user_email: str
    user_name: str
    document_url: str
    status: str

class PendingPhotoItem(BaseModel):
    photo_id: int
    user_id: int
    user_email: str
    user_name: str
    photo_url: str
    is_main: bool
    is_approved: bool
    created_at: datetime.datetime

class PendingVerificationsResponse(BaseModel):
    documents: List[PendingDocItem]
    photos: List[PendingPhotoItem]

@router.get("/pending-verifications", response_model=PendingVerificationsResponse)
def get_pending_verifications(
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    # Pending documents
    pending_users = db.query(User).filter(User.id_verification_status == "Pending").all()
    documents = []
    for u in pending_users:
        profile = db.query(Profile).filter(Profile.user_id == u.id).first()
        documents.append(PendingDocItem(
            user_id=u.id,
            user_email=u.email,
            user_name=profile.name if profile else u.email,
            document_url=u.id_verification_document_url or "",
            status=u.id_verification_status
        ))

    # Pending photos
    pending_photos = db.query(Photo).filter(Photo.is_approved == False).all()
    photos = []
    for p in pending_photos:
        user = db.query(User).filter(User.id == p.user_id).first()
        profile = db.query(Profile).filter(Profile.user_id == p.user_id).first()
        photos.append(PendingPhotoItem(
            photo_id=p.id,
            user_id=p.user_id,
            user_email=user.email if user else f"user_{p.user_id}",
            user_name=profile.name if profile else f"User {p.user_id}",
            photo_url=p.url,
            is_main=p.is_main,
            is_approved=p.is_approved,
            created_at=p.created_at
        ))

    return PendingVerificationsResponse(documents=documents, photos=photos)

@router.post("/verify-id/{user_id}", response_model=UserResponse)
def verify_user_document(
    user_id: int,
    action_in: VerificationAction,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    action = action_in.action.lower()
    if action == "approve":
        target_user.id_verification_status = "Verified"
        target_user.id_verified_at = datetime.datetime.utcnow()
    elif action == "reject":
        target_user.id_verification_status = "Rejected"
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'approve' or 'reject'.")

    db.commit()
    db.refresh(target_user)
    return target_user

@router.post("/verify-photo/{photo_id}")
def verify_user_photo(
    photo_id: int,
    action_in: VerificationAction,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    action = action_in.action.lower()
    if action == "approve":
        photo.is_approved = True
        db.commit()
        return {"status": "success", "message": "Photo approved successfully"}
    elif action == "reject":
        db.delete(photo)
        db.commit()
        return {"status": "success", "message": "Photo rejected and deleted"}
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'approve' or 'reject'.")

@router.get("/users")
def get_all_users_admin(
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    users = db.query(User).all()
    result = []
    for u in users:
        profile = db.query(Profile).filter(Profile.user_id == u.id).first()
        photos_count = db.query(Photo).filter(Photo.user_id == u.id).count()
        unapproved_count = db.query(Photo).filter(Photo.user_id == u.id, Photo.is_approved == False).count()
        result.append({
            "id": u.id,
            "email": u.email,
            "name": profile.name if profile else "N/A",
            "is_admin": u.is_admin,
            "is_active": u.is_active,
            "membership_status": u.membership_status,
            "plan_type": u.plan_type,
            "id_verification_status": u.id_verification_status,
            "document_url": u.id_verification_document_url,
            "photos_count": photos_count,
            "unapproved_photos_count": unapproved_count,
            "created_at": u.created_at
        })
    return result

@router.post("/toggle-admin/{user_id}")
def toggle_admin_status(
    user_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    target.is_admin = not target.is_admin
    db.commit()
    db.refresh(target)
    return {"status": "success", "user_id": target.id, "is_admin": target.is_admin}

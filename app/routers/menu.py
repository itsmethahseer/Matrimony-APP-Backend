from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import datetime

from app.database import get_db
from app.models.user import User
from app.models.profile import Profile
from app.schemas.user import UserResponse, PlanUpgrade
from app.utils.deps import get_current_user
from app.utils.security import get_password_hash

router = APIRouter(prefix="/menu", tags=["Menu & Membership"])

from app.utils.credits import is_user_plan_active, is_user_plan_expired

class MenuSummaryResponse(BaseModel):
    name: str
    user_id: int
    membership_status: str
    plan_type: Optional[str]
    remaining_contact_views: int
    remaining_messages: int
    remaining_call_time: int
    credits: int
    plan_validity: Optional[datetime.datetime]
    is_expired: bool
    is_plan_active: bool

class FeedbackCreate(BaseModel):
    rating: int # 1 to 5
    comment: str

class AccountSettingsUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

@router.get("/summary", response_model=MenuSummaryResponse)
def get_menu_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    name = profile.name if profile else current_user.email.split("@")[0].capitalize()
    
    now = datetime.datetime.utcnow()
    is_expired = False
    if current_user.plan_validity and current_user.plan_validity <= now:
        is_expired = True
        if current_user.membership_status == "Premium":
            current_user.membership_status = "Expired"
            db.commit()
            db.refresh(current_user)
    elif current_user.plan_validity and current_user.plan_validity > now:
        if current_user.membership_status != "Premium" and current_user.plan_type:
            current_user.membership_status = "Premium"
            db.commit()
            db.refresh(current_user)

    if current_user.is_admin:
        return MenuSummaryResponse(
            name=name,
            user_id=current_user.id,
            membership_status="Admin",
            plan_type="Administrator",
            remaining_contact_views=9999,
            remaining_messages=9999,
            remaining_call_time=9999,
            credits=9999,
            plan_validity=None,
            is_expired=False,
            is_plan_active=True
        )

    plan_active = is_user_plan_active(current_user)

    return MenuSummaryResponse(
        name=name,
        user_id=current_user.id,
        membership_status=current_user.membership_status,
        plan_type=current_user.plan_type,
        remaining_contact_views=current_user.remaining_contact_views,
        remaining_messages=current_user.remaining_messages,
        remaining_call_time=current_user.remaining_call_time,
        credits=current_user.credits,
        plan_validity=current_user.plan_validity,
        is_expired=is_expired,
        is_plan_active=plan_active
    )


@router.post("/subscribe", response_model=UserResponse)
def subscribe_or_upgrade(
    plan_in: PlanUpgrade,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upgrades or recharges user plan with credit rollover:
    - Silver (1 month): 20 contact views, 200 messages, 60 minutes calls, 100 credits, 30 days validity
    - Gold (3 months): 100 contact views, 1000 messages, 300 minutes calls, 500 credits, 90 days validity
    - Platinum (6 months): 9999 contact views, 9999 messages, 1000 minutes calls, 9999 credits, 180 days validity

    Rollover logic:
    - Unused credits, remaining messages, contact views, and call minutes from previous recharges
      are NOT cleared — they are extended and ADDED to the new plan credits.
    - If user recharges before expiry, new validity days are added onto their existing validity date.
    - If user recharges after expiry, validity starts from now.
    """
    if plan_in.payment_status != "Success":
        raise HTTPException(status_code=400, detail="Payment transaction failed. Please retry.")

    plan = plan_in.plan_type.lower()
    if plan == "silver":
        validity_days = 30
        contact_views = 20
        messages = 200
        call_time = 60
        credits_replenish = 100
    elif plan == "gold":
        validity_days = 90
        contact_views = 100
        messages = 1000
        call_time = 300
        credits_replenish = 500
    elif plan == "platinum":
        validity_days = 180
        contact_views = 9999
        messages = 9999
        call_time = 1000
        credits_replenish = 9999
    else:
        raise HTTPException(status_code=400, detail="Invalid plan type. Options: Silver, Gold, Platinum")

    now = datetime.datetime.utcnow()
    # 1. Validity extension logic
    if current_user.plan_validity and current_user.plan_validity > now:
        # Extend from existing expiration date
        current_user.plan_validity = current_user.plan_validity + datetime.timedelta(days=validity_days)
    else:
        # Start fresh validity from now
        current_user.plan_validity = now + datetime.timedelta(days=validity_days)

    # 2. Rollover & add balances onto existing credits
    current_user.membership_status = "Premium"
    current_user.plan_type = plan_in.plan_type.capitalize()

    if plan == "platinum":
        current_user.remaining_contact_views = 9999
        current_user.remaining_messages = 9999
        current_user.remaining_call_time = max((current_user.remaining_call_time or 0) + call_time, 1000)
        current_user.credits = 9999
    else:
        current_user.remaining_contact_views = (current_user.remaining_contact_views or 0) + contact_views
        current_user.remaining_messages = (current_user.remaining_messages or 0) + messages
        current_user.remaining_call_time = (current_user.remaining_call_time or 0) + call_time
        current_user.credits = (current_user.credits or 0) + credits_replenish
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/renew", response_model=UserResponse)
def renew_membership(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Renews existing plan if subscription has expired or is nearing expiry.
    """
    plan_to_renew = current_user.plan_type or "Silver"
    plan_in = PlanUpgrade(plan_type=plan_to_renew, payment_status="Success")
    return subscribe_or_upgrade(plan_in=plan_in, current_user=current_user, db=db)


@router.put("/settings", response_model=UserResponse)
def update_account_settings(
    settings_in: AccountSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if settings_in.email:
        existing = db.query(User).filter(User.email == settings_in.email, User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email address is already in use by another account.")
        current_user.email = settings_in.email
        
    if settings_in.password:
        current_user.hashed_password = get_password_hash(settings_in.password)
        
    if settings_in.is_active is not None:
        current_user.is_active = settings_in.is_active
        
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/notifications")
def get_notifications(current_user: User = Depends(get_current_user)):
    # Return mock matrimony system notifications
    return [
        {
            "id": 1,
            "title": "Welcome to Matrimony!",
            "message": "Complete your profile to get matches 10x faster.",
            "created_at": datetime.datetime.utcnow() - datetime.timedelta(hours=12)
        },
        {
            "id": 2,
            "title": "ID Verification Notice",
            "message": "Verify your ID to get a verified badge and gain trust from potential matches.",
            "created_at": datetime.datetime.utcnow() - datetime.timedelta(days=1)
        }
    ]


@router.post("/link-device")
def link_web_device(pairing_code: str, current_user: User = Depends(get_current_user)):
    return {
        "status": "success",
        "message": f"Successfully linked device with pairing code {pairing_code}",
        "linked_at": datetime.datetime.utcnow()
    }


@router.post("/feedback")
def submit_feedback(feedback: FeedbackCreate, current_user: User = Depends(get_current_user)):
    return {
        "status": "success",
        "message": "Thank you for your valuable feedback!",
        "received_at": datetime.datetime.utcnow()
    }


@router.get("/support")
def get_help_and_support():
    return {
        "support_email": "support@matrimonyapp.com",
        "hotline": "+1-800-MATRIMONY",
        "operating_hours": "24/7 Support",
        "faq": [
            {"question": "How do I edit my profile?", "answer": "Go to View/Edit profile in the sidebar menu and update any details."},
            {"question": "What happens when contact views run out?", "answer": "You will need to upgrade/subscribe to Silver, Gold, or Platinum plans to get more views."}
        ]
    }


class PaymentConfigResponse(BaseModel):
    merchant_upi_id: str
    merchant_name: str

@router.get("/payment-config", response_model=PaymentConfigResponse)
def get_payment_config():
    from app.config import settings
    return PaymentConfigResponse(
        merchant_upi_id=settings.MERCHANT_UPI_ID,
        merchant_name=settings.MERCHANT_NAME
    )

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.profile import Profile
from app.models.interaction import (
    Interest, ProfileVisit, ContactView, Favourite, Note, Block, Pass
)
from app.schemas.interaction import (
    InterestResponse, InterestCreate, InterestUpdate,
    ProfileVisitResponse, ContactViewResponse, FavouriteResponse, FavouriteCreate,
    NoteResponse, NoteCreate, BlockResponse, BlockCreate, PassResponse, PassCreate
)
from app.utils.deps import get_current_user
from app.utils.credits import get_action_credit_cost, is_user_plan_active, is_user_plan_expired

router = APIRouter(prefix="/explore", tags=["Explore & Interactions"])

# --- INTERESTS ---
@router.post("/interests", response_model=InterestResponse, status_code=status.HTTP_201_CREATED)
def send_interest(
    interest_in: InterestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if interest_in.receiver_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot send an interest to yourself.")
    
    # Check if receiver exists
    receiver = db.query(User).filter(User.id == interest_in.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Recipient user not found.")
        
    # Check for existing block
    blocked = db.query(Block).filter(
        or_(
            and_(Block.blocker_id == current_user.id, Block.blocked_id == receiver.id),
            and_(Block.blocker_id == receiver.id, Block.blocked_id == current_user.id)
        )
    ).first()
    if blocked:
        raise HTTPException(status_code=403, detail="Cannot send interest to this profile.")

    # Check for existing interest in the same direction
    existing = db.query(Interest).filter(
        Interest.sender_id == current_user.id,
        Interest.receiver_id == receiver.id
    ).first()
    if existing:
        if existing.status == "Declined":
            existing.status = "Pending"
            db.commit()
            db.refresh(existing)
            return existing
        else:
            raise HTTPException(status_code=400, detail="Interest already sent.")

    # Check for existing interest in the opposite direction (from receiver to current user)
    opposite = db.query(Interest).filter(
        Interest.sender_id == receiver.id,
        Interest.receiver_id == current_user.id
    ).first()

    if opposite:
        # If there's an opposite pending or declined interest, auto-accept it to connect them
        if opposite.status in ["Pending", "Declined"]:
            opposite.status = "Accepted"
            db.commit()
            db.refresh(opposite)
            return opposite
        else:
            raise HTTPException(status_code=400, detail="You are already connected with this user.")

    # Check cost and deduct credits
    if not current_user.is_admin:
        if is_user_plan_expired(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your membership plan has expired. Your credits are preserved, but you must recharge or renew your plan to send interest requests."
            )
        cost = get_action_credit_cost(current_user.plan_type, "send_interest")
        if (current_user.credits or 0) < cost:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient credits remaining. Sending interest requires {cost} credits. Please upgrade your membership!"
            )
        current_user.credits -= cost

    # Create interest
    interest = Interest(sender_id=current_user.id, receiver_id=receiver.id, status="Pending")
    db.add(interest)
    db.commit()
    db.refresh(interest)
    return interest

@router.get("/interests/received", response_model=List[InterestResponse])
def get_received_interests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    interests = db.query(Interest).filter(
        Interest.receiver_id == current_user.id,
        Interest.status != "Declined"
    ).all()
    # We populate the profile objects in responses via serialization
    return interests

@router.get("/interests/sent", response_model=List[InterestResponse])
def get_sent_interests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Interest).filter(Interest.sender_id == current_user.id).all()

@router.put("/interests/{interest_id}", response_model=InterestResponse)
def respond_to_interest(
    interest_id: int,
    status_update: InterestUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    interest = db.query(Interest).filter(
        Interest.id == interest_id,
        Interest.receiver_id == current_user.id
    ).first()
    
    if not interest:
        raise HTTPException(status_code=404, detail="Interest request not found.")
        
    if status_update.status not in ["Accepted", "Declined"]:
        raise HTTPException(status_code=400, detail="Invalid status. Must be Accepted or Declined.")
        
    interest.status = status_update.status
    db.commit()
    db.refresh(interest)
    return interest

@router.delete("/interests/{interest_id}")
def cancel_interest(
    interest_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    interest = db.query(Interest).filter(Interest.id == interest_id).first()
    if not interest:
        raise HTTPException(status_code=404, detail="Interest request not found.")
    
    # Check if the current user is the sender
    if interest.sender_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only cancel interests that you sent.")
    
    # Only pending interests can be cancelled (cannot cancel if already accepted or declined)
    if interest.status != "Pending":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel interest that has already been {interest.status.lower()}."
        )
        
    # Refund credits
    cost = get_action_credit_cost(current_user.plan_type, "send_interest")
    current_user.credits += cost
    
    db.delete(interest)
    db.commit()
    return {"message": "Interest cancelled successfully.", "refunded_credits": cost, "id": interest_id}

@router.delete("/interests/cancel-by-user/{receiver_id}")
def cancel_interest_by_user(
    receiver_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    interest = db.query(Interest).filter(
        Interest.sender_id == current_user.id,
        Interest.receiver_id == receiver_id
    ).first()
    if not interest:
        raise HTTPException(status_code=404, detail="No sent interest found for this profile.")
        
    if interest.status != "Pending":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel interest that has already been {interest.status.lower()}."
        )
        
    cost = get_action_credit_cost(current_user.plan_type, "send_interest")
    current_user.credits += cost
    
    deleted_id = interest.id
    db.delete(interest)
    db.commit()
    return {"message": "Interest cancelled successfully.", "refunded_credits": cost, "id": deleted_id}

@router.get("/interests/status/{target_user_id}")
def get_interest_status(
    target_user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sent = db.query(Interest).filter(
        Interest.sender_id == current_user.id,
        Interest.receiver_id == target_user_id
    ).first()
    
    received = db.query(Interest).filter(
        Interest.sender_id == target_user_id,
        Interest.receiver_id == current_user.id
    ).first()
    
    return {
        "sent": {
            "id": sent.id,
            "status": sent.status,
            "created_at": sent.created_at.isoformat() if sent.created_at else None
        } if sent else None,
        "received": {
            "id": received.id,
            "status": received.status,
            "created_at": received.created_at.isoformat() if received.created_at else None
        } if received else None,
    }


# --- PROFILE VISITS ---
@router.get("/visits/my-visitors", response_model=List[ProfileVisitResponse])
def get_my_visitors(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # People who visited me
    return db.query(ProfileVisit).filter(ProfileVisit.visited_id == current_user.id).order_by(ProfileVisit.created_at.desc()).all()

@router.get("/visits/visited-by-me", response_model=List[ProfileVisitResponse])
def get_profiles_i_visited(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # People I visited
    return db.query(ProfileVisit).filter(ProfileVisit.visitor_id == current_user.id).order_by(ProfileVisit.created_at.desc()).all()


# --- CONTACT VIEWS (With quota check) ---
@router.post("/contact-views/{target_user_id}", response_model=ContactViewResponse)
def view_contact_details(
    target_user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if target_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot view your own contact record.")

    # Check if target exists
    target_user = db.query(User).filter(User.id == target_user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found.")

    # Check if contact already viewed
    existing = db.query(ContactView).filter(
        ContactView.viewer_id == current_user.id,
        ContactView.viewed_id == target_user_id
    ).first()

    if not existing:
        if not current_user.is_admin:
            # Contact views are only allowable for users with an active paid plan
            if not is_user_plan_active(current_user):
                if is_user_plan_expired(current_user):
                    raise HTTPException(
                        status_code=403,
                        detail="Your membership plan has expired. Your remaining credits and contact views are preserved, but you must recharge or renew your plan to unlock contact details."
                    )
                else:
                    raise HTTPException(
                        status_code=403,
                        detail="Contact views are not available on the Free tier. Please upgrade to a Silver, Gold, or Platinum plan to unlock contact details."
                    )

            cost = get_action_credit_cost(current_user.plan_type, "contact_view")
            if (current_user.remaining_contact_views or 0) <= 0 and (current_user.credits or 0) < cost:
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient contact views or credits remaining. Unlocking contact details requires {cost} credits. Please recharge your membership!"
                )
            
            # Decrement limit
            if current_user.remaining_contact_views and current_user.remaining_contact_views > 0:
                current_user.remaining_contact_views -= 1
            elif current_user.credits and current_user.credits >= cost:
                current_user.credits -= cost
        
        # Log view
        existing = ContactView(viewer_id=current_user.id, viewed_id=target_user_id)
        db.add(existing)
        db.commit()
        db.refresh(existing)
        
    return existing

@router.get("/contact-views/viewed-by-me", response_model=List[ContactViewResponse])
def get_contacts_i_viewed(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(ContactView).filter(ContactView.viewer_id == current_user.id).all()

@router.get("/contact-views/my-viewers", response_model=List[ContactViewResponse])
def get_my_contact_viewers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(ContactView).filter(ContactView.viewed_id == current_user.id).all()


# --- FAVOURITES ---
@router.post("/favourites", response_model=FavouriteResponse)
def add_to_favourites(
    fav_in: FavouriteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if fav_in.favourited_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot favourite yourself.")
        
    target = db.query(User).filter(User.id == fav_in.favourited_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target user not found.")
        
    existing = db.query(Favourite).filter(
        Favourite.user_id == current_user.id,
        Favourite.favourited_id == fav_in.favourited_id
    ).first()
    
    if existing:
        return existing
        
    fav = Favourite(user_id=current_user.id, favourited_id=fav_in.favourited_id)
    db.add(fav)
    db.commit()
    db.refresh(fav)
    return fav

@router.get("/favourites", response_model=List[FavouriteResponse])
def get_my_favourites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Favourite).filter(Favourite.user_id == current_user.id).all()

@router.delete("/favourites/{target_user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_favourites(
    target_user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    fav = db.query(Favourite).filter(
        Favourite.user_id == current_user.id,
        Favourite.favourited_id == target_user_id
    ).first()
    
    if not fav:
        raise HTTPException(status_code=404, detail="Favourite relation not found.")
        
    db.delete(fav)
    db.commit()
    return None


# --- NOTES ---
@router.post("/notes", response_model=NoteResponse)
def create_or_update_note(
    note_in: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Note targets a profile. Retrieve profile ID
    profile = db.query(Profile).filter(Profile.id == note_in.profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")
        
    existing_note = db.query(Note).filter(
        Note.user_id == current_user.id,
        Note.profile_id == note_in.profile_id
    ).first()
    
    if existing_note:
        existing_note.note_text = note_in.note_text
        db.commit()
        db.refresh(existing_note)
        return existing_note
        
    new_note = Note(
        user_id=current_user.id,
        profile_id=note_in.profile_id,
        note_text=note_in.note_text
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note

@router.get("/notes/{profile_id}", response_model=NoteResponse)
def get_note_for_profile(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    note = db.query(Note).filter(
        Note.user_id == current_user.id,
        Note.profile_id == profile_id
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")
    return note

@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")
        
    db.delete(note)
    db.commit()
    return None


# --- BLOCKED ---
@router.post("/blocked", response_model=BlockResponse)
def block_profile(
    block_in: BlockCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if block_in.blocked_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot block yourself.")
        
    target = db.query(User).filter(User.id == block_in.blocked_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target user not found.")
        
    existing = db.query(Block).filter(
        Block.blocker_id == current_user.id,
        Block.blocked_id == block_in.blocked_id
    ).first()
    
    if existing:
        return existing
        
    block = Block(blocker_id=current_user.id, blocked_id=block_in.blocked_id)
    db.add(block)
    
    # Remove any existing interests or favourites between these users
    db.query(Interest).filter(
        or_(
            and_(Interest.sender_id == current_user.id, Interest.receiver_id == block_in.blocked_id),
            and_(Interest.sender_id == block_in.blocked_id, Interest.receiver_id == current_user.id)
        )
    ).delete(synchronize_session=False)
    
    db.query(Favourite).filter(
        or_(
            and_(Favourite.user_id == current_user.id, Favourite.favourited_id == block_in.blocked_id),
            and_(Favourite.user_id == block_in.blocked_id, Favourite.favourited_id == current_user.id)
        )
    ).delete(synchronize_session=False)

    db.commit()
    db.refresh(block)
    return block

@router.get("/blocked", response_model=List[BlockResponse])
def get_blocked_profiles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Block).filter(Block.blocker_id == current_user.id).all()

@router.delete("/blocked/{target_user_id}", status_code=status.HTTP_204_NO_CONTENT)
def unblock_profile(
    target_user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    block = db.query(Block).filter(
        Block.blocker_id == current_user.id,
        Block.blocked_id == target_user_id
    ).first()
    
    if not block:
        raise HTTPException(status_code=404, detail="Block relation not found.")
        
    db.delete(block)
    db.commit()
    return None


# --- PASSED ---
@router.post("/passed", response_model=PassResponse)
def pass_profile(
    pass_in: PassCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if pass_in.passed_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot pass yourself.")
        
    target = db.query(User).filter(User.id == pass_in.passed_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target user not found.")
        
    existing = db.query(Pass).filter(
        Pass.passer_id == current_user.id,
        Pass.passed_id == pass_in.passed_id
    ).first()
    
    if existing:
        return existing
        
    pass_obj = Pass(passer_id=current_user.id, passed_id=pass_in.passed_id)
    db.add(pass_obj)
    db.commit()
    db.refresh(pass_obj)
    return pass_obj

@router.get("/passed", response_model=List[PassResponse])
def get_passed_profiles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Pass).filter(Pass.passer_id == current_user.id).all()

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, func, case
from typing import List, Optional
import datetime

from app.database import get_db
from app.models.user import User
from app.models.profile import Profile
from app.models.chat import ChatMessage
from app.models.interaction import Block
from app.schemas.chat import MessageCreate, MessageResponse, ChatSummaryResponse, ChatParticipant
from app.utils.deps import get_current_user
from app.utils.credits import get_action_credit_cost, is_user_plan_active, is_user_plan_expired

router = APIRouter(prefix="/inbox", tags=["Inbox & Chats"])

# Help helper to get online status
def is_user_online(last_active: datetime.datetime) -> bool:
    if not last_active:
        return False
    # Threshold for "online now" is 5 minutes
    return last_active > datetime.datetime.utcnow() - datetime.timedelta(minutes=5)

@router.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(
    msg_in: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if msg_in.receiver_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot message yourself.")

    # Check block
    blocked = db.query(Block).filter(
        or_(
            and_(Block.blocker_id == current_user.id, Block.blocked_id == msg_in.receiver_id),
            and_(Block.blocker_id == msg_in.receiver_id, Block.blocked_id == current_user.id)
        )
    ).first()
    if blocked:
        raise HTTPException(status_code=403, detail="Cannot send message. User has blocked you or is blocked.")

    # Check quotas and deduct credits (Skipped for Admin users)
    if not current_user.is_admin:
        if msg_in.message_type == "call":
            raise HTTPException(
                status_code=400,
                detail="In-app voice calling is no longer supported. Please connect directly using the match's mobile number or WhatsApp."
            )

        elif msg_in.message_type == "chat":
            has_active_plan = is_user_plan_active(current_user)

            if not has_active_plan:
                # Free tier & Expired users: Only allowed to send messages if someone messaged them first
                incoming_msg = db.query(ChatMessage).filter(
                    ChatMessage.sender_id == msg_in.receiver_id,
                    ChatMessage.receiver_id == current_user.id
                ).first()

                if not incoming_msg:
                    if is_user_plan_expired(current_user):
                        raise HTTPException(
                            status_code=403,
                            detail="Your membership plan has expired. Please recharge or renew your plan to initiate new conversations. You can still reply to messages received from paid members."
                        )
                    else:
                        raise HTTPException(
                            status_code=403,
                            detail="Free members can only reply to messages initiated by paid members. Please upgrade to a Silver, Gold, or Platinum plan to start new conversations."
                        )

                # Replying to an existing conversation — use cost table for consistency
                free_cost = get_action_credit_cost(current_user.plan_type, "send_message")
                if (current_user.remaining_messages or 0) <= 0 and (current_user.credits or 0) < free_cost:
                    raise HTTPException(
                        status_code=403,
                        detail="You have used all your message credits. Please upgrade your membership to continue chatting."
                    )
                if current_user.remaining_messages and current_user.remaining_messages > 0:
                    current_user.remaining_messages -= 1
                elif current_user.credits and current_user.credits >= free_cost:
                    current_user.credits -= free_cost

            else:
                # Active plan user: Can start new chats or reply
                cost = get_action_credit_cost(current_user.plan_type, "send_message")
                if (current_user.remaining_messages or 0) <= 0 and (current_user.credits or 0) < cost:
                    raise HTTPException(
                        status_code=403,
                        detail=f"Insufficient message balance. Sending a message requires {cost} credits. Please recharge your membership!"
                    )
                if current_user.remaining_messages and current_user.remaining_messages > 0:
                    current_user.remaining_messages -= 1
                elif current_user.credits and current_user.credits >= cost:
                    current_user.credits -= cost

    message = ChatMessage(
        sender_id=current_user.id,
        receiver_id=msg_in.receiver_id,
        message_text=msg_in.message_text,
        message_type=msg_in.message_type,
        call_duration=msg_in.call_duration
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@router.get("/conversations", response_model=List[ChatSummaryResponse])
def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Find all unique users this user has chatted with
    # Subquery to get max message ID for each conversation (Cross-DB compatible with PostgreSQL and SQLite)
    pair_low = case((ChatMessage.sender_id < ChatMessage.receiver_id, ChatMessage.sender_id), else_=ChatMessage.receiver_id)
    pair_high = case((ChatMessage.sender_id < ChatMessage.receiver_id, ChatMessage.receiver_id), else_=ChatMessage.sender_id)

    subquery = db.query(
        func.max(ChatMessage.id).label("max_id")
    ).filter(
        or_(
            ChatMessage.sender_id == current_user.id,
            ChatMessage.receiver_id == current_user.id
        )
    ).group_by(
        pair_low, pair_high
    ).subquery()

    subquery_select = db.query(subquery.c.max_id)
    messages = db.query(ChatMessage).filter(ChatMessage.id.in_(subquery_select)).order_by(desc(ChatMessage.created_at)).all()
    
    conversations = []
    for msg in messages:
        partner_id = msg.receiver_id if msg.sender_id == current_user.id else msg.sender_id
        partner = db.query(User).filter(User.id == partner_id).first()
        if not partner:
            continue
            
        partner_profile = db.query(Profile).filter(Profile.user_id == partner_id).first()
        partner_name = partner_profile.name if partner_profile else partner.email.split("@")[0]
        partner_age = partner_profile.age if partner_profile else 18
        partner_gender = partner_profile.gender if partner_profile else "Unknown"
        
        # Get main photo URL
        photo_url = None
        if partner.photos:
            main_photo = next((p for p in partner.photos if p.is_main), None)
            if main_photo:
                photo_url = main_photo.url
            elif len(partner.photos) > 0:
                photo_url = partner.photos[0].url

        # Check unread count
        unread_count = db.query(ChatMessage).filter(
            ChatMessage.sender_id == partner_id,
            ChatMessage.receiver_id == current_user.id,
            ChatMessage.is_read == False
        ).count()

        conversations.append(
            ChatSummaryResponse(
                participant=ChatParticipant(
                    id=partner_id,
                    name=partner_name,
                    gender=partner_gender,
                    age=partner_age,
                    photo_url=photo_url,
                    is_online=is_user_online(partner.last_active_at)
                ),
                last_message=msg,
                unread_count=unread_count
            )
        )
        
    return conversations


@router.get("/conversations/{participant_id}", response_model=List[MessageResponse])
def get_message_history(
    participant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Mark messages as read
    db.query(ChatMessage).filter(
        ChatMessage.sender_id == participant_id,
        ChatMessage.receiver_id == current_user.id,
        ChatMessage.is_read == False
    ).update({"is_read": True})
    db.commit()

    messages = db.query(ChatMessage).filter(
        or_(
            and_(ChatMessage.sender_id == current_user.id, ChatMessage.receiver_id == participant_id),
            and_(ChatMessage.sender_id == participant_id, ChatMessage.receiver_id == current_user.id)
        )
    ).order_by(ChatMessage.created_at.asc()).all()
    
    return messages


# --- CATEGORIZED FILTERS FOR INBOX ---
@router.get("/all", response_model=List[MessageResponse])
def get_all_inbox_messages(
    online_now: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns all sent/received messages. If online_now is True, 
    only returns messages where the other participant is currently active.
    """
    query = db.query(ChatMessage).filter(
        or_(
            ChatMessage.sender_id == current_user.id,
            ChatMessage.receiver_id == current_user.id
        )
    )

    if online_now:
        # We need to filter by other user's active status. Let's do a join.
        # User is online if last_active_at > 5 minutes ago
        threshold = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
        
        # We join User twice or filter using subquery
        online_user_ids = db.query(User.id).filter(User.last_active_at >= threshold).subquery()
        
        query = query.filter(
            or_(
                and_(ChatMessage.sender_id == current_user.id, ChatMessage.receiver_id.in_(online_user_ids)),
                and_(ChatMessage.receiver_id == current_user.id, ChatMessage.sender_id.in_(online_user_ids))
            )
        )

    return query.order_by(desc(ChatMessage.created_at)).all()


@router.get("/chats", response_model=List[MessageResponse])
def get_chats_only(
    online_now: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns only messages of type 'chat'.
    """
    query = db.query(ChatMessage).filter(
        ChatMessage.message_type == "chat",
        or_(
            ChatMessage.sender_id == current_user.id,
            ChatMessage.receiver_id == current_user.id
        )
    )

    if online_now:
        threshold = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
        online_user_ids = db.query(User.id).filter(User.last_active_at >= threshold).subquery()
        query = query.filter(
            or_(
                and_(ChatMessage.sender_id == current_user.id, ChatMessage.receiver_id.in_(online_user_ids)),
                and_(ChatMessage.receiver_id == current_user.id, ChatMessage.sender_id.in_(online_user_ids))
            )
        )

    return query.order_by(desc(ChatMessage.created_at)).all()


@router.get("/requests", response_model=List[MessageResponse])
def get_requests_only(
    online_now: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns only messages of type 'request'.
    """
    query = db.query(ChatMessage).filter(
        ChatMessage.message_type == "request",
        or_(
            ChatMessage.sender_id == current_user.id,
            ChatMessage.receiver_id == current_user.id
        )
    )

    if online_now:
        threshold = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
        online_user_ids = db.query(User.id).filter(User.last_active_at >= threshold).subquery()
        query = query.filter(
            or_(
                and_(ChatMessage.sender_id == current_user.id, ChatMessage.receiver_id.in_(online_user_ids)),
                and_(ChatMessage.receiver_id == current_user.id, ChatMessage.sender_id.in_(online_user_ids))
            )
        )

    return query.order_by(desc(ChatMessage.created_at)).all()


@router.get("/calls", response_model=List[MessageResponse])
def get_calls_only(
    online_now: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns only call logs.
    """
    query = db.query(ChatMessage).filter(
        ChatMessage.message_type == "call",
        or_(
            ChatMessage.sender_id == current_user.id,
            ChatMessage.receiver_id == current_user.id
        )
    )

    if online_now:
        threshold = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
        online_user_ids = db.query(User.id).filter(User.last_active_at >= threshold).subquery()
        query = query.filter(
            or_(
                and_(ChatMessage.sender_id == current_user.id, ChatMessage.receiver_id.in_(online_user_ids)),
                and_(ChatMessage.receiver_id == current_user.id, ChatMessage.sender_id.in_(online_user_ids))
            )
        )

    return query.order_by(desc(ChatMessage.created_at)).all()

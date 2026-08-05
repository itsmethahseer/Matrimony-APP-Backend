from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Membership fields
    membership_status = Column(String, default="Free")  # Free, Premium, Expired
    plan_type = Column(String, nullable=True)            # Silver, Gold, Platinum, etc.
    remaining_contact_views = Column(Integer, default=5)
    remaining_messages = Column(Integer, default=50)
    remaining_call_time = Column(Integer, default=0)    # in minutes
    credits = Column(Integer, default=25)
    plan_validity = Column(DateTime, nullable=True)
    
    # ID Verification
    id_verification_status = Column(String, default="Unverified") # Unverified, Pending, Verified, Rejected
    id_verification_document_url = Column(String, nullable=True)
    id_verified_at = Column(DateTime, nullable=True)

    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    photos = relationship("Photo", back_populates="user", cascade="all, delete-orphan")
    
    # Interactions
    interests_sent = relationship("Interest", foreign_keys="Interest.sender_id", back_populates="sender", cascade="all, delete-orphan")
    interests_received = relationship("Interest", foreign_keys="Interest.receiver_id", back_populates="receiver", cascade="all, delete-orphan")
    
    visits_sent = relationship("ProfileVisit", foreign_keys="ProfileVisit.visitor_id", back_populates="visitor", cascade="all, delete-orphan")
    visits_received = relationship("ProfileVisit", foreign_keys="ProfileVisit.visited_id", back_populates="visited", cascade="all, delete-orphan")
    
    contacts_viewed = relationship("ContactView", foreign_keys="ContactView.viewer_id", back_populates="viewer", cascade="all, delete-orphan")
    contact_viewers = relationship("ContactView", foreign_keys="ContactView.viewed_id", back_populates="viewed", cascade="all, delete-orphan")
    
    favourites_sent = relationship("Favourite", foreign_keys="Favourite.user_id", back_populates="user", cascade="all, delete-orphan")
    favourites_received = relationship("Favourite", foreign_keys="Favourite.favourited_id", back_populates="favourited", cascade="all, delete-orphan")
    
    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")
    
    blocked_sent = relationship("Block", foreign_keys="Block.blocker_id", back_populates="blocker", cascade="all, delete-orphan")
    blocked_received = relationship("Block", foreign_keys="Block.blocked_id", back_populates="blocked", cascade="all, delete-orphan")
    
    passed_sent = relationship("Pass", foreign_keys="Pass.passer_id", back_populates="passer", cascade="all, delete-orphan")
    passed_received = relationship("Pass", foreign_keys="Pass.passed_id", back_populates="passed", cascade="all, delete-orphan")
    
    messages_sent = relationship("ChatMessage", foreign_keys="ChatMessage.sender_id", back_populates="sender", cascade="all, delete-orphan")
    messages_received = relationship("ChatMessage", foreign_keys="ChatMessage.receiver_id", back_populates="receiver", cascade="all, delete-orphan")

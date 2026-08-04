import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class Interest(Base):
    __tablename__ = "interests"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, default="Pending") # Pending, Accepted, Declined
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('sender_id', 'receiver_id', name='_sender_receiver_uc'),
    )

    sender = relationship("User", foreign_keys=[sender_id], back_populates="interests_sent")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="interests_received")

    @property
    def sender_profile(self):
        return self.sender.profile if self.sender else None

    @property
    def receiver_profile(self):
        return self.receiver.profile if self.receiver else None


class ProfileVisit(Base):
    __tablename__ = "profile_visits"

    id = Column(Integer, primary_key=True, index=True)
    visitor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    visited_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    visitor = relationship("User", foreign_keys=[visitor_id], back_populates="visits_sent")
    visited = relationship("User", foreign_keys=[visited_id], back_populates="visits_received")

    @property
    def visitor_profile(self):
        return self.visitor.profile if self.visitor else None

    @property
    def visited_profile(self):
        return self.visited.profile if self.visited else None


class ContactView(Base):
    __tablename__ = "contact_views"

    id = Column(Integer, primary_key=True, index=True)
    viewer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    viewed_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    viewer = relationship("User", foreign_keys=[viewer_id], back_populates="contacts_viewed")
    viewed = relationship("User", foreign_keys=[viewed_id], back_populates="contact_viewers")

    @property
    def viewed_profile(self):
        return self.viewed.profile if self.viewed else None


class Favourite(Base):
    __tablename__ = "favourites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    favourited_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('user_id', 'favourited_id', name='_user_favourited_uc'),
    )

    user = relationship("User", foreign_keys=[user_id], back_populates="favourites_sent")
    favourited = relationship("User", foreign_keys=[favourited_id], back_populates="favourites_received")

    @property
    def favourited_profile(self):
        return self.favourited.profile if self.favourited else None


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    note_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="notes")


class Block(Base):
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, index=True)
    blocker_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    blocked_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('blocker_id', 'blocked_id', name='_blocker_blocked_uc'),
    )

    blocker = relationship("User", foreign_keys=[blocker_id], back_populates="blocked_sent")
    blocked = relationship("User", foreign_keys=[blocked_id], back_populates="blocked_received")


class Pass(Base):
    __tablename__ = "passes"

    id = Column(Integer, primary_key=True, index=True)
    passer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    passed_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('passer_id', 'passed_id', name='_passer_passed_uc'),
    )

    passer = relationship("User", foreign_keys=[passer_id], back_populates="passed_sent")
    passed = relationship("User", foreign_keys=[passed_id], back_populates="passed_received")

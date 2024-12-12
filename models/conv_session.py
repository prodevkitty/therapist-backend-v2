from sqlalchemy import Column, Integer, ForeignKey, Boolean, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from database import Base
from datetime import datetime

class ConvSession(Base):
    __tablename__ = 'conv_sessions'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    session_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    start_time = Column(TIMESTAMP, default=datetime.utcnow)
    end_time = Column(TIMESTAMP, nullable=True)
    is_completed = Column(Boolean, default=False)

    user = relationship("User", back_populates="sessions")
    conversation_history = relationship("ConversationHistory", back_populates="conv_session")
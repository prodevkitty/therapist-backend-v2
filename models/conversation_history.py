from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class ConversationHistory(Base):
    __tablename__ = 'conversation_history'
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('therapy_sessions.id'), nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    message = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    therapy_session = relationship("TherapySession", back_populates="conversation_history")
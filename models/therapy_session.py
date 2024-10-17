from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base

class TherapySession(Base):
    __tablename__ = 'therapy_sessions'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    session_date = Column(DateTime)
    session_duration = Column(Integer)
    notes = Column(Text)

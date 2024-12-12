from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base

class Progress(Base):
    __tablename__ = 'progress_tracking'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    date = Column(DateTime)
    stress_level = Column(Integer)
    negative_thoughts_reduction = Column(Integer)
    positive_thoughts_increase = Column(Integer)

    user = relationship("User", back_populates="progress")
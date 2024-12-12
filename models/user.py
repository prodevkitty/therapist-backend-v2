from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)

    subscription = relationship("Subscription", uselist=False, back_populates="user")
    user_tools = relationship("UserTool", back_populates="user")
    progress = relationship("Progress", back_populates="user")
    sessions = relationship("ConvSession", back_populates="user")
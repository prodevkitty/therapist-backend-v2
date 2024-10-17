from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base

class UserTool(Base):
    __tablename__ = 'user_tools'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    tool_id = Column(Integer, ForeignKey('tools.id'))
    interaction_date = Column(DateTime)

    user = relationship("User", back_populates="user_tools")
    tool = relationship("Tool", back_populates="user_tools")
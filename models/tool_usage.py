from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base

class ToolUsage(Base):
    __tablename__ = 'tools_usage'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    tool_type = Column(String)
    usage_time = Column(DateTime)
    notes = Column(Text)

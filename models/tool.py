from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Tool(Base):
    __tablename__ = 'tools'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    category = Column(String)  # e.g., 'gratitude_journal', 'breathing_technique', etc.
    content = Column(Text)  # This can store the actual content or a link to the content

    user_tools = relationship("UserTool", back_populates="tool")
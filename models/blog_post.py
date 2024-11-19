from sqlalchemy import Column, Integer, String, Text
from database import Base
from datetime import datetime

class BlogPost(Base):
    __tablename__ = "blog_posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    date = Column(String, default=datetime.utcnow)
    views = Column(Integer, default=0)
    mainImage = Column(String)
    detailedImage1 = Column(String)
    detailedImage2 = Column(String)
    newsText = Column(Text)
    overlayText = Column(Text)
    detailText = Column(Text)
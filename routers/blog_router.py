from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db


router = APIRouter()

class BlogPostBase(BaseModel):
    title: str
    author: str
    date: str
    views: int
    mainImage: str
    detailedImage1: str
    detailedImage2: str
    newsText: str
    overlayText: str
    detailText: str

class BlogPostCreate(BlogPostBase):
    pass

class BlogPost(BlogPostBase):
    id: int

    class Config:
        orm_mode = True


# API to create a new blog post
@router.post("/posts/", response_model=BlogPost)
def create_blog_post(post: BlogPostCreate, db: Session = Depends(get_db)):
    return create_blog_post(db=db, post=post)

# API to get a blog post by ID
@router.get("/posts/{post_id}", response_model=BlogPost)
def get_blog_post(post_id: int, db: Session = Depends(get_db)):
    db_post = get_blog_post(db=db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post

# API to get all blog posts
@router.get("/posts/", response_model=list[BlogPost])
def get_blog_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    posts = get_blog_posts(db=db, skip=skip, limit=limit)
    return posts

# API to update a blog post
@router.put("/posts/{post_id}", response_model=BlogPost)
def update_blog_post(post_id: int, post: BlogPostCreate, db: Session = Depends(get_db)):
    db_post = update_blog_post(db=db, post_id=post_id, post=post)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post

# API to delete a blog post
@router.delete("/posts/{post_id}", response_model=BlogPost)
def delete_blog_post(post_id: int, db: Session = Depends(get_db)):
    db_post = delete_blog_post(db=db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post

def create_blog_post(db: Session, post: BlogPostCreate):
    db_post = BlogPost(
        title=post.title,
        author=post.author,
        date=post.date,
        views=post.views,
        mainImage=post.mainImage,
        detailedImage1=post.detailedImage1,
        detailedImage2=post.detailedImage2,
        newsText=post.newsText,
        overlayText=post.overlayText,
        detailText=post.detailText,
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

# Get a blog post by ID
def get_blog_post(db: Session, post_id: int):
    return db.query(BlogPost).filter(BlogPost.id == post_id).first()

# Get all blog posts
def get_blog_posts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(BlogPost).offset(skip).limit(limit).all()

# Update a blog post
def update_blog_post(db: Session, post_id: int, post: BlogPostCreate):
    db_post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if db_post:
        db_post.title = post.title
        db_post.author = post.author
        db_post.date = post.date
        db_post.views = post.views
        db_post.mainImage = post.mainImage
        db_post.detailedImage1 = post.detailedImage1
        db_post.detailedImage2 = post.detailedImage2
        db_post.newsText = post.newsText
        db_post.overlayText = post.overlayText
        db_post.detailText = post.detailText
        db.commit()
        db.refresh(db_post)
        return db_post
    return None

# Delete a blog post
def delete_blog_post(db: Session, post_id: int):
    db_post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if db_post:
        db.delete(db_post)
        db.commit()
        return db_post
    return None

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
from database import get_db
from models.progress import Progress

router = APIRouter()

class ProgressCreate(BaseModel):
    user_id: int
    date: str
    stress_level: int
    negative_thoughts_reduction: int
    positive_thoughts_increase: int

class ProgressResponse(BaseModel):
    id: int
    user_id: int
    date: datetime
    stress_level: int
    negative_thoughts_reduction: int
    positive_thoughts_increase: int

@router.post("/progress", response_model=ProgressResponse)
def track_progress(progress: ProgressCreate, db: Session = Depends(get_db)):
    db_progress = Progress(**progress.dict())
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress

@router.get("/progress/{user_id}", response_model=list[ProgressResponse])
def get_progress(user_id: int, db: Session = Depends(get_db)):
    return db.query(Progress).filter(Progress.user_id == user_id).all()
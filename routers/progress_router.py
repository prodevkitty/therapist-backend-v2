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

    class Config:
        orm_mode = True

@router.post("/create", response_model=ProgressResponse)
def create_progress(progress: ProgressCreate, db: Session = Depends(get_db)):
    """
    Create a new progress entry.
    """
    db_progress = Progress(**progress.dict())
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress

@router.get("/get/{user_id}", response_model=list[ProgressResponse])
def get_progress(user_id: int, db: Session = Depends(get_db)):
    """
    Get all progress entries for a user.
    """
    print(user_id)
    return db.query(Progress).filter(Progress.user_id == user_id).all()

# @router.get("/progress_report/{user_id}", response_model=list[ProgressResponse])
# def get_weekly_progress_report(user_id: int, db: Session = Depends(get_db)):
#     """
#     Get the weekly progress report for a user.
#     """
#     from datetime import datetime, timedelta
#     one_week_ago = datetime.now() - timedelta(days=7)
#     return db.query(Progress).filter(Progress.user_id == user_id, Progress.date >= one_week_ago).all()
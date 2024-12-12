from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.subscription import Subscription
from models.user import User
from database import get_db
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class SubscriptionCreate(BaseModel):
    user_id: int
    subscription_type: str

class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    subscription_type: str
    sessions_used: int
    next_billing_date: datetime
    is_active: bool

    class Config:
        orm_mode = True


@router.post("/subscriptions", response_model=SubscriptionResponse)
def create_subscription(subscription: SubscriptionCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == subscription.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_subscription = Subscription(**subscription.dict())
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription

@router.get("/subscriptions/{user_id}", response_model=SubscriptionResponse)
def get_subscription(user_id: int, db: Session = Depends(get_db)):
    db_subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    if not db_subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return db_subscription
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from services.auth_service import authenticate_user, create_access_token, register_user
from database import get_db

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    password: str
    email: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    print("user data", user)
    db_user = authenticate_user(db, username=user.username, password=user.password)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    message =  register_user(db=db, username=user.username, password=user.password, email=user.email)
    if message["msg"] == "User registered successfully":
        access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, username=user.username, password=user.password)
    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from services.auth_service import authenticate_user, create_access_token, register_user, validate_access_token
from database import get_db
from models.user import User

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    password: str
    email: str

class UserLogin(BaseModel):
    email: str
    password: str

class AutoLogin(BaseModel):
    token: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_name: str
    user_id: int

class TokenWithEmail(BaseModel):
    access_token: str
    token_type: str
    user_name: str
    user_id: int
    email: str

@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    print("user data", user)
    db_user = authenticate_user(db, email=user.email, password=user.password)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    message =  register_user(db=db, username=user.username, password=user.password, email=user.email)
    print("register message", message)
    if message["msg"] == "User registered successfully":
        access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "user_id": message["user_id"], "user_name": message["user_name"]}

@router.post("/token", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    print("user data", user)
    db_user = authenticate_user(db, email=user.email, password=user.password)
    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": db_user.email})
    print("login message:")
    print(db_user)
    print(db_user.username, db_user.id)
    return {"access_token": access_token, "token_type": "bearer", "user_id": db_user.id, "user_name": db_user.username}

@router.post("/auto-token", response_model=TokenWithEmail)
def auth(param: AutoLogin, db: Session = Depends(get_db)):
    payload = validate_access_token(param.token)
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Unregistered user")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id, "user_name": user.username, "email": user.email}
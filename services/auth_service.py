import redis
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import time

load_dotenv()  # Load environment variables from .env file

# Database URL and Redis setup
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")

# Set up PostgreSQL connection
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Set up Redis connection
redis_client = redis.StrictRedis.from_url(REDIS_URL)

# Cryptographic context for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "prodevkitty_jwt_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 100
# User model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

# Initialize database
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Password hashing and verification
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
def check_token_form_auth(token: str):
    token_status = redis_client.get(token)
    token_ttl = redis_client.ttl(token)  # Get time-to-live of the token
    print(f"token_status: {token_status}, token_ttl: {token_ttl}")
    return "ok"
# Create JWT token and store in Redis
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    # Print SECRET_KEY for debugging
    print(f"SECRET_KEY: {SECRET_KEY}")

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print("created token: ", token)
    print(f"Token created at: {datetime.utcnow()}, expires at: {expire}")

    # Store token in Redis with an expiration
    try:
        success = redis_client.setex(token, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), "active")
        if success:
            print("Token successfully stored in Redis.")
            print(f"Token TTL: {redis_client.ttl(token)} seconds")
        else:
            print("Failed to store token in Redis.")
    except redis.exceptions.ConnectionError as e:
        print(f"Redis connection failed: {e}")

    return token

def validate_access_token(token: str):
    print("Token validation started!")
    try:
        # Decode the token and extract the payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded Payload: {payload}")

        # Check token status and TTL in Redis
        token_status = redis_client.get(token)
        token_ttl = redis_client.ttl(token)
        print(f"Token status: {token_status}, TTL: {token_ttl}")

        # Log the current time and expiration time for comparison
        current_time = datetime.utcnow()
        expiration_time = datetime.utcfromtimestamp(payload['exp'])
        print(f"Current time: {current_time}, Token expiration time: {expiration_time}")

        if not token_status or token_ttl <= 0:
            redis_client.delete(token)  # Remove token from Redis
            raise JWTError("Token expired or invalid")

        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expired or invalid")





# Invalidate JWT token (Logout)
def invalidate_access_token(token: str):
    redis_client.delete(token)

# Authenticate user during login
def authenticate_user(db, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return user

# Register a new user
def register_user(db, username: str, password: str):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed_password = hash_password(password)
    new_user = User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "User registered successfully"}

import redis
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import HTTPException
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from models.user import User

load_dotenv()  # Load environment variables from .env file

# Database URL and Redis setup
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")

# Set up Redis connection
redis_client = redis.StrictRedis.from_url(REDIS_URL)

# Cryptographic context for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "prodevkitty_jwt_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

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

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    print("test:")
    if user and verify_password(password, user.password_hash):
        return user
    return None

# Register a new user
def register_user(db, username: str, password: str, email: str):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed_password = hash_password(password)
    new_user = User(username= username, email= email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "User registered successfully", "user_id": new_user.id, "user_name": new_user.username}

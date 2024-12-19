from fastapi import FastAPI
# from pydantic import BaseModel
# from sqlalchemy.orm import Session
# from services.auth_service import User, authenticate_user, create_access_token, register_user, validate_access_token
# from services.ai_service import get_answer, process_audio_to_text
# from services.notification_service import generate_notifications
from fastapi.middleware.cors import CORSMiddleware
from routers import auth_router, progress_router, subscription_router, tool_router, blog_router
import socketio
from database import Base, engine
from services.socket_service import sio

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust to match your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(progress_router.router, prefix="/progress", tags=["progress"])
app.include_router(subscription_router.router, prefix="/subscriptions", tags=["subscriptions"])
app.include_router(tool_router.router, prefix="/tools", tags=["tools"])
app.include_router(blog_router.router, prefix="/blog", tags=["blog"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Therapy App"}

# Initialize Socket.IO server
app = socketio.ASGIApp(sio, app)

# Initialize database
Base.metadata.create_all(bind=engine)

# --- Run with Socket.IO & FastAPI (using Uvicorn) ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

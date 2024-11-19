from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from services.auth_service import User, authenticate_user, create_access_token, register_user, validate_access_token
from services.ai_service import get_answer, process_audio_to_text
from services.notification_service import generate_notifications
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError
from routers import auth_router, progress_router, subscription_router, tool_router, blog_router
import socketio
from database import Base, engine, SessionLocal

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
sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='asgi')
app = socketio.ASGIApp(sio, app)


# Initialize database
Base.metadata.create_all(bind=engine)

@sio.event
async def connect(sid, environ, auth):
    """
    Handle new client connection.

    Args:
        sid (str): Session ID.
        environ (dict): Environment variables.
        auth (dict): Authentication data.

    Raises:
        JWTError: If the authorization token is missing or invalid.
        HTTPException: If there is an error during token validation or notification generation.
    """
    print(f"Auth data received: {auth}")
    db: Session = SessionLocal()
    try:
        if not auth or 'token' not in auth:
            raise JWTError("Missing authorization token")

        # Extract and validate token
        token = auth['token'].split(" ")[1]
        user = validate_access_token(token)  # This will raise JWTError if token is invalid
        username = user['sub']
        print(f"User {user['sub']} connected with session {sid}")
        notification_message = await generate_notifications(username, db)
        print(notification_message)
        await sio.emit('first_notification', {'notification': notification_message}, to=sid)
    except HTTPException as e:
        # Emit the error to the client
        print(f"Auth error: {e.detail}")
        await sio.emit('auth_error', {'code': e.status_code, 'message': e.detail}, to=sid)
        await sio.disconnect(sid)  # Disconnect after sending errors
    except Exception as e:
        # Handle general exceptions
        print(f"Unexpected error during connection: {e}")
        await sio.emit('auth_error', {'code': 500, 'message': 'Internal server error'}, to=sid)
        await sio.disconnect(sid)
    
# Handle AI conversation via Socket.IO
@sio.event
async def user_message(sid, data):
    print(f"Received message from {sid}: {data}")  # Log to check if data is received
    
    # Validate the token before processing the message
    try:
        # Process the message
        message = data.get("text")
        is_voice = data.get("is_voice", False)
        token = data.get("token")
        if not token:
            raise JWTError("Missing authorization token")
        
        user = validate_access_token(token)  # Validate the token
        
        print(f"User {user['sub']} is sending a message with session {sid}")

        if is_voice:
            text = await process_audio_to_text(message)  # Placeholder function
            print(f"Received voice input, transcribed to: {text}")
        else:
            text = message

        # Construct AI instructions
        therapy_instructions = (
            "You are a virtual therapist. Engage the user in a reflective dialogue. Begin by asking broad questions "
            "to understand their emotional state and concerns. Use supportive and empathetic language. Reflect on "
            "what they share to build a clear understanding. Avoid giving direct solutions; instead, guide them "
            "to explore their thoughts and feelings. Ask only one question at a time, ensuring each builds upon the "
            "user's response. For example: 'How have you been feeling lately?' and then move to specific questions "
            "based on their answers. Summarize key points and offer gentle, non-prescriptive suggestions."
        )
        
        # Combine user input with instructions
        input_text = f"{therapy_instructions}\n\nUser input: {text}"  

        # Process the text input with AI
        ai_response = await get_answer(input_text)
        
        # Ensure ai_response is a string or object with the 'response' key
        response_data = {"response": ai_response.get('response') if isinstance(ai_response, dict) else ai_response}
        
        # Emit the AI response back to the client
        await sio.emit('ai_response', response_data, to=sid)

    except HTTPException as e:
        # Handle token validation issues
        print(f"Token error during message processing: {e.detail}")
        await sio.emit('auth_error', {'code': e.status_code, 'message': e.detail}, to=sid)
        await sio.disconnect(sid)  # Disconnect user on token issues

    except Exception as e:
        # General error handling
        print(f"Unexpected error during message processing: {e}")
        await sio.emit('auth_error', {'code': 500, 'message': 'Internal server error'}, to=sid)
        await sio.disconnect(sid)


@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")


# --- Run with Socket.IO & FastAPI (using Uvicorn) ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

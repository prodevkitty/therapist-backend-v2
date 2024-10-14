from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from services.auth_service import User, authenticate_user, create_access_token, register_user, get_db, validate_access_token, invalidate_access_token, check_token_form_auth
from services.ai_service import get_answer, process_audio_to_text
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
import socketio
from jose import JWTError

# FastAPI app
sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='asgi')
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust to match your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


# OAuth2 scheme for handling bearer tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models for requests
class TextRequest(BaseModel):
    text: str
    is_voice: bool = False  # False for text input, True for voice

class RegisterUserRequest(BaseModel):
    username: str
    password: str

class LoginUserRequest(BaseModel):
    username: str
    password: str

# # AI Route for Text/Voice inputs via HTTP
# @app.post("/ai/ask")
# async def ask_ai(request: TextRequest, user: User = Depends(authenticate_user)):
#     response = await process_input(request.text, request.is_voice)
#     return response

# Registration route
@app.post("/register")
def register(user: RegisterUserRequest, db: Session = Depends(get_db)):
    return register_user(db, user.username, user.password)

# Login route (returns JWT token)
@app.post("/token")
def login(user: LoginUserRequest, db: Session = Depends(get_db)):
    authenticated_user = authenticate_user(db, user.username, user.password)
    access_token = create_access_token(data={"sub": authenticated_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Protected route (requires a valid token)
@app.get("/protected")
def protected_route(token: str = Depends(oauth2_scheme)):
    payload = validate_access_token(token)
    return {"message": "This is a protected route", "user": payload["sub"]}

# Logout route (invalidate token)
@app.post("/logout")
def logout(token: str = Depends(oauth2_scheme)):
    invalidate_access_token(token)
    return {"msg": "Successfully logged out"}

@app.get("/check_token/{token}")
def check_token(token: str):
    result = check_token_form_auth(token)
    

# --- SOCKET.IO INTEGRATION ---

# Middleware for validating JWT tokens in Socket.IO connections



# Mount Socket.IO server on FastAPI app using ASGI
app = socketio.ASGIApp(sio, app)

@sio.event
async def connect(sid, environ, auth):
    print(f"Auth data received: {auth}")
    try:
        if not auth or 'token' not in auth:
            raise JWTError("Missing authorization token")

        # Extract and validate token
        token = auth['token'].split(" ")[1]
        user = validate_access_token(token)  # This will raise JWTError if token is invalid
        print(f"User {user['sub']} connected with session {sid}")
    except HTTPException as e:
        # Emit the error to the client
        print(f"Auth error: {e.detail}")
        await sio.emit('auth_error', {'code': e.status_code, 'message': e.detail}, to=sid)
        await sio.disconnect(sid)  # Disconnect after sending error

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

        # Process the text input with AI
        ai_response = await get_answer(text)
        
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

from sqlalchemy.orm import Session
from services.auth_service import User, validate_access_token
from services.ai_service import get_answer, process_audio_to_text, get_advanced_answer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import HTTPException
from services.notification_service import generate_notifications
from jose import JWTError
import socketio
from database import SessionLocal
from models.conv_session import ConvSession
from models.conversation_history import ConversationHistory
from models.progress import Progress
from datetime import datetime

sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='asgi')

active_sessions = {}

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
        email = user['sub']
        print(f"User {user['sub']} connected with session {sid}")
        notification_message = await generate_notifications(email, db)
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
async def user_message_advanced(sid, data):
    print(f"Received advanced message from {sid}: {data}")  # Log to check if data is received
    db: Session = SessionLocal()
    try:
        message = data.get("text")
        token = data.get("token")
        if not token:
            raise JWTError("Missing authorization token")
        
        user = validate_access_token(token)
        user_email = user['sub']
        user_record = db.query(User).filter(User.email == user_email).first()
        user_id = user_record.id if user_record else None

        print(f"User ID: {user_id}")

        if not user_id:
            raise JWTError("User not found")

        # Check if there's an active session for the user
        if user_id not in active_sessions:
            # Create a new session in the database
            new_session = ConvSession(user_id=user_id)
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            active_sessions[user_id] = str(new_session.session_id)
        session_id = active_sessions[user_id]
        
        # Save user message to the conversation history
        new_message = ConversationHistory(
            session_id=session_id,
            role="user",
            message=message
        )
        db.add(new_message)
        db.commit()
        # Fetch session conversation history
        conversation_history = db.query(ConversationHistory).filter_by(session_id=session_id).all()
        print(f"Conversation history: {conversation_history}")
        # Prepare AI input
        instructions = (
            "You are a virtual therapist. Use the conversation history to reflect on past questions and answers. But remember, do not return history to user."
            "Build on the user's input and avoid repeating yourself. Provide empathetic, supportive, and actionable guidance "
            "when sufficient context is available. Summarize key points before offering suggestions."
        )
        conversation_input = [{"role": "system", "content": instructions}] + [
            {"role": msg.role, "content": msg.message} for msg in conversation_history
        ]
        print(f"Conversation input: {conversation_input}")
        # Process conversation with AI
        ai_response = await get_advanced_answer(conversation_input)
        print(f"AI response: {ai_response}")
        # Save AI response to the conversation history
        new_ai_response = ConversationHistory(
            session_id=session_id,
            role="assistant",
            message=ai_response.get('response') if isinstance(ai_response, dict) else ai_response
        )
        db.add(new_ai_response)
        db.commit()
        # Emit the AI response back to the client
        response_data = {"response": new_ai_response.message}
        await sio.emit('ai_response', response_data, to=sid)
    except JWTError as e:
        print(f"JWT Error: {e}")
        await sio.emit('auth_error', {'code': 401, 'message': 'Unauthorized'}, to=sid)
        await sio.disconnect(sid)
    except Exception as e:
        print(f"Unexpected error during message processing: {e}")
        await sio.emit('auth_error', {'code': 500, 'message': 'Internal server error'}, to=sid)
    finally:
        db.close()


@sio.event
async def end_session(sid, data):
    db: Session = SessionLocal()
    try:
        token = data.get("token")
        if not token:
            raise JWTError("Missing authorization token")
        
        user = validate_access_token(token)
        user_email = user['sub']
        user_record = db.query(User).filter(User.email == user_email).first()
        user_id = user_record.id if user_record else None

        if not user_id:
            raise JWTError("User not found")


        # Save the updated progress data
        progress_data = {
            "user_id": user_id,
            "date": datetime.utcnow(),
            "stress_level": data.get("stress_level"),
            "negative_thoughts_reduction": data.get("negative_thoughts_reduction"),
            "positive_thoughts_increase": data.get("positive_thoughts_increase")
        }
        new_progress = Progress(**progress_data)
        db.add(new_progress)
        db.commit()

        # Mark session as completed
        if user_id in active_sessions:
            print(active_sessions)
            session_id = active_sessions[user_id]
            session = db.query(ConvSession).filter_by(session_id=session_id).first()
            if session:
                session.end_time = datetime.utcnow()
                session.is_completed = True
                db.commit()
                del active_sessions[user_id]
                await sio.emit('session_ended', {"message": "Session ended successfully"}, to=sid)
            else:
                await sio.emit('session_error', {"message": "Session not found"}, to=sid)
        else:
            await sio.emit('session_error', {"message": "No active session found"}, to=sid)

    except JWTError as e:
        print(f"JWT Error: {e}")
        await sio.emit('auth_error', {'code': 401, 'message': 'Unauthorized'}, to=sid)
    except Exception as e:
        print(f"Error ending session: {e}")
        await sio.emit('session_error', {"message": "Internal server error"}, to=sid)
    finally:
        db.close()

@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")
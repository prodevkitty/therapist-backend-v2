import os
from cerebras.cloud.sdk import Cerebras
from pydub import AudioSegment
import speech_recognition as sr
import base64
import io

# Initialize Cerebras client
api_key = os.getenv('CEREBRAS_API_KEY')
if not api_key:
    raise ValueError("CEREBRAS_API_KEY environment variable not set")

client = Cerebras(api_key=api_key)

# Preprocessing text
def preprocess_text(text: str):
    # You can add more sophisticated text preprocessing here
    return text

# Function to process audio (Base64-encoded) and convert it to text
async def process_audio_to_text(base64_audio: str):
    # Decode the Base64 audio data into binary
    audio_data = base64.b64decode(base64_audio)

    # Convert the binary audio data into a format suitable for speech recognition
    audio_file = io.BytesIO(audio_data)  # Create an in-memory bytes buffer
    recognizer = sr.Recognizer()

    try:
        # Read the audio file into SpeechRecognition's AudioFile object
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)  # Read the entire audio file

            # Recognize speech using Google Web Speech API
            text = recognizer.recognize_google(audio)
            return text

    except sr.UnknownValueError:
        # Handle if the speech was unintelligible
        raise ValueError("Could not understand the audio")
    except sr.RequestError:
        # Handle if the request to the recognition service failed
        raise ValueError("Could not request results from the speech recognition service")


# Processing the response from AI (Llama3.1-8B)
async def get_answer(input_text: str):
    preprocessed_text = preprocess_text(input_text)
    
    chat_completion = client.chat.completions.create(
        model="llama3.1-8b",
        messages=[{"role": "user", "content": preprocessed_text}],
    )
    
    message_content = chat_completion.choices[0].message.content
    return {"response": message_content}

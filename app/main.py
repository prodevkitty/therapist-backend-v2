from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from transformers import BertTokenizer
from googletrans import Translator
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text
import httpx

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    # Add other origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Load the pre-trained BERT model and tokenizer
model_path = 'app/models/experts-bert-tensorflow2-pubmed-v2'  # Update with the actual path to your model
model = hub.load(model_path)

# Initialize the translator
translator = Translator()

async def translate_text(text: str, src_lang: str, dest_lang: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            'https://translate.googleapis.com/translate_a/single',
            params={
                'client': 'gtx',
                'sl': src_lang,
                'tl': dest_lang,
                'dt': 't',
                'q': text,
            },
        )
        translated_text = response.json()[0][0][0]
        return translated_text


# Path to your local preprocessor
preprocessor_path = "app/models/bert-tensorflow2-en-uncased-preprocess-v3"

# Load the preprocessor from the local directory
preprocessor = hub.load(preprocessor_path)

# Define a function to preprocess text
def preprocess_text(text):
    # Tokenize the text input
    tokenize = hub.KerasLayer(preprocessor.tokenize)
    tokenized_input = tokenize(tf.constant([text]))
    
    # Pack the tokenized input
    seq_length = 128  # Define your sequence length
    bert_pack_inputs = hub.KerasLayer(preprocessor.bert_pack_inputs, arguments=dict(seq_length=seq_length))
    encoder_input = bert_pack_inputs([tokenized_input])
    
    return encoder_input


@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_input = data.get("message", "")
    
    # Detect the language of the input
    detected_lang = translator.detect(user_input).lang
    
    # Supported languages
    supported_languages = ['en', 'es', 'pt', 'pt-BR', 'it', 'ar', 'qu', 'zh', 'ko']
    
    # If the input is in a supported language other than English, translate it to English
    if detected_lang in supported_languages and detected_lang != 'en':
        translated_input = await translate_text(user_input, src_lang=detected_lang, dest_lang='en')
    else:
        translated_input = user_input
    
    # Preprocess the text
    preprocessed_text = preprocess_text(translated_input)

    
    # Generate response in English
    outputs = model(preprocessed_text)
    print("Outputs of tensorflow modle is like this:")
    print(outputs)
    pooled_output = outputs['pooled_output']
    print("pooled_output:")
    print(pooled_output)
    sequence_output = outputs['sequence_output']
    print("sequence output:")
    print(sequence_output)
    predicted_class_id = tf.argmax(pooled_output, axis=-1).numpy()[0]
    print("predicted_class_id:")
    print(predicted_class_id)
    
    
    # Map the predicted class ID to a response (this mapping should be defined based on your model's training)
    response_mapping = {
        0: "I'm here to help you.",
        1: "Can you please elaborate on that?",
        # Add more mappings based on your model's output classes
    }
    english_response = response_mapping.get(predicted_class_id, "I'm not sure how to respond to that.")
    
    # If the original input was in a supported language other than English, translate the response back to that language
    if detected_lang in supported_languages and detected_lang != 'en':
        final_response = await translate_text(english_response, src_lang='en', dest_lang=detected_lang)
    else:
        final_response = english_response
    
    return JSONResponse(content={"response": final_response})
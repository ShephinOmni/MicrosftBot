from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi import  Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse  # Import StreamingResponse
import asyncio
import boto3
import requests
import json
from boto3.session import Session
from io import BytesIO
import os
import boto3 
import base64
from pydantic import BaseModel
from dotenv import load_dotenv

app = FastAPI()

# Load environment variables (if stored in Google Drive)
dotenv_path = '.env'  # Adjust the path
load_dotenv(dotenv_path)



# AWS Credentials and Polly Client Initialization
# Retrieve API and AWS credentials
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
AWS_REGION = os.getenv('AWS_REGION')
OPENAI_ENDPOINT = os.getenv('OPENAI_endpoint')
polly_client = boto3.client('polly', aws_access_key_id=AWS_ACCESS_KEY,
                            aws_secret_access_key=AWS_SECRET_KEY,
                            region_name=AWS_REGION)

# Jinja2 template directory
templates = Jinja2Templates(directory="templates")


 # Directory for static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class TextData(BaseModel):
    text: str


# Route for index page
@app.get("/")
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Route for meeting page
@app.get("/meeting")
async def get_meeting(request: Request):
    return templates.TemplateResponse("meeting.html", {"request": request})



@app.post("/meeting/api/sendtext")
async def send_text(data: TextData):
    chat_response = get_chatgpt_response(data.text)
    audio_stream = aws_polly_speak(chat_response)
    audio_stream_bytes = BytesIO(audio_stream).read()  # Read bytes from audio stream
    audio_stream_blob = base64.b64encode(audio_stream_bytes).decode()  # Convert to base64 string
    return {"chatResponse": chat_response, "audioStreamBlob": audio_stream_blob}



@app.post("/meeting/api/audio")
async def get_audio(data: TextData):
    # Convert the received text to speech
    audio_stream = aws_polly_speak(data.text)
    return StreamingResponse(BytesIO(audio_stream), media_type="audio/mpeg")



# Function to get ChatGPT response
def get_chatgpt_response(prompt):
    # Ensure OPENAI_API_KEY and OPENAI_ENDPOINT are loaded from environment variables
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_ENDPOINT = os.getenv('OPENAI_ENDPOINT')  # Ensure this is set in your .env file

    # Check if API key is loaded
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key is not set.")

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENAI_API_KEY}'
    }
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {'role': 'system', 'content': "Your custom system message here."},
            {'role': 'user', 'content': prompt},
        ]
    }
    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            data=json.dumps(data)
        )
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error in calling OpenAI API: {e}")

    # Check for non-success status codes
    if response.status_code != 200:
        error_detail = response.json().get('error', {}).get('message', 'Unknown error')
        raise HTTPException(status_code=response.status_code, detail=f"Error from ChatGPT API: {error_detail}")

    return response.json()['choices'][0]['message']['content']


def upload_to_s3(audio_stream, bucket_name, s3_filename):
    s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=AWS_REGION)
    s3_client.upload_fileobj(BytesIO(audio_stream), bucket_name, s3_filename)



# Function to synthesize speech using Amazon Polly
def aws_polly_speak(text):
    session = Session(
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )
    polly_client = session.client('polly')

    try:
        response = polly_client.synthesize_speech(
            VoiceId='Joanna',
            OutputFormat='mp3',
            Text=text
        )
        return response['AudioStream'].read()
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail="Error in Polly synthesis")




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

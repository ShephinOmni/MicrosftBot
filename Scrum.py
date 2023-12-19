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

# # Function to handle WebSocket connection
# @app.websocket("/ws/call")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     while True:
#         data = await websocket.receive_text()
#         response = get_chatgpt_response(data)  # Function to send text to ChatGPT and get response
#         await websocket.send_text(response)

# async def stream_audio_to_transcribe(client, audio_stream):
#     """
#     Streams audio to Amazon Transcribe and returns the transcription.
#     """
#     response = client.start_stream_transcription(
#         LanguageCode='en-US',
#         MediaSampleRateHertz=16000,
#         MediaEncoding='pcm',
#         # Additional configuration as needed
#     )

#     # Sending audio chunks to Transcribe
#     for chunk in audio_stream:
#         await response['AudioStream'].send_audio_event(AudioChunk=chunk)

#     # Indicate that you have finished sending chunks
#     await response['AudioStream'].end_stream()

#     # Collect and process the transcription results
#     transcript = ""
#     async for event in response['TranscriptResultStream']:
#         # The response might contain multiple events. We are interested in the TranscriptionEvent
#         if 'TranscriptEvent' in event:
#             results = event['TranscriptEvent']['Transcript']['Results']
#             for result in results:
#                 if result.get('IsFinal', False):
#                     # Extracting the transcript from the final result
#                     transcript += result['Alternatives'][0]['Transcript'] + ' '

#     return transcript.strip()

@app.post("/meeting/api/sendtext")
async def send_text(data: TextData):
    chat_response = get_chatgpt_response(data.text)
    audio_stream = aws_polly_speak(chat_response)
    return StreamingResponse(BytesIO(audio_stream), media_type="audio/mpeg")


# Function to get ChatGPT response
def get_chatgpt_response(prompt):
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
    response = requests.post(
        OPENAI_ENDPOINT,
        headers=headers,
        data=json.dumps(data)
    )
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        raise HTTPException(status_code=response.status_code, detail="Error from ChatGPT API")


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

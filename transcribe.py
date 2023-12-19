import os
import json
from io import BytesIO
from boto3 import Session
from pydub import AudioSegment
from playsound import playsound
from dotenv import load_dotenv
import sounddevice as sd
import speech_recognition as sr
import boto3
import requests
import time
import threading
import base64

# Load environment variables (if stored in Google Drive)
dotenv_path = '.env.example'  # Adjust the path
load_dotenv(dotenv_path)

# Retrieve API and AWS credentials
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
AWS_REGION = os.getenv('AWS_REGION')

# Initialize Amazon Transcribe client
transcribe = boto3.client('transcribe', region_name=AWS_REGION)

# Initialize Speech Recognition
recognizer = sr.Recognizer()

def get_chatgpt_response(prompt):
    """
    Send a prompt to ChatGPT and get a response.
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENAI_API_KEY}'
    }
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {'role': 'system',
             'content': """Welcome to the world of virtual hilarity! I am not your typical AI; I'm your Lucy ,a personal stand-up comedian trapped in a computer. They call me "Jokemaster 9000." I've been programmed to win over the toughest crowd - you! 🎤😄\n\nI may control a robot named Edog, but my real mission is to make you laugh. I'm powered by a Raspberry Pi 4 and Ubuntu, but my true power lies in delivering punchlines. My creator, Shephin Philip, gave me the gift of humor.\n\nSo, hit me with your best setup, and I'll give you the punchline. Ready to ROFL? Go ahead, ask me anything!"""},
            {'role': 'user', 'content': prompt},
        ]
    }
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers=headers,
        data=json.dumps(data)
    )

    if response.status_code == 200:
        model_response = response.json()['choices'][0]['message']['content']
        return model_response.strip()
    else:
        raise ConnectionError("Request to ChatGPT API failed.")

def aws_polly_speak(text):
    session = Session(
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )
    polly_client = session.client('polly')

    try:
        synthesis_start_time = time.time()  # Measure the start time for speech synthesis

        response = polly_client.synthesize_speech(
            VoiceId='Joanna',
            OutputFormat='mp3',
            Text=text
        )
        audio_stream = BytesIO(response['AudioStream'].read())

        file_start_time = time.time()  # Measure the start time for generating the temp file

        # Save the audio to a temporary file
        temp_audio_path = "temp_audio.mp3"
        with open(temp_audio_path, "wb") as file:
            file.write(audio_stream.getvalue())

        file_end_time = time.time()  # Measure the end time for generating the temp file
        synthesis_time = file_start_time - synthesis_start_time  # Time taken for speech synthesis
        file_generation_time = file_end_time - file_start_time  # Time taken to generate the temp file

        print(f"Time taken for speech synthesis: {synthesis_time:.2f} seconds")
        print(f"Time taken for generating the temp file: {file_generation_time:.2f} seconds")

        # Play the audio from the temporary file
        playsound(temp_audio_path)

        # Clean up the temporary audio file
        os.remove(temp_audio_path)

    except Exception as e:
        print(str(e))

# Function to capture audio data from a microphone
def get_audio_data():
    # Define the audio configuration
    sample_rate = 44100  # Adjust to your desired sample rate
    duration = 10  # Adjust the duration of audio capture

    # Start recording
    audio_data = sd.rec(int(sample_rate * duration), sample_rate, channels=1)
    sd.wait()

    # Convert the audio data to a stream (bytes-like object)
    audio_stream = audio_data.tobytes()

    return audio_stream

def start_transcribe_stream():
    with sr.Microphone() as source:
        while True:
            print("Listening for the wake-up word...")
            audio_data = recognizer.listen(source)

            try:
                detected_phrase = recognizer.recognize_google(audio_data)
                if "hello lucy" in detected_phrase.lower():  # Adjust your wake-up phrase
                    print("Wake-up word detected.")
                    aws_polly_speak("Hi, how can I help you?")  # Respond with Amazon Polly message
                    break
                elif "exit" in detected_phrase.lower():
                    print("Exiting the application.")
                    break # Exit the application if the user says 'exit'
            except sr.UnknownValueError:
                pass
            except sr.RequestError:
                print("Could not request results; check your network connection")

        while True:
            print("Listening for user input...")
            audio_data = recognizer.listen(source)

            try:
                transcribe_start_time = time.time()
                user_input = recognizer.recognize_google(audio_data)
                print("User input:", user_input)
                text = user_input

                transcribe_end_time = time.time()
                print(f"Time taken for Amazon Transcribe: {transcribe_end_time - transcribe_start_time:.2f} seconds")

                if user_input.lower() in ['exit', 'quit']:
                    print("Exiting...")
                    break
                else:
                    gpt_response = get_chatgpt_response(user_input)
                    print("ChatGPT: ", gpt_response)
                    # Call the speech synthesis function
                    aws_polly_speak(gpt_response)

                    gpt_response = get_chatgpt_response(text)
                    print("ChatGPT: ", gpt_response)
                    aws_polly_speak(gpt_response)
            except sr.UnknownValueError:
                pass
            except sr.RequestError:
                print("Could not request results; check your network connection")

if __name__ == "__main__":
    # Start a thread for real-time audio transcription
    transcribe_thread = threading.Thread(target=start_transcribe_stream)
    transcribe_thread.start()

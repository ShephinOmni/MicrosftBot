import boto3
import sounddevice as sd
import speech_recognition as sr
import time
from Scrum import get_chatgpt_response

# Initialize the Amazon Polly client
polly_client = boto3.client('polly')

# Speech Recognition
recognizer = sr.Recognizer()

# Function to synthesize speech using Amazon Polly
def aws_polly_speak(text):
    try:
        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Joanna'
        )
        if 'AudioStream' in response:
            # Play the audio using an appropriate audio player
            # This part needs to be implemented based on your specific requirements
            pass
    except Exception as e:
        print(f"Error in synthesizing speech: {e}")

# Function to capture audio data from a microphone
def get_audio_data():
    sample_rate = 44100  # Desired sample rate
    duration = 10  # Duration of audio capture

    audio_data = sd.rec(int(sample_rate * duration), sample_rate, channels=1)
    sd.wait()
    return audio_data.tobytes()

def start_transcribe_stream():
    with sr.Microphone() as source:
        while True:
            print("Listening for user input...")
            audio_data = recognizer.listen(source)

            try:
                user_input = recognizer.recognize_google(audio_data)
                print("User input:", user_input)

                if user_input.lower() in ['exit', 'quit']:
                    print("Exiting...")
                    break
                else:
                    gpt_response = get_chatgpt_response(user_input)
                    print("ChatGPT: ", gpt_response)
                    aws_polly_speak(gpt_response)
            except Exception as e:
                print(f"Error: {e}")


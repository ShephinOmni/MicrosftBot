from flask import Flask, request, Response, render_template, jsonify  # Import jsonify
from botbuilder.schema import Activity, ActivityTypes
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
import openai
import os
import json

app = Flask(__name__, template_folder="templates", static_url_path='/static')

# Load environment variables from .env file
from dotenv import load_dotenv
dotenv_path = '.env'
load_dotenv(dotenv_path)

# Get configuration settings from environment variables
MICROSOFT_APP_ID = os.getenv("MICROSOFT_APP_ID")
MICROSOFT_APP_PASSWORD = os.getenv("MICROSOFT_APP_PASSWORD")
OPENAI_API_KEYS = os.getenv("OPENAI_API_KEY")

# Create BotFrameworkAdapter
bot_settings = BotFrameworkAdapterSettings(MICROSOFT_APP_ID, MICROSOFT_APP_PASSWORD)
bot_adapter = BotFrameworkAdapter(bot_settings)

# Initialize OpenAI with your API key
openai.api_key = OPENAI_API_KEYS

# Define the conversation state
conversation_state = {}

@app.route("/")
def home():
    # Render the HTML chat interface
    return render_template("index.html")

@app.route("/api/messages", methods=["POST"])
def messages():
    if "application/json" in request.headers["Content-Type"]:
        body = request.json
    else:
        return Response(status=415)

    activity = Activity().deserialize(body)

    # Handle different activity types
    if activity.type == ActivityTypes.message:
        # Check if it's a user message
        if activity.from_property.id != "bot":
            response = handle_message(activity)
            return jsonify({"botResponse": response})  # Send JSON response

    return Response(status=200)

def sendMessage(user_message):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt="Your name is Lucy Parker, an AI scrum master with 10 years of experience. Your duty is to ask questions to the user to collect all the information for the sprint planning. User: " + user_message,
        max_tokens=50  # Adjust this based on your desired response length
    )

    bot_response = response.choices[0].text

    return bot_response  # Return the text response



def handle_message(activity):
    user_message = activity.text
    bot_response = sendMessage(user_message)

    return bot_response  # Return the bot's response

if __name__ == "__main__":
    app.debug = True  # Set debug mode before running the app
    app.run("localhost", 3978)
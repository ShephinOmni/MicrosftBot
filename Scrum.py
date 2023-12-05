# app.py (Flask Application)
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

# Additional routes and socket events for video chat, adding participants

if __name__ == '__main__':
    socketio.run(app, debug=True)

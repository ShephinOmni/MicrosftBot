document.addEventListener('DOMContentLoaded', function() {
    var videoElement = document.getElementById('userCamera');
    var cameraButton = document.getElementById('camera-toggle');
    var microphoneButton = document.getElementById('mic-toggle');
    var exitButton = document.getElementById('exit-button');
    var isMicActive = false;
    var stream = null;
    var microphoneStream = null;
    var mediaRecorder = null;
    var recognition; // Variable to hold the SpeechRecognition instance
    const socket = new WebSocket("ws:http://127.0.0.1:8000/ws/call"); // Initialize WebSocket

    // Access camera
    function accessCamera() {
        navigator.mediaDevices.getUserMedia({ video: true, audio: false })
            .then(newStream => {
                stream = newStream;
                videoElement.srcObject = stream;
                videoElement.onloadedmetadata = () => videoElement.play();
                updateCameraIcon(true);
            }).catch(error => {
                console.error("Error accessing the camera: ", error);
                alert("Error accessing the camera.");
            });
    }

    // Toggle camera
    function toggleCamera() {
        if (stream && stream.active) {
            stopMediaStream(stream);
            updateCameraIcon(false);
        } else {
            accessCamera();
        }
    }

    // Update camera icon
    function updateCameraIcon(isCameraOn) {
        const cameraIcon = cameraButton.querySelector('i');
        cameraIcon.classList.toggle('fa-video', isCameraOn);
        cameraIcon.classList.toggle('fa-video-slash', !isCameraOn);
    }

    // Initialize or toggle microphone
    async function toggleMicrophone() {
        const micIcon = microphoneButton.querySelector('i');
        if (!isMicActive) {
            try {
                microphoneStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                // Initialize Speech Recognition
                initializeSpeechRecognition();
            } catch (error) {
                console.error("Error accessing the microphone: ", error);
                alert("Error accessing the microphone.");
            }
        } else {
            stopMicrophone();
            micIcon.classList.replace('fa-microphone-slash', 'fa-microphone');
            if (recognition && typeof recognition.stop === 'function') {
                recognition.stop(); // Stop the speech recognition
            }
    }
}

    function initializeSpeechRecognition() {
        recognition = new SpeechRecognition();
        recognition.interimResults = true;
        recognition.continuous = true;
        recognition.onresult = event => {
            const transcript = event.results[event.results.length - 1][0].transcript;
            document.getElementById('speechOutput').innerText = transcript; // Display recognized text
            sendTextToServer(transcript); // Send transcript to server
        };
        recognition.start();
    }
    

    // Function to send the recognized text to the FastAPI server
   // Function to send the recognized text to the FastAPI server
    // Function to send the recognized text to the FastAPI server
    function sendTextToServer(text) {
        const serverUrl = 'http://127.0.0.1:8000/meeting/api/send_text'; // Corrected URL
        fetch(serverUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: text })
        })
        .then(response => response.json())
        .then(data => {
            console.log('ChatGPT Response:', data);
            playAudioResponse(data.audioUrl);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }


   // Stop microphone and media recorder
    function stopMicrophone() {
        if (mediaRecorder) {
            mediaRecorder.stop();
            mediaRecorder = null;  // Reset mediaRecorder to null
        }

        if (microphoneStream) {
            microphoneStream.getTracks().forEach(track => track.stop());
            microphoneStream = null;
        }

        isMicActive = false;
        updateMicrophoneIcon(); // Update the microphone icon (if you have a function for this)
    }



    socket.onmessage = function (event) {
        // Assuming event.data contains the audio file URL or binary data
        playAudioResponse(event.data);
    };
    
    function playAudioResponse(audioData) {
        let audio = new Audio(audioData);
        audio.play();
    }
    

    // Update microphone icon function (if not exists, create it)
    function updateMicrophoneIcon() {
        const micIcon = microphoneButton.querySelector('i');
        micIcon.classList.toggle('fa-microphone', !isMicActive);
        micIcon.classList.toggle('fa-microphone-slash', isMicActive);
    }


    // Stop media stream tracks
    function stopMediaStream(stream) {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    }

    // Event listeners
    cameraButton.addEventListener('click', toggleCamera);
    microphoneButton.addEventListener('click', toggleMicrophone);
    exitButton.addEventListener('click', () => {
        if (confirm("Are you sure you want to leave the meeting?")) {
            stopMediaStream(stream);
            window.location.href = '/';
        }
    });
});

function sendAudioData(audioBlob) {
    if (socket.readyState === WebSocket.OPEN) {
      // Send the audio blob to the scrum.py server
      socket.send(audioBlob);
    } else {
      console.error("WebSocket is not open.");
    }
  }

  // Handle audio data on stop
  async function handleAudioData() {
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    audioChunks = [];

    // Add functionality to send audio data and receive text response
    sendAudioData(audioBlob);

    // Receive text response from WebSocket
    socket.onmessage = function (event) {
      const textResponse = JSON.parse(event.data);
      // Process and display the text response (e.g., using a text box)
      console.log("Received text response:", textResponse);

      // Use the text response to generate another audio response 
      // (replace this with your desired functionality)
      const audioResponse = generateAudioResponse(textResponse);
      playAudioResponse(audioResponse);
    };
  }

  // Function to generate audio response based on text (replace this with your desired implementation)
  function generateAudioResponse(text) {
    // This is a placeholder for your actual implementation
    // You can use a text-to-speech API like Amazon Polly or Google Cloud Text-to-Speech
    const audioResponse = "Placeholder audio response";
    return audioResponse;
  }


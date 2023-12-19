document.addEventListener('DOMContentLoaded', function() {
  var videoElement = document.getElementById('videoElement');
  var cameraButton = document.getElementById('camera-btn');
  var microphoneButton = document.getElementById('microphone-btn');
  var cameraStream = null;
  var microphoneStream = null;

  async function toggleCamera() {
      try {
          if (cameraStream) {
              stopMediaStream(cameraStream);
              cameraButton.textContent = 'Turn Camera On';
          } else {
              cameraStream = await navigator.mediaDevices.getUserMedia({ video: true });
              videoElement.srcObject = cameraStream;
              videoElement.style.display = 'block';
              cameraButton.textContent = 'Turn Camera Off';
          }
      } catch (error) {
          console.error("Error accessing the camera: ", error);
          alert("Error accessing the camera.");
      }
  }

  async function toggleMicrophone() {
      try {
          if (microphoneStream) {
              stopMediaStream(microphoneStream);
              microphoneButton.textContent = 'Turn Microphone On';
          } else {
              microphoneStream = await navigator.mediaDevices.getUserMedia({ audio: true });
              microphoneButton.textContent = 'Turn Microphone Off';
              // Process the audio stream as needed
          }
      } catch (error) {
          console.error("Error accessing the microphone: ", error);
          alert("Error accessing the microphone.");
      }
  }

  function stopMediaStream(stream) {
      stream.getTracks().forEach(track => track.stop());
  }

  cameraButton.addEventListener('click', toggleCamera);
  microphoneButton.addEventListener('click', toggleMicrophone);

  document.getElementById('join-btn').addEventListener('click', function() {
      toggleCamera();  // Start the camera
      startChatSession();  // Initiate chat with ChatGPT
  });

  function startChatSession() {
      // Here you would implement the logic to start the chat session
      console.log("Starting chat session");
  }

  // Other existing code for dropdowns and window click events...
});

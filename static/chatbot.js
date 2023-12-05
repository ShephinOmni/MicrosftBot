document.addEventListener('DOMContentLoaded', function() {
  var videoElement = document.getElementById('videoElement');
  var avatarElement = document.getElementById('avatar');
  var cameraButton = document.getElementById('camera-btn');
  var stream = null; // This will hold the stream

  function toggleCamera() {
    if (stream) {
      // If the stream is already active, stop all tracks
      stream.getTracks().forEach(function(track) {
        track.stop();
      });
  
      // Ensure the camera light is turned off by removing the stream
      if (videoElement.srcObject) {
        videoElement.srcObject.getTracks().forEach(track => track.stop());
      }
  
      // Clear the video element source
      videoElement.srcObject = null;
      stream = null;
  
      // Update UI to reflect the camera is off
      videoElement.style.display = 'none'; // Hide the video element
      avatarElement.style.display = 'block'; // Show the avatar
      cameraButton.textContent = 'Turn Camera On'; // Update button text
    } else {
      // If the camera is not active, start the stream
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
          .then(function(newStream) {
            stream = newStream;
            videoElement.srcObject = stream;
  
            // Update UI to reflect the camera is on
            videoElement.style.display = 'block'; // Show the video element
            avatarElement.style.display = 'none'; // Hide the avatar
            cameraButton.textContent = 'Turn Camera Off'; // Update button text
  
            // Play the video once the metadata has loaded
            videoElement.onloadedmetadata = function() {
              videoElement.play().catch(function(error) {
                console.error("Error attempting to play video: ", error);
              });
            };
          }).catch(function(error) {
            console.error("Error accessing the camera: ", error);
            alert("Error accessing the camera.");
          });
      } else {
        alert("Your browser does not support media devices.");
      }
    }
  }
  
  // Event listener for camera button
  cameraButton.addEventListener('click', toggleCamera);

  // Dropdown toggle function
  function toggleDropdownMenu() {
    var dropdownMenu = this.nextElementSibling;
    dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
  }

  // Event listeners for dropdown-caret
  var dropdownCarets = document.querySelectorAll('.dropdown-caret');
  dropdownCarets.forEach(function(caret) {
    caret.addEventListener('click', function(event) {
      toggleDropdownMenu.call(this);
      event.stopPropagation();
    });
  });

  // Close the dropdown if the user clicks outside of it
  window.onclick = function(event) {
    var dropdownMenus = document.getElementsByClassName("dropdown-menu");
    for (var i = 0; i < dropdownMenus.length; i++) {
      var openDropdownMenu = dropdownMenus[i];
      if (openDropdownMenu.style.display === 'block') {
        openDropdownMenu.style.display = 'none';
      }
    }
  };
});

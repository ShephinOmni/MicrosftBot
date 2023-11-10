// DOM Elements
const inputField = document.getElementById("input-field");
const submitButton = document.getElementById("submit-button");
const chatBody = document.getElementById("conversation");

async function appendUserMessage(message) {
  if (message.trim() !== "") {
    const userDiv = document.createElement("div");
    userDiv.className = "user-message";
    const userText = document.createElement("p");
    userText.className = "user-text";
    userText.textContent = message;
    userDiv.appendChild(userText);
    chatBody.appendChild(userDiv);
  }
}

async function appendBotMessage(message) {
  const botDiv = document.createElement("div");
  botDiv.className = "bot-message";
  botDiv.textContent = message;
  chatBody.appendChild(botDiv);
}

function sendMessage(event) {
  event.preventDefault();

  const userMessage = document.getElementById('input-field').value;
  const userMessageContainer = document.querySelector('.user-message .user-text');
  userMessageContainer.textContent = userMessage;

  fetch('http://localhost:5000/api/get_response', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ user_input: userMessage })
})

  .then(response => response.json())
  .then(data => {
      const chatbotMessageContainer = document.querySelector('.chatbot-message .chatbot-text');
      chatbotMessageContainer.textContent = data.response;
  });

  // Clear the input field
  document.getElementById('input-field').value = '';
}

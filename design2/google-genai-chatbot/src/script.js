// This file contains the JavaScript code that integrates the Google GenAI API for the chatbot functionality.

const apiKey = 'YOUR_API_KEY'; // Replace with your actual API key
const chatButton = document.getElementById('chat-button');
const chatContainer = document.getElementById('chat-container');
const userInput = document.getElementById('user-input');

chatButton.addEventListener('click', async () => {
    const userMessage = userInput.value;
    if (userMessage.trim() === '') return;

    displayMessage('User', userMessage);
    userInput.value = '';

    const response = await getAIResponse(userMessage);
    displayMessage('AI', response);
});

async function getAIResponse(message) {
    const response = await fetch('https://api.google.com/genai/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({ prompt: message })
    });

    const data = await response.json();
    return data.response; // Adjust based on the actual response structure
}

function displayMessage(sender, message) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('chat-message');
    messageElement.innerText = `${sender}: ${message}`;
    chatContainer.appendChild(messageElement);
}
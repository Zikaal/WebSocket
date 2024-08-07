document.addEventListener('DOMContentLoaded', () => {
    const chatLog = document.getElementById('chat-log');
    const messageInput = document.getElementById('message-input');
    const connectBtn = document.getElementById('connect-btn');

    let websocket;

    // Function to display messages in the chat log
    function displayMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.textContent = message;
        chatLog.appendChild(messageElement);
        chatLog.scrollTop = chatLog.scrollHeight; // Scroll to the bottom
    }

    // Function to send a message
    function sendMessage() {
        if (websocket && websocket.readyState === WebSocket.OPEN) {
            const message = messageInput.value;
            const messageObject = { message: message }; // Обернем сообщение в объект JSON
            websocket.send(JSON.stringify(messageObject));
            displayMessage(`You: ${message}`);
            messageInput.value = '';
        }
    }

    // Event handler for receiving messages
    function onMessage(event) {
        displayMessage(`${event.data}`);
    }

    // Event handler for the connect button
    connectBtn.addEventListener('click', () => {
        const username = prompt('Enter your username:');
        if (username) {
            console.log('Attempting to connect...');
            websocket = new WebSocket('ws://localhost:8765');

            websocket.onopen = () => {
                console.log('Connected to the server.');
                websocket.send(JSON.stringify({ username: username }));
                displayMessage('Connected to the server.');

                // Assign message handler
                websocket.onmessage = (event) => {
                    console.log(`Received message: ${event.data}`);  // Debug output
                    onMessage(event);
                };
            };

            websocket.onerror = (error) => {
                console.error('WebSocket Error:', error);
                displayMessage(`Error: ${error.message}`);
            };

            websocket.onclose = () => {
                console.log('Disconnected from the server.');
                displayMessage('Disconnected from the server.');
            };
        }
    });

    // Event handler for sending messages when Enter is pressed
    messageInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            sendMessage();
        }
    });
});

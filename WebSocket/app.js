document.addEventListener('DOMContentLoaded', () => {
    const chatLog = document.getElementById('chat-log');
    const messageInput = document.getElementById('message-input');
    const connectBtn = document.getElementById('connect-btn');

    let websocket;

    function displayMessage(message, isUser = false) {
        const messageElement = document.createElement('div');
        messageElement.textContent = message;
        messageElement.classList.add('message');
        
        if (isUser) {
            messageElement.classList.add('user-message');
        } else {
            messageElement.classList.add('server-message');
        }
    
        chatLog.appendChild(messageElement);
        chatLog.scrollTop = chatLog.scrollHeight; // Прокрутка вниз, чтобы показать последнее сообщение
    }
    
    function sendMessage() {
        if (websocket && websocket.readyState === WebSocket.OPEN) {
            const message = messageInput.value;
            const messageObject = { message: message }; 
            websocket.send(JSON.stringify(messageObject));
            displayMessage(`You: ${message}`, true); // Используем true для сообщений пользователя
            messageInput.value = '';
        }
    }
    
    function onMessage(event) {
        displayMessage(`${event.data}`); // Сообщения с сервера
    }
    

    connectBtn.addEventListener('click', () => {
        const username = prompt('Enter your username:');
        const password = prompt('Enter your password:');
        if (username && password) {
            console.log('Attempting to connect...');
            websocket = new WebSocket('ws://localhost:8765');

            websocket.onopen = () => {
                console.log('Connected to the server.');
                websocket.send(JSON.stringify({ username: username, password: password }));
                displayMessage('Connected to the server.');

                websocket.onmessage = (event) => {
                    console.log(`Received message: ${event.data}`);
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

    messageInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            sendMessage();
        }
    });
});

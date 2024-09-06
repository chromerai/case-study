let socket;
let isConnected = false;
let messageQueue = [];
let currentResolver = null;

const initializeSocket = () => {
  if (!socket) {
    socket = new WebSocket('ws://localhost:8000/ws');

    socket.onopen = () => {
      console.log('Connected to server');
      isConnected = true;
      processQueue();
    };

    socket.onclose = () => {
      console.log('Disconnected from server');
      isConnected = false;
    };

    socket.onmessage = (event) => {
      const parsedData = JSON.parse(event.data);
      console.log('Message received:', parsedData);
      if (currentResolver) {
        currentResolver(parsedData);
        currentResolver = null;
      }
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }
};

const processQueue = () => {
  while (messageQueue.length > 0 && isConnected) {
    const { message, resolve } = messageQueue.shift();
    sendMessageToServer(message, resolve);
  }
};

const sendMessageToServer = (message, resolve) => {
  currentResolver = resolve;
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({
      event: 'message',
      data: message
    }));
  } else {
    console.error('WebSocket is not open. Message not sent.');
    if (resolve) resolve({ error: 'WebSocket is not open' });
  }
};

export const getAIMessage = async (userQuery, onIntermediateResponse) => {
  return new Promise((resolve) => {
    const handleMessage = (message) => {
      if (message.type === 'intermediate') {
        console.log('Intermediate response:', message.message);
        onIntermediateResponse({
          role: "assistant",
          content: message.message
        });
        // Handle intermediate response if needed
      } else if (message.type === 'final') {
        console.log('Final response:', message.message);
        resolve({
          role: "assistant",
          content: message.message
        });
      }
    };

    if (!isConnected) {
      messageQueue.push({ message: userQuery, resolve: handleMessage });
      initializeSocket();
    } else {
      sendMessageToServer(userQuery, handleMessage);
    }
  });
};
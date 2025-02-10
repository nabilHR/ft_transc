console.log("JavaScript file loaded successfully!");
const socket = new WebSocket(`ws://localhost:6000/ws/status/`); // Or wss:// for secure connections

socket.onopen = () => {
    console.log("WebSocket connection opened");
};

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("User status update:", data);
    // Update UI (e.g., display user's online status)
};

socket.onclose = () => {
    console.log("WebSocket connection closed");
};
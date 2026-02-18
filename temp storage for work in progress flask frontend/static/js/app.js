document.addEventListener("DOMContentLoaded", () => {

    // ============================
    // DOM ELEMENT REFERENCES
    // ============================

    const chatWindow = document.getElementById("chat-window");
    const chatInput = document.getElementById("chat-input");
    const sendBtn = document.getElementById("send-btn");

    const fileUpload = document.getElementById("file-upload");

    const urlInput = document.getElementById("url-input");
    const urlAddBtn = document.getElementById("url-add-btn");

    const recordBtn = document.getElementById("record-btn");
    const voiceSelect = document.getElementById("voice-select");
    const playBtn = document.getElementById("play-btn");
    const autoTTS = document.getElementById("auto-tts");

    const exportPdfBtn = document.getElementById("export-pdf-btn");
    const printBtn = document.getElementById("print-btn");


    // ============================
    // EVENT HANDLER STUBS
    // ============================

    sendBtn.addEventListener("click", () => {
        // TODO: handle sending chat message
        console.log("Send clicked");
    });

    chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            // TODO: handle Enter key send
            console.log("Enter pressed");
            console.log("ENTER KEY HANDLER FIRED");
        }
    });

    fileUpload.addEventListener("change", () => {
        // TODO: handle file selection
        console.log("Files selected:", fileUpload.files);
    });

    urlAddBtn.addEventListener("click", () => {
        // TODO: handle URL submission
        console.log("URL added:", urlInput.value);
    });

    recordBtn.addEventListener("mousedown", () => {
        // TODO: start recording
        console.log("Recording started");
    });

    recordBtn.addEventListener("mouseup", () => {
        // TODO: stop recording
        console.log("Recording stopped");
    });

    playBtn.addEventListener("click", () => {
        // TODO: play TTS audio
        console.log("Play TTS");
    });

    autoTTS.addEventListener("change", () => {
        // TODO: toggle auto TTS
        console.log("Auto TTS:", autoTTS.checked);
    });

    exportPdfBtn.addEventListener("click", () => {
        // TODO: export PDF
        console.log("Export PDF clicked");
    });

    printBtn.addEventListener("click", () => {
        // TODO: print page
        console.log("Print clicked");
    });


    // ============================
    // BASIC DOM HELPER (OPTIONAL)
    // ============================

    function appendMessage(role, text) {
        // TODO: render chat messages
        const msg = document.createElement("div");
        msg.className = `msg msg-${role}`;
        msg.textContent = text;
        chatWindow.appendChild(msg);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

});

const socket = io();

// Socket listeners: render incoming user and bot messages
socket.on("user-message", (data) => {
    console.log("USER-MESSAGE LISTENER FIRED:", data);
    const chat = document.getElementById("chat-container");
    const bubble = document.createElement("div");
    bubble.className = "chat-bubble user-bubble";
    bubble.textContent = data && data.message ? data.message : String(data);
    console.log("Prepared user bubble:", bubble, "target chat elem:", chat);
    if (chat) {
        chat.appendChild(bubble);
        chat.scrollTop = chat.scrollHeight;
        console.log("Appended user bubble. chat children:", chat.children.length);
    } else {
        console.warn("user-message received but no #chat-container found to append to");
    }
});

socket.on("bot-response", (data) => {
    console.log("BOT-RESPONSE LISTENER FIRED:", data);
    const chat = document.getElementById("chat-container");
    const bubble = document.createElement("div");
    bubble.className = "chat-bubble bot-bubble";
    bubble.textContent = data && data.message ? data.message : String(data);
    console.log("Prepared bot bubble:", bubble, "target chat elem:", chat);
    if (chat) {
        chat.appendChild(bubble);
        chat.scrollTop = chat.scrollHeight;
        console.log("Appended bot bubble. chat children:", chat.children.length);
    } else {
        console.warn("bot-response received but no #chat-container found to append to");
    }
});

// DOM references
const inputBox = document.getElementById("chat-input");
const sendButton = document.getElementById("send-btn");

// Unified send handler
function sendMessage() {
    const message = inputBox.value.trim();
    if (!message) return;

    const payload = {
        session_id: sessionId,
        user_id: username,
        username: username,
        message: message,
        timestamp: Date.now(),
        metadata: {
            source: "frontend",
            client_type: "web"
        }
    };

    socket.emit("send-message", payload);
    socket.emit("user-message", payload);  // frontend echo to trigger the user-message listener
}

// Mouse click
sendButton.addEventListener("click", sendMessage);

// Enter key
inputBox.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        e.preventDefault();
        sendMessage();
    }
});

// Debug: verify chat-container is found and visible
try {
    const test = document.getElementById("chat-container");
    if (test) {
        const dbg = document.createElement("div");
        dbg.className = "chat-bubble user-bubble";
        dbg.textContent = "DEBUG: chat-container is visible";
        test.appendChild(dbg);
        console.log("DEBUG: appended debug bubble to #chat-container");
    } else {
        console.warn("DEBUG: #chat-container not found");
    }
} catch (err) {
    console.error("DEBUG: error while appending debug bubble", err);
}
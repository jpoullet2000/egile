class GrokChatbot {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.messageQueue = [];
        this.init();
    }

    init() {
        this.connectToServer();
        this.setupEventListeners();
        this.setupTextareaAutoResize();
    }

    connectToServer() {
        try {
            // Connect to the WebSocket bridge (Smart Agent)
            this.ws = new WebSocket('ws://localhost:8770');
            
            this.ws.onopen = () => {
                this.isConnected = true;
                this.updateConnectionStatus(true);
                // Wait for server confirmation before showing connection message
                
                // Process any queued messages
                while (this.messageQueue.length > 0) {
                    const message = this.messageQueue.shift();
                    this.ws.send(JSON.stringify(message));
                }
            };

            this.ws.onmessage = (event) => {
                const response = JSON.parse(event.data);
                this.handleServerResponse(response);
            };

            this.ws.onclose = () => {
                this.isConnected = false;
                this.updateConnectionStatus(false);
                this.addMessage('system', '⚠️ Connection lost. Attempting to reconnect...');
                
                // Attempt to reconnect after 3 seconds
                setTimeout(() => this.connectToServer(), 3000);
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.addMessage('system', '❌ Connection error. Please ensure the Grok agent server is running.');
            };

        } catch (error) {
            console.error('Failed to connect:', error);
            this.updateConnectionStatus(false);
        }
    }

    setupEventListeners() {
        const messageInput = document.getElementById('messageInput');
        
        // Focus input on load
        messageInput.focus();
    }

    setupTextareaAutoResize() {
        const textarea = document.getElementById('messageInput');
        
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
    }

    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connectionStatus');
        if (connected) {
            statusElement.textContent = '🚀 Connected to Grok AI Agent';
            statusElement.className = 'connection-status';
        } else {
            statusElement.textContent = '❌ Disconnected from Grok AI Agent';
            statusElement.className = 'connection-status disconnected';
        }
    }

    sendMessage(text) {
        const messageInput = document.getElementById('messageInput');
        const message = text || messageInput.value.trim();
        
        if (!message) return;

        // Clear input and reset height
        messageInput.value = '';
        messageInput.style.height = 'auto';
        
        // Add user message to chat
        this.addMessage('user', message);
        
        // Show typing indicator
        this.showTypingIndicator();

        // Send to server
        const payload = {
            type: 'chat_message',
            message: message,
            timestamp: Date.now()
        };

        if (this.isConnected) {
            this.ws.send(JSON.stringify(payload));
        } else {
            this.messageQueue.push(payload);
            this.addMessage('system', '📤 Message queued. Will send when reconnected.');
        }
    }

    handleServerResponse(response) {
        this.hideTypingIndicator();

        if (response.type === 'connection_confirmed') {
            this.addMessage('system', '🤖 Connected to Grok AI! Ready to assist you.');
        } else if (response.type === 'processing') {
            this.showTypingIndicator();
        } else if (response.type === 'chat_response') {
            this.addMessage('bot', response.message);
        } else if (response.type === 'error') {
            this.addMessage('system', `❌ Error: ${response.message}`);
        } else {
            // Handle other response types (from the Grok agent)
            this.addMessage('bot', response.message || 'I received your message but couldn\'t generate a proper response.');
        }
    }

    addMessage(type, content) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Enhanced content formatting
        const formattedContent = this.formatContent(content);
        contentDiv.innerHTML = formattedContent;
        
        messageDiv.appendChild(contentDiv);
        messagesContainer.appendChild(messageDiv);
        
        // Smooth scroll to bottom
        this.scrollToBottom();
    }

    formatContent(content) {
        // Enhanced formatting for better readability
        return content
            // Bold text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Italic text
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            // Code blocks
            .replace(/`(.*?)`/g, '<code style="background: #f1f3f4; padding: 2px 6px; border-radius: 4px; font-family: monospace;">$1</code>')
            // Line breaks
            .replace(/\n/g, '<br>')
            // Bullet points (enhanced)
            .replace(/^• /gm, '• ')
            // Numbers with periods
            .replace(/^(\d+)\. /gm, '<strong>$1.</strong> ');
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chatMessages');
        messagesContainer.scrollTo({
            top: messagesContainer.scrollHeight,
            behavior: 'smooth'
        });
    }

    showTypingIndicator() {
        document.getElementById('typingIndicator').style.display = 'flex';
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        document.getElementById('typingIndicator').style.display = 'none';
    }
}

// Global functions for HTML event handlers
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function sendMessage(text) {
    chatbot.sendMessage(text);
}

function sendQuickMessage(message) {
    const messageInput = document.getElementById('messageInput');
    messageInput.value = message;
    sendMessage();
}

// Initialize chatbot when page loads
let chatbot;
window.addEventListener('load', () => {
    chatbot = new GrokChatbot();
});
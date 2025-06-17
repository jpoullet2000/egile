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
        // Try multiple ports for Smart Agent bridge
        const ports = [8770, 8769, 8771, 8772];
        this.tryConnectToPorts(ports, 0);
    }

    tryConnectToPorts(ports, index) {
        if (index >= ports.length) {
            this.addMessage('system', '❌ Could not connect to Smart Agent on any available port.');
            return;
        }

        const port = ports[index];
        try {
            // Connect to the WebSocket bridge (Smart Agent)
            this.ws = new WebSocket(`ws://localhost:${port}`);
            
            this.ws.onopen = () => {
                this.isConnected = true;
                this.updateConnectionStatus(true);
                console.log(`✅ Connected to Smart Agent on port ${port}`);
                
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
                
                // Try next port
                if (index < ports.length - 1) {
                    console.log(`Port ${port} closed, trying next port...`);
                    setTimeout(() => this.tryConnectToPorts(ports, index + 1), 1000);
                } else {
                    this.addMessage('system', '⚠️ Connection lost. Attempting to reconnect...');
                    setTimeout(() => this.connectToServer(), 3000);
                }
            };

            this.ws.onerror = (error) => {
                console.error(`WebSocket error on port ${port}:`, error);
                // Try next port
                if (index < ports.length - 1) {
                    setTimeout(() => this.tryConnectToPorts(ports, index + 1), 500);
                } else {
                    this.addMessage('system', '❌ Connection error. Please ensure the Smart Agent server is running.');
                }
            };

        } catch (error) {
            console.error(`Failed to connect to port ${port}:`, error);
            if (index < ports.length - 1) {
                this.tryConnectToPorts(ports, index + 1);
            }
        }
    }

    setupEventListeners() {
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');

        // Send message on button click
        sendButton.addEventListener('click', () => {
            console.log('📤 Send button clicked');
            const message = messageInput.value.trim();
            if (message) {
                console.log('📤 Sending message:', message);
                this.sendMessage(message);
                messageInput.value = '';
            } else {
                console.log('⚠️ No message to send');
            }
        });

        // Send message on Enter key (but allow Shift+Enter for new lines)
        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const message = messageInput.value.trim();
                if (message) {
                    this.sendMessage(message);
                    messageInput.value = '';
                }
            }
        });

        // Handle quick buttons
        const quickButtons = document.querySelectorAll('.quick-button');
        console.log(`🔘 Found ${quickButtons.length} quick buttons`);
        quickButtons.forEach((button, index) => {
            button.addEventListener('click', () => {
                console.log(`🔘 Quick button ${index} clicked`);
                const message = button.getAttribute('data-message');
                if (message) {
                    console.log('📤 Sending quick message:', message);
                    this.sendMessage(message);
                } else {
                    console.log('⚠️ No data-message found on button');
                }
            });
        });
    }

    setupTextareaAutoResize() {
        const messageInput = document.getElementById('messageInput');
        messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
    }

    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connectionStatus');
        
        if (connected) {
            statusElement.className = 'connection-status connected';
            statusElement.textContent = 'Connected to Smart Agent';
        } else {
            statusElement.className = 'connection-status disconnected';
            statusElement.textContent = 'Disconnected';
        }
    }

    sendMessage(text) {
        if (!this.isConnected) {
            this.messageQueue.push({message: text});
            this.addMessage('system', '⏳ Message queued. Connecting to Smart Agent...');
            return;
        }

        // Add user message to chat
        this.addMessage('user', text);
        
        // Show typing indicator
        this.showTypingIndicator();

        // Send to server
        const message = {
            message: text,
            timestamp: Date.now()
        };

        try {
            this.ws.send(JSON.stringify(message));
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.addMessage('system', '❌ Failed to send message. Please try again.');
        }
    }

    handleServerResponse(response) {
        this.hideTypingIndicator();
        
        switch (response.type) {
            case 'system':
                this.addMessage('system', response.message);
                break;
            case 'agent':
                this.addMessage('ai', response.message);
                break;
            case 'error':
                this.addMessage('system', `❌ ${response.message}`);
                break;
            case 'typing':
                // Handle typing indicator if needed
                break;
            default:
                this.addMessage('ai', response.message || JSON.stringify(response));
        }
    }

    addMessage(type, content) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = type === 'user' ? '👤' : type === 'ai' ? '🧠' : 'ℹ️';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'content';
        contentDiv.innerHTML = this.formatContent(content);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);
        messagesContainer.appendChild(messageDiv);
        
        this.scrollToBottom();
    }

    formatContent(content) {
        // Basic markdown-like formatting
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chatMessages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    showTypingIndicator() {
        const existingIndicator = document.querySelector('.ai-thinking');
        if (!existingIndicator) {
            this.addMessage('system', '<div class="ai-thinking">Smart Agent is thinking...</div>');
        }
    }

    hideTypingIndicator() {
        const indicators = document.querySelectorAll('.ai-thinking');
        indicators.forEach(indicator => {
            const messageDiv = indicator.closest('.message');
            if (messageDiv) {
                messageDiv.remove();
            }
        });
    }
}

// Initialize the chatbot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Initializing Smart Chatbot...');
    window.chatbot = new GrokChatbot();
    
    // Show initial welcome message after a short delay
    setTimeout(() => {
        console.log('📝 Adding welcome message...');
        window.chatbot.addMessage('system', 'Welcome to the Smart E-commerce Agent! 🧠');
    }, 500);
    
    // Add some debugging
    console.log('✅ Chatbot initialized and available as window.chatbot');
});

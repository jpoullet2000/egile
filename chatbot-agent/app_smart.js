class GrokChatbot {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.messageQueue = [];
        this.connectionAttempts = 0;
        this.maxConnectionAttempts = 3;
        this.isConnecting = false;
        this.pingInterval = null;
        this.init();
    }

    init() {
        // Only initialize once
        if (this.initialized) {
            console.log('⚠️ Chatbot already initialized, skipping...');
            return;
        }
        this.initialized = true;
        
        this.connectToServer();
        this.setupEventListeners();
        this.setupTextareaAutoResize();
    }

    connectToServer() {
        // Prevent multiple simultaneous connection attempts
        if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.CONNECTING)) {
            console.log('⚠️ Connection attempt already in progress...');
            return;
        }
        
        this.isConnecting = true;
        
        // Close any existing connection first
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        
        // Try connecting to possible Smart Agent bridge ports
        const possiblePorts = [8770, 8771, 8772, 8773, 8774];
        this.tryConnectToPorts(possiblePorts, 0);
    }

    tryConnectToPorts(ports, index) {
        if (index >= ports.length) {
            console.error('❌ Failed to connect to Smart Agent on any port');
            this.isConnecting = false;
            this.updateConnectionStatus(false);
            this.addMessage('system', '❌ Could not connect to Smart Agent on any port. Please ensure the server is running.');
            return;
        }
        
        const port = ports[index];
        console.log(`Trying to connect to port ${port}...`);
        this.connectToPort(port, () => {
            // On failure, try next port after a short delay
            console.log(`Port ${port} failed, trying next port...`);
            setTimeout(() => {
                this.tryConnectToPorts(ports, index + 1);
            }, 1000);
        });
    }

    connectToPort(port, onFailure = null) {
        try {
            console.log(`Attempting to connect to Smart Agent on port ${port}...`);
            this.ws = new WebSocket(`ws://localhost:${port}`);
            
            let connectionSuccessful = false;
            
            this.ws.onopen = () => {
                connectionSuccessful = true;
                this.isConnected = true;
                this.isConnecting = false;
                this.connectionAttempts = 0;
                this.updateConnectionStatus(true);
                console.log(`✅ Connected to Smart Agent on port ${port}`);
                
                // Send a ping to keep connection alive
                this.startPingInterval();
                
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

            this.ws.onclose = (event) => {
                this.isConnected = false;
                this.isConnecting = false;
                this.updateConnectionStatus(false);
                this.stopPingInterval();
                console.log(`Connection closed on port ${port}. Code: ${event.code}, Reason: ${event.reason}`);
                
                // If connection was never successful and we have a failure callback, use it
                if (!connectionSuccessful && onFailure) {
                    onFailure();
                    return;
                }
                
                // Only attempt reconnection if it wasn't a manual close and we haven't exceeded max attempts
                if (event.code !== 1000 && event.code !== 1001 && this.connectionAttempts < this.maxConnectionAttempts) {
                    this.connectionAttempts++;
                    console.log(`Connection lost. Attempting to reconnect (${this.connectionAttempts}/${this.maxConnectionAttempts})...`);
                    this.addMessage('system', `⚠️ Connection lost. Reconnecting... (${this.connectionAttempts}/${this.maxConnectionAttempts})`);
                    setTimeout(() => this.connectToServer(), 3000);
                } else if (this.connectionAttempts >= this.maxConnectionAttempts) {
                    this.addMessage('system', '❌ Could not connect to Smart Agent after multiple attempts. Please refresh the page.');
                }
            };

            this.ws.onerror = (error) => {
                console.error(`WebSocket error on port ${port}:`, error);
                this.isConnecting = false;
                
                // If we have a failure callback for port discovery, use it
                if (onFailure && !connectionSuccessful) {
                    onFailure();
                    return;
                }
                
                // Otherwise use the normal retry logic
                if (this.connectionAttempts < this.maxConnectionAttempts) {
                    this.connectionAttempts++;
                    console.log(`Connection error. Retrying (${this.connectionAttempts}/${this.maxConnectionAttempts})...`);
                    setTimeout(() => this.connectToServer(), 2000);
                } else {
                    this.addMessage('system', '❌ Connection error. Please ensure the Smart Agent server is running and refresh the page.');
                }
            };

        } catch (error) {
            console.error(`Failed to connect to port ${port}:`, error);
            this.isConnecting = false;
            if (onFailure) {
                onFailure();
            } else {
                this.addMessage('system', '❌ Failed to establish connection. Please refresh the page.');
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

    startPingInterval() {
        // Send ping every 30 seconds to keep connection alive
        this.pingInterval = setInterval(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                try {
                    this.ws.send(JSON.stringify({ type: 'ping' }));
                } catch (error) {
                    console.error('Error sending ping:', error);
                    this.stopPingInterval();
                }
            } else {
                this.stopPingInterval();
            }
        }, 30000);
    }

    stopPingInterval() {
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
            this.pingInterval = null;
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
    
    // Prevent multiple instances
    if (window.chatbot) {
        console.log('⚠️ Chatbot already exists, skipping initialization');
        return;
    }
    
    window.chatbot = new GrokChatbot();
    
    // Show initial welcome message after a short delay
    setTimeout(() => {
        console.log('📝 Adding welcome message...');
        if (window.chatbot) {
            window.chatbot.addMessage('system', 'Welcome to the Smart E-commerce Agent! 🧠');
        }
    }, 500);
    
    // Add some debugging
    console.log('✅ Chatbot initialized and available as window.chatbot');
});

// Handle page unload to clean up connections
window.addEventListener('beforeunload', () => {
    if (window.chatbot && window.chatbot.ws) {
        console.log('🔌 Closing WebSocket connection before page unload');
        window.chatbot.ws.close(1000, 'Page unloading');
    }
});

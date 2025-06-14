class EcommerceChatbot {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.messageQueue = [];
        this.init();
    }

    init() {
        this.connectToServer();
        this.setupEventListeners();
    }

    connectToServer() {
        try {
            // Connect to the WebSocket bridge
            this.ws = new WebSocket('ws://localhost:8765');
            
            this.ws.onopen = () => {
                this.isConnected = true;
                this.updateConnectionStatus(true);
                this.addMessage('system', 'Connected to MCP server successfully!');
                
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
                this.addMessage('system', 'Connection lost. Attempting to reconnect...');
                
                // Attempt to reconnect after 3 seconds
                setTimeout(() => this.connectToServer(), 3000);
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.addMessage('system', 'Connection error. Please make sure the MCP server is running.');
            };

        } catch (error) {
            console.error('Failed to connect:', error);
            this.updateConnectionStatus(false);
        }
    }

    setupEventListeners() {
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');

        // Focus input on load
        messageInput.focus();
    }

    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connectionStatus');
        if (connected) {
            statusElement.textContent = 'Connected to MCP server';
            statusElement.className = 'connection-status';
        } else {
            statusElement.textContent = 'Disconnected from MCP server';
            statusElement.className = 'connection-status disconnected';
        }
    }

    sendMessage(text) {
        const messageInput = document.getElementById('messageInput');
        const message = text || messageInput.value.trim();
        
        if (!message) return;

        // Clear input
        messageInput.value = '';
        
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
            this.addMessage('system', 'Message queued. Will send when reconnected.');
        }
    }

    handleServerResponse(response) {
        this.hideTypingIndicator();

        if (response.type === 'chat_response') {
            this.addMessage('bot', response.message);
        } else if (response.type === 'error') {
            this.addMessage('system', `Error: ${response.message}`);
        } else if (response.type === 'tool_result') {
            this.handleToolResult(response);
        }
    }

    handleToolResult(response) {
        const { tool, result, success } = response;
        
        if (success) {
            let message = '';
            
            switch (tool) {
                case 'list_products':
                case 'search_products':
                    message = this.formatProductList(result);
                    break;
                case 'get_product':
                    message = this.formatProduct(result);
                    break;
                case 'create_product':
                    message = `✅ Product created successfully!\n\n${this.formatProduct(result)}`;
                    break;
                case 'list_customers':
                    message = this.formatCustomerList(result);
                    break;
                case 'get_customer':
                    message = this.formatCustomer(result);
                    break;
                case 'create_customer':
                    message = `✅ Customer created successfully!\n\n${this.formatCustomer(result)}`;
                    break;
                case 'list_orders':
                    message = this.formatOrderList(result);
                    break;
                case 'get_order':
                case 'create_order':
                    message = this.formatOrder(result);
                    break;
                case 'get_low_stock_products':
                    message = this.formatLowStockProducts(result);
                    break;
                case 'update_stock':
                    message = `✅ Stock updated successfully!\n\nProduct: ${result.name}\nNew Stock: ${result.stock_quantity}`;
                    break;
                default:
                    message = JSON.stringify(result, null, 2);
            }
            
            this.addMessage('bot', message);
        } else {
            this.addMessage('system', `Tool error: ${result}`);
        }
    }

    formatProductList(products) {
        if (!products || products.length === 0) {
            return "No products found.";
        }

        let message = `📦 Found ${products.length} product(s):\n\n`;
        products.forEach(product => {
            message += `• **${product.name}** (${product.sku})\n`;
            message += `  💰 $${product.price} | 📦 Stock: ${product.stock_quantity}\n`;
            message += `  📂 ${product.category}\n\n`;
        });
        
        return message;
    }

    formatProduct(product) {
        return `📦 **${product.name}**\n` +
               `ID: ${product.id}\n` +
               `SKU: ${product.sku}\n` +
               `Price: $${product.price}\n` +
               `Category: ${product.category}\n` +
               `Stock: ${product.stock_quantity}\n` +
               `Description: ${product.description || 'N/A'}`;
    }

    formatCustomerList(customers) {
        if (!customers || customers.length === 0) {
            return "No customers found.";
        }

        let message = `👥 Found ${customers.length} customer(s):\n\n`;
        customers.forEach(customer => {
            message += `• **${customer.first_name} ${customer.last_name}**\n`;
            message += `  📧 ${customer.email}\n`;
            if (customer.phone) message += `  📞 ${customer.phone}\n`;
            message += `  🆔 ${customer.id}\n\n`;
        });
        
        return message;
    }

    formatCustomer(customer) {
        let message = `👤 **${customer.first_name} ${customer.last_name}**\n` +
                     `ID: ${customer.id}\n` +
                     `Email: ${customer.email}\n`;
        
        if (customer.phone) message += `Phone: ${customer.phone}\n`;
        if (customer.address) {
            message += `Address: ${customer.address.street}, ${customer.address.city}, ${customer.address.state} ${customer.address.zip}\n`;
        }
        
        return message;
    }

    formatOrderList(orders) {
        if (!orders || orders.length === 0) {
            return "No orders found.";
        }

        let message = `📋 Found ${orders.length} order(s):\n\n`;
        orders.forEach(order => {
            message += `• **Order ${order.id}**\n`;
            message += `  👤 Customer: ${order.customer_id}\n`;
            message += `  💰 Total: $${order.total_amount}\n`;
            message += `  📊 Status: ${order.status}\n`;
            message += `  📅 ${new Date(order.created_at).toLocaleDateString()}\n\n`;
        });
        
        return message;
    }

    formatOrder(order) {
        let message = `📋 **Order ${order.id}**\n` +
                     `Customer: ${order.customer_id}\n` +
                     `Status: ${order.status}\n` +
                     `Total: $${order.total_amount}\n` +
                     `Created: ${new Date(order.created_at).toLocaleDateString()}\n\n` +
                     `Items:\n`;
        
        order.items.forEach(item => {
            message += `• ${item.quantity}x Product ${item.product_id} - $${item.total_price}\n`;
        });
        
        return message;
    }

    formatLowStockProducts(products) {
        if (!products || products.length === 0) {
            return "🎉 No products with low stock!";
        }

        let message = `⚠️ ${products.length} product(s) with low stock:\n\n`;
        products.forEach(product => {
            message += `• **${product.name}** (${product.sku})\n`;
            message += `  📦 Only ${product.stock_quantity} left!\n`;
            message += `  💰 $${product.price}\n\n`;
        });
        
        return message;
    }

    addMessage(type, content) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Format content with basic markdown-like styling
        const formattedContent = content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');
        
        contentDiv.innerHTML = formattedContent;
        messageDiv.appendChild(contentDiv);
        messagesContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    showTypingIndicator() {
        document.getElementById('typingIndicator').style.display = 'flex';
        const messagesContainer = document.getElementById('chatMessages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    hideTypingIndicator() {
        document.getElementById('typingIndicator').style.display = 'none';
    }
}

// Global functions for HTML event handlers
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

function sendMessage(text) {
    chatbot.sendMessage(text);
}

function sendQuickMessage(message) {
    document.getElementById('messageInput').value = message;
    sendMessage();
}

// Initialize chatbot when page loads
let chatbot;
window.addEventListener('load', () => {
    chatbot = new EcommerceChatbot();
});
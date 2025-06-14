# Egile E-commerce Chatbot

A modern web-based chatbot interface for the Egile E-commerce MCP Server.

## 🚀 Quick Start

From the project root directory:

```bash
# Start the chatbot
python run_chatbot.py
```

This will:
1. Start the WebSocket bridge server
2. Open the chatbot interface in your browser automatically
3. Connect to the MCP server

## 📁 Directory Structure

```
chatbot/
├── index.html      # Main chatbot web interface
├── app.js          # Frontend JavaScript application
├── bridge.py       # WebSocket bridge server
└── README.md       # This file
```

## 🔧 Manual Setup

If you prefer to start components manually:

### 1. Start the Bridge Server
```bash
cd chatbot
python bridge.py
```

### 2. Open the Chatbot
Open `chatbot/index.html` in your browser, or serve it with a local web server:

```bash
# Using Python's built-in server
cd chatbot
python -m http.server 8080
# Then open http://localhost:8080
```

## 💬 Usage

### Natural Language Commands
The chatbot understands natural language. Try:
- "Show me all products"
- "Create a new customer"
- "What products are low in stock?"

### Specific Commands
For precise control, use these formats:

**Products:**
- `list products` - Show all products
- `create product "Wireless Mouse" 29.99 MOUSE-001 Electronics 25` - Create product
- `get product MOUSE-001` - Get product details
- `search products wireless` - Search products

**Customers:**
- `list customers` - Show all customers
- `create customer john@example.com "John" "Doe" "+1-555-0123"` - Create customer
- `get customer john@example.com` - Get customer details

**Orders:**
- `list orders` - Show all orders
- `create order cust_000001 prod_000001 2` - Create order
- `get order order_000001` - Get order details

**Inventory:**
- `stock low` - Show products with low stock (default threshold: 10)
- `stock low 5` - Show products with stock below 5
- `stock update prod_000001 50` - Update product stock

### Quick Actions
Use the predefined buttons for common tasks:
- **List Products** - View all products
- **List Customers** - View all customers  
- **List Orders** - View all orders
- **Low Stock** - Check inventory
- **Help** - Show all commands

## 🌟 Features

- **Real-time Communication**: WebSocket-based for instant responses
- **Auto-reconnection**: Handles connection drops gracefully
- **Rich Formatting**: Products, orders, and customers display beautifully
- **Responsive Design**: Works on desktop and mobile
- **Natural Language**: Type commands naturally
- **Quick Actions**: Pre-built buttons for common tasks
- **Typing Indicators**: Visual feedback during processing

## 🔧 Technical Details

### WebSocket Bridge
The `bridge.py` server acts as a middleware between the web frontend and the MCP server:
- Listens on `ws://localhost:8765`
- Parses natural language commands
- Converts to MCP tool calls
- Returns formatted responses

### Frontend Application
The `app.js` handles:
- WebSocket communication
- Message formatting and display
- Auto-reconnection logic
- UI interactions

### Web Interface
The `index.html` provides:
- Modern chat UI with gradients
- Responsive design
- Quick action buttons
- Connection status indicators

## 🛠️ Customization

### Styling
Edit the CSS in `index.html` to customize:
- Colors and gradients
- Typography
- Layout and spacing
- Animations

### Commands
Modify the `parse_user_intent()` method in `bridge.py` to:
- Add new command patterns
- Change command syntax
- Add custom responses

### UI Features
Update `app.js` to:
- Add new quick action buttons
- Modify message formatting
- Change connection behavior

## 🐛 Troubleshooting

### Connection Issues
- Ensure the bridge server is running on port 8765
- Check that the MCP server dependencies are installed
- Verify no firewall is blocking WebSocket connections

### Display Issues  
- Try refreshing the browser
- Check browser console for JavaScript errors
- Ensure modern browser with WebSocket support

### Performance
- The chatbot handles multiple concurrent connections
- Messages are processed asynchronously
- Auto-reconnection prevents data loss

## 📝 Development

To extend the chatbot:

1. **Add new commands**: Modify `parse_user_intent()` in `bridge.py`
2. **Update UI**: Edit `index.html` for layout changes
3. **Add features**: Extend `app.js` for new functionality
4. **Style changes**: Update CSS in `index.html`

## 🔗 Integration

The chatbot integrates seamlessly with:
- Egile MCP Server
- All existing e-commerce tools
- Database operations
- CLI functionality

Start chatting and managing your e-commerce data through a beautiful web interface!
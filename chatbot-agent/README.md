# Grok AI E-commerce Chatbot

An intelligent, conversational chatbot powered by Grok 3 that interacts with your E-commerce MCP Server.

## 🚀 Features

- **🤖 Grok 3 AI Integration**: Natural language understanding and generation
- **💬 Conversational Interface**: Chat naturally about your e-commerce operations
- **🎯 Smart Intent Recognition**: Understands what you want to do from context
- **📊 Rich Responses**: Beautifully formatted data presentation
- **🛍️ Complete E-commerce Management**: All MCP server functionality via chat
- **✨ Enhanced UI**: Modern, responsive design with smooth animations

## 🆚 Differences from Basic Chatbot

| Feature | Basic Chatbot | Grok AI Chatbot |
|---------|---------------|-----------------|
| **AI Model** | Pattern matching | Grok 3 LLM |
| **Understanding** | Command-based | Natural language |
| **Responses** | Template-based | AI-generated |
| **Conversation** | Single exchanges | Context-aware chat |
| **Port** | 8765 | 8766 |
| **Interface** | Standard | Enhanced with AI indicators |

## 📋 Prerequisites

### Required Dependencies
```bash
pip install websockets mcp httpx
```

### Grok API Key (Recommended)
```bash
# Get your API key from X.AI
export XAI_API_KEY='your_api_key_here'
```

**Note**: The chatbot works without an API key but with limited AI features (falls back to pattern matching).

## 🚀 Quick Start

### Option 1: Use the Launcher (Recommended)
```bash
# From project root
python run_grok_chatbot.py
```

### Option 2: Manual Start
```bash
# Start the bridge server
cd chatbot-agent
python bridge.py

# Open index.html in your browser
```

## 🎯 Usage Examples

### Natural Language Commands
Unlike the basic chatbot, you can use natural language:

```
❌ Basic: "list products"
✅ Grok: "What products do we have in stock?"
✅ Grok: "Show me all our products"
✅ Grok: "I'd like to see the product catalog"
```

```
❌ Basic: "stock low"  
✅ Grok: "Which items are running low on inventory?"
✅ Grok: "What products need restocking?"
✅ Grok: "Show me products with low stock levels"
```

```
❌ Basic: "create product 'Widget' 29.99 WID-001 Electronics 50"
✅ Grok: "Help me create a new product"
✅ Grok: "I want to add a widget to my inventory"
✅ Grok: "Can you walk me through adding a new item?"
```

### Smart Context Understanding
The Grok chatbot understands context and can have conversations:

```
You: "I need to check my inventory"
Bot: "I'd be happy to help you check your inventory! What specifically would you like to see?"

You: "Items that might need restocking"
Bot: "Let me check which products are running low on stock..."
```

### Conversational Product Creation
```
You: "I want to add a new product"
Bot: "Great! I'll help you create a new product. Could you tell me the details like name, price, SKU, category, and stock quantity?"

You: "It's a wireless mouse, $29.99, SKU is MOUSE-002, Electronics category, 25 in stock"
Bot: "Perfect! Let me create that wireless mouse for you..."
```

## 🔧 Configuration

### Environment Variables
```bash
# Required for full AI features
export XAI_API_KEY='your_api_key_here'

# Optional: Adjust Grok model settings
export GROK_MODEL='grok-beta'  # default
export GROK_TEMPERATURE='0.7'  # default
```

### Customizing AI Behavior
Edit `grok_agent.py` to modify:
- AI personality and tone
- Response formatting preferences  
- Intent recognition patterns
- Conversation flow logic

## 🎨 Interface Features

### Enhanced Visual Design
- **Gradient backgrounds** with AI-themed colors
- **Animated message bubbles** with smooth transitions
- **AI thinking indicators** during processing
- **Avatar icons** for bot and user messages
- **Auto-resizing textarea** for longer messages

### Smart Interactions
- **Shift+Enter** for new lines
- **Enter** to send messages
- **Auto-scroll** to latest messages
- **Quick action buttons** for common tasks
- **Connection status** with auto-reconnect

## 🔧 Technical Architecture

### Components
```
chatbot-agent/
├── index.html      # Enhanced AI chatbot interface
├── app.js          # Frontend with AI-specific features
├── bridge.py       # WebSocket bridge for Grok agent
├── grok_agent.py   # Main AI agent with Grok integration
└── README.md       # This documentation
```

### Data Flow
1. **User Input** → Web Interface (app.js)
2. **WebSocket** → Bridge Server (bridge.py)
3. **AI Processing** → Grok Agent (grok_agent.py)
4. **Intent Analysis** → Grok 3 API (if available)
5. **Action Execution** → MCP Server (egile.agent)
6. **Response Generation** → Grok 3 API (if available)  
7. **Formatted Response** → Web Interface

### Fallback Behavior
If Grok API is unavailable, the agent falls back to:
- Pattern-matching for intent recognition
- Template-based response generation
- All core functionality remains available

## 🚦 API Usage

### Grok 3 Integration
The agent makes calls to X.AI's Grok API for:
- **Intent Analysis**: Understanding user requests
- **Response Generation**: Creating natural replies
- **Context Management**: Maintaining conversation flow

### Rate Limiting
- Intelligent caching of similar requests
- Fallback to local processing when needed
- Optimized API calls for cost efficiency

## 🔧 Development

### Adding New Capabilities
1. **Extend Intent Analysis**: Modify `analyze_intent_with_grok()`
2. **Add MCP Operations**: Update `execute_ecommerce_action()`
3. **Customize Responses**: Edit `generate_response_with_grok()`

### Debugging
```bash
# Enable debug logging
export PYTHONPATH=/path/to/egile
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from chatbot_agent.grok_agent import GrokEcommerceAgent
# Run tests...
"
```

## 🎯 Best Practices

### For Users
- **Be conversational**: "Can you help me..." works better than commands
- **Provide context**: "I'm looking for products that..." is clearer
- **Ask follow-ups**: The AI remembers conversation context

### For Developers
- **API Key Security**: Never commit API keys to version control
- **Error Handling**: Always provide fallback functionality
- **Response Formatting**: Keep AI responses scannable and actionable

## 🔄 Comparison with Basic Chatbot

### When to Use Grok Chatbot
- ✅ You want natural language interaction
- ✅ You need conversational context
- ✅ You have a Grok API key
- ✅ You prefer AI-generated responses

### When to Use Basic Chatbot
- ✅ You want faster, deterministic responses
- ✅ You prefer command-based interaction
- ✅ You don't need an API key
- ✅ You want simpler, lightweight operation

Both chatbots connect to the same MCP server and provide identical functionality - the difference is in the interaction style and intelligence level.

## 🆘 Troubleshooting

### Common Issues

**Connection Failed**
```bash
# Check if bridge server is running
ps aux | grep bridge.py

# Check port availability
netstat -an | grep 8766
```

**API Key Issues**
```bash
# Verify API key is set
echo $XAI_API_KEY

# Test API access
curl -H "Authorization: Bearer $XAI_API_KEY" https://api.x.ai/v1/models
```

**Slow Responses**
- Check internet connection for Grok API calls
- Consider using basic chatbot for faster responses
- Monitor API rate limits

### Getting Help
1. Check the console logs in your browser
2. Look at the bridge server terminal output
3. Verify MCP server is running
4. Test with basic chatbot first

Start chatting with AI-powered intelligence! 🤖✨
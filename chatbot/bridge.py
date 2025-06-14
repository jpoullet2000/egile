#!/usr/bin/env python3
"""
Working WebSocket bridge for connecting the browser chatbot to the MCP server.
"""

import asyncio
import json
import websockets
import logging
from typing import Dict, Any, Optional
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from egile.agent import EcommerceAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatbotBridge:
    def __init__(self):
        self.agent: Optional[EcommerceAgent] = None
        self.connected_clients = set()

    async def start_agent(self):
        """Initialize and start the MCP agent"""
        try:
            self.agent = EcommerceAgent()
            await self.agent.start_server()
            logger.info("MCP agent started successfully")
        except Exception as e:
            logger.error(f"Failed to start MCP agent: {e}")
            raise

    async def stop_agent(self):
        """Stop the MCP agent"""
        if self.agent:
            await self.agent.stop_server()
            logger.info("MCP agent stopped")

    async def handle_client(self, websocket):
        """Handle a new WebSocket client connection"""
        self.connected_clients.add(websocket)
        try:
            client_addr = getattr(websocket, "remote_address", "unknown")
            logger.info(
                f"Client connected from {client_addr}. Total clients: {len(self.connected_clients)}"
            )
        except Exception:
            logger.info(
                f"Client connected. Total clients: {len(self.connected_clients)}"
            )

        try:
            async for message in websocket:
                await self.process_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client disconnected normally")
        except Exception as e:
            logger.error(f"Error handling client: {e}")
        finally:
            self.connected_clients.discard(websocket)

    async def process_message(self, websocket, message: str):
        """Process a message from the web client"""
        try:
            logger.info(f"Received message: {message}")
            data = json.loads(message)
            message_type = data.get("type")

            if message_type == "chat_message":
                await self.handle_chat_message(websocket, data["message"])
            else:
                await self.send_error(
                    websocket, f"Unknown message type: {message_type}"
                )

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            await self.send_error(websocket, "Invalid JSON message")
        except KeyError as e:
            logger.error(f"Missing key in message: {e}")
            await self.send_error(websocket, f"Missing required field: {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send_error(websocket, f"Internal error: {str(e)}")

    async def handle_chat_message(self, websocket, user_message: str):
        """Handle a chat message and convert it to MCP tool calls"""
        try:
            action = self.parse_user_intent(user_message)
            logger.info(f"Action determined: {action}")  # Added log

            if action["type"] == "tool_call":
                result = await self.execute_tool(action["tool"], action["params"])
                logger.info(f"Result from execute_tool: {result}")  # Added log
                await self.send_tool_result(
                    websocket, action["tool"], result, success=True
                )
            elif action["type"] == "help":
                await self.send_help_message(websocket)
            elif action["type"] == "chat_response":
                await self.send_chat_response(websocket, action["message"])
            else:
                await self.send_chat_response(
                    websocket,
                    "I'm not sure how to help with that. Try 'help' for commands.",
                )

        except Exception as e:
            logger.error(f"Error handling chat message: {e}")
            await self.send_tool_result(websocket, "unknown", str(e), success=False)

    def parse_user_intent(self, message: str) -> Dict[str, Any]:
        """Parse user message and determine the intended action"""
        message_lower = message.lower().strip()

        # Help commands
        if any(word in message_lower for word in ["help", "commands"]):
            return {"type": "help"}

        # Product commands
        if "list products" in message_lower or "show products" in message_lower:
            return {"type": "tool_call", "tool": "list_products", "params": {}}

        # Customer commands
        if "list customers" in message_lower or "show customers" in message_lower:
            return {"type": "tool_call", "tool": "list_customers", "params": {}}

        # Order commands
        if "list orders" in message_lower or "show orders" in message_lower:
            return {"type": "tool_call", "tool": "list_orders", "params": {}}

        # Stock commands
        if "stock low" in message_lower or "low stock" in message_lower:
            return {
                "type": "tool_call",
                "tool": "get_low_stock_products",
                "params": {"threshold": 10},
            }

        # Default response
        return {
            "type": "chat_response",
            "message": "I can help you with:\n• 'list products'\n• 'list customers'\n• 'list orders'\n• 'stock low'\n• 'help'",
        }

    async def execute_tool(self, tool_name: str, params: Dict[str, Any]):
        """Execute an MCP tool call"""
        if not self.agent:
            raise Exception("MCP agent not initialized")

        tool_mapping = {
            "list_products": "get_all_products",
            "list_customers": "get_all_customers",
            "list_orders": "get_all_orders",
            "get_low_stock_products": "get_low_stock_products",
        }

        if tool_name not in tool_mapping:
            raise Exception(f"Unknown tool: {tool_name}")

        method_name = tool_mapping[tool_name]
        method = getattr(self.agent, method_name)

        try:
            if params:
                agent_response = await method(**params)
            else:
                agent_response = await method()

            # Handle AgentResponse object
            if hasattr(agent_response, "success"):
                if agent_response.success:
                    # Extract and parse the JSON data from the MCP response
                    raw_data = agent_response.data  # This is [{'type': 'text', 'text': 'JSON string'}]
                    if isinstance(raw_data, list) and len(raw_data) > 0:
                        text_content = raw_data[0].get('text', '[]')
                        try:
                            # Parse the JSON string to get the actual data
                            parsed_data = json.loads(text_content)
                            return parsed_data
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse JSON from MCP response: {text_content[:100]}...")
                            return text_content
                    return raw_data
                else:
                    raise Exception(agent_response.error or agent_response.message)
            else:
                # Direct result
                return agent_response

        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            raise

    async def send_tool_result(self, websocket, tool: str, result: Any, success: bool):
        """Send tool execution result to client"""
        try:
            response_data = {
                "type": "tool_result",
                "tool": tool,
                "result": result,
                "success": success,
            }
            json_response = json.dumps(response_data)
            await websocket.send(json_response)
        except TypeError as te:
            logger.error(f"TypeError during JSON serialization for tool '{tool}': {te}")
            logger.error(
                f"Data that failed to serialize (type: {type(result)}): {str(result)[:500]}"
            )
            error_response_data = {
                "type": "error",
                "message": f"Failed to serialize result for tool '{tool}'. Server encountered a TypeError.",
                "tool": tool,
            }
            try:
                await websocket.send(json.dumps(error_response_data))
            except Exception as e_send_err:
                logger.error(f"Failed to send TypeError notification: {e_send_err}")
        except Exception as e:
            logger.error(f"Failed to send tool result for tool '{tool}': {e}")
            try:
                generic_error = {
                    "type": "error",
                    "message": "Failed to send tool result due to an unexpected server error.",
                }
                await websocket.send(json.dumps(generic_error))
            except Exception as final_e:
                logger.error(
                    f"CRITICAL: Failed even to send a generic error message for tool_result: {final_e}"
                )

    async def send_chat_response(self, websocket, message: str):
        """Send a chat response to client"""
        try:
            response_data = {"type": "chat_response", "message": message}
            json_response = json.dumps(response_data)
            await websocket.send(json_response)
        except TypeError as te:
            logger.error(f"TypeError during JSON serialization for chat_response: {te}")
            logger.error(f"Message that failed to serialize: {message[:500]}")
            # Attempt to send a simplified error message if the original message itself was the problem
            try:
                error_response_data = {
                    "type": "error",
                    "message": "Failed to serialize chat response due to a TypeError.",
                }
                await websocket.send(json.dumps(error_response_data))
            except Exception as e_send_err:
                logger.error(
                    f"Failed to send TypeError notification for chat_response: {e_send_err}"
                )
        except Exception as e:
            logger.error(f"Failed to send chat response: {e}")
            try:
                generic_error = {
                    "type": "error",
                    "message": "Failed to send chat response due to an unexpected server error.",
                }
                await websocket.send(json.dumps(generic_error))
            except Exception as final_e:
                logger.error(
                    f"CRITICAL: Failed even to send a generic error message for chat_response: {final_e}"
                )

    async def send_help_message(self, websocket):
        """Send help message to client"""
        help_text = """Available commands:
• 'list products' - Show all products
• 'list customers' - Show all customers  
• 'list orders' - Show all orders
• 'stock low' - Show low stock products
• 'help' - Show this help message

You can also type natural language requests!"""
        await self.send_chat_response(websocket, help_text)

    async def send_error(self, websocket, error_message: str):
        """Send error message to client"""
        try:
            response_data = {"type": "error", "message": error_message}
            json_response = json.dumps(response_data)
            await websocket.send(json_response)
        except TypeError as te:
            # This is less likely here as error_message is usually a string, but good for robustness
            logger.error(f"TypeError during JSON serialization for send_error: {te}")
            logger.error(
                f"Error message that failed to serialize: {error_message[:500]}"
            )
            # Attempt to send a very basic error if the error_message itself was complex
            try:
                basic_error = {
                    "type": "error",
                    "message": "A server error occurred, and the error message itself could not be serialized.",
                }
                await websocket.send(json.dumps(basic_error))
            except Exception as e_send_err:
                logger.error(
                    f"Failed to send TypeError notification for send_error: {e_send_err}"
                )
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")
            # Final attempt to notify client of an issue
            try:
                critical_error = {
                    "type": "error",
                    "message": "A critical server error occurred while trying to send an error message.",
                }
                await websocket.send(json.dumps(critical_error))
            except Exception as final_e:
                logger.error(
                    f"CRITICAL: Failed even to send a critical error message: {final_e}"
                )


async def main():
    """Main function to start the WebSocket bridge server"""
    bridge = ChatbotBridge()

    try:
        await bridge.start_agent()

        logger.info("Starting WebSocket server on localhost:8765")
        # Direct method reference works with websockets 15.x
        server = await websockets.serve(bridge.handle_client, "localhost", 8765)

        logger.info("Chatbot bridge is running!")
        logger.info("Press Ctrl+C to stop the server.")

        await server.wait_closed()

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        await bridge.stop_agent()


if __name__ == "__main__":
    asyncio.run(main())

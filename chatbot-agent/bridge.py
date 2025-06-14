#!/usr/bin/env python3
"""
WebSocket bridge for the Grok-powered chatbot.
This server connects the web frontend to the Grok AI agent.
"""

import asyncio
import json
import websockets
import logging
from typing import Set
import sys
from pathlib import Path

# Add the current directory to the Python path for local imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from grok_agent import GrokEcommerceAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GrokChatbotBridge:
    def __init__(self):
        self.agent: GrokEcommerceAgent = None
        self.connected_clients: Set = set()

    async def start_agent(self):
        """Initialize and start the Grok agent"""
        try:
            self.agent = GrokEcommerceAgent()
            await self.agent.start()
            logger.info("Grok AI agent started successfully")
        except Exception as e:
            logger.error(f"Failed to start Grok agent: {e}")
            raise

    async def stop_agent(self):
        """Stop the Grok agent"""
        if self.agent:
            await self.agent.stop()
            logger.info("Grok AI agent stopped")

    async def handle_client(self, websocket, path):
        """Handle a new WebSocket client connection"""
        self.connected_clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.connected_clients)}")

        try:
            async for message in websocket:
                await self.process_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client disconnected")
        except Exception as e:
            logger.error(f"Error handling client: {e}")
        finally:
            self.connected_clients.discard(websocket)

    async def process_message(self, websocket, message: str):
        """Process a message from the web client"""
        try:
            data = json.loads(message)
            message_type = data.get("type")

            if message_type == "chat_message":
                await self.handle_chat_message(websocket, data["message"])
            else:
                await self.send_error(
                    websocket, f"Unknown message type: {message_type}"
                )

        except json.JSONDecodeError:
            await self.send_error(websocket, "Invalid JSON message")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send_error(websocket, f"Internal error: {str(e)}")

    async def handle_chat_message(self, websocket, user_message: str):
        """Handle a chat message using the Grok agent"""
        try:
            # Process the message with the Grok agent
            response = await self.agent.process_message(user_message)

            # Send the response back to the client
            await websocket.send(json.dumps(response))

        except Exception as e:
            logger.error(f"Error handling chat message: {e}")
            await self.send_error(websocket, f"Agent error: {str(e)}")

    async def send_error(self, websocket, error_message: str):
        """Send error message to client"""
        response = {"type": "error", "message": error_message}
        await websocket.send(json.dumps(response))


async def main():
    """Main function to start the WebSocket bridge server"""
    bridge = GrokChatbotBridge()

    try:
        # Start the Grok agent
        await bridge.start_agent()

        # Start WebSocket server
        logger.info("Starting WebSocket server on localhost:8766")
        server = await websockets.serve(bridge.handle_client, "localhost", 8766)

        logger.info(
            "Grok chatbot bridge is running! Open chatbot-agent/index.html in your browser."
        )
        logger.info("Press Ctrl+C to stop the server.")

        # Keep the server running
        await server.wait_closed()

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        await bridge.stop_agent()


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
WebSocket bridge for the Smart Agent-powered chatbot.
This server connects the web frontend to the new SmartAgent.
"""

import asyncio
import json
import websockets
import logging
from typing import Set
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import after path setup
from egile.smart_agent import SmartAgent


class SmartChatbotBridge:
    def __init__(self):
        self.agent: SmartAgent = None
        self.connected_clients: Set = set()

    async def start_agent(self):
        """Initialize and start the Smart Agent"""
        try:
            self.agent = SmartAgent()
            await self.agent.start()
            logger.info("Smart Agent started successfully")
        except Exception as e:
            logger.error(f"Failed to start Smart Agent: {e}")
            raise

    async def stop_agent(self):
        """Stop the Smart Agent"""
        if self.agent:
            await self.agent.stop()
            logger.info("Smart Agent stopped")

    async def handle_client(self, websocket, path=None):
        """Handle incoming WebSocket connections"""
        self.connected_clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.connected_clients)}")

        try:
            # Send welcome message
            welcome_msg = {
                "type": "system",
                "message": "Connected to Smart E-commerce Agent. How can I help you today?",
                "timestamp": asyncio.get_event_loop().time(),
            }
            await websocket.send(json.dumps(welcome_msg))

            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.process_message(websocket, data)
                except json.JSONDecodeError:
                    error_msg = {
                        "type": "error",
                        "message": "Invalid JSON format",
                        "timestamp": asyncio.get_event_loop().time(),
                    }
                    await websocket.send(json.dumps(error_msg))
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    error_msg = {
                        "type": "error",
                        "message": f"Error processing message: {str(e)}",
                        "timestamp": asyncio.get_event_loop().time(),
                    }
                    await websocket.send(json.dumps(error_msg))

        except websockets.exceptions.ConnectionClosed:
            logger.info("Client disconnected")
        finally:
            self.connected_clients.discard(websocket)
            logger.info(f"Client removed. Total clients: {len(self.connected_clients)}")

    async def process_message(self, websocket, data):
        """Process incoming messages from the client"""
        if not self.agent:
            error_msg = {
                "type": "error",
                "message": "Agent not initialized",
                "timestamp": asyncio.get_event_loop().time(),
            }
            await websocket.send(json.dumps(error_msg))
            return

        user_message = data.get("message", "")
        if not user_message:
            return

        try:
            # Send typing indicator
            typing_msg = {
                "type": "typing",
                "message": "Smart Agent is thinking...",
                "timestamp": asyncio.get_event_loop().time(),
            }
            await websocket.send(json.dumps(typing_msg))  # Process with Smart Agent
            response_data = await self.agent.process_request(user_message)

            # Extract the message from the response
            if isinstance(response_data, dict):
                response_message = response_data.get("message", str(response_data))
                response_type = (
                    "agent" if response_data.get("success", True) else "error"
                )
            else:
                response_message = str(response_data)
                response_type = "agent"

            # Send response
            response_msg = {
                "type": response_type,
                "message": response_message,
                "timestamp": asyncio.get_event_loop().time(),
            }
            await websocket.send(json.dumps(response_msg))

        except Exception as e:
            logger.error(f"Error processing user message: {e}")
            error_msg = {
                "type": "error",
                "message": f"Sorry, I encountered an error: {str(e)}",
                "timestamp": asyncio.get_event_loop().time(),
            }
            await websocket.send(json.dumps(error_msg))

    async def start_server(self, host="localhost", port=8770):
        """Start the WebSocket server"""
        await self.start_agent()

        logger.info(f"Starting Smart Chatbot Bridge on {host}:{port}")

        # Try multiple ports if the default is in use
        max_attempts = 5
        current_port = port

        for attempt in range(max_attempts):
            try:
                # Use direct method reference for better compatibility
                async with websockets.serve(self.handle_client, host, current_port):
                    logger.info(
                        f"Smart Chatbot Bridge listening on ws://{host}:{current_port}"
                    )
                    print(f"✅ Smart Agent Bridge started on port {current_port}")
                    # Keep the server running
                    await asyncio.Future()  # Run forever
            except OSError as e:
                if "Address already in use" in str(e) and attempt < max_attempts - 1:
                    current_port += 1
                    logger.warning(
                        f"Port {current_port - 1} in use, trying port {current_port}"
                    )
                    continue
                else:
                    logger.error(f"Server error after {max_attempts} attempts: {e}")
                    print(f"❌ Failed to start server: {e}")
                    break
            except Exception as e:
                logger.error(f"Server error: {e}")
                print(f"❌ Server error: {e}")
                break

        await self.stop_agent()


async def main():
    """Main entry point"""
    bridge = SmartChatbotBridge()
    try:
        await bridge.start_server()
    except KeyboardInterrupt:
        logger.info("Shutting down bridge...")
    except Exception as e:
        logger.error(f"Bridge error: {e}")


if __name__ == "__main__":
    asyncio.run(main())

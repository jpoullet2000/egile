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
import socket

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import after path setup
from egile.smart_agent import SmartAgent


def find_available_port(start_port=8770, max_attempts=20):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise OSError(
        f"No available ports found in range {start_port}-{start_port + max_attempts}"
    )


class SmartChatbotBridge:
    def __init__(self):
        self.agent: SmartAgent = None
        self.connected_clients: Set = set()
        self.max_clients = 10  # Limit connections
        self.client_addresses: dict = {}  # Track client addresses

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

        # Check connection limit
        if len(self.connected_clients) >= self.max_clients:
            logger.warning(
                f"Connection limit reached ({self.max_clients}), rejecting new connection"
            )
            await websocket.close(1008, "Server full")
            return

        client_address = websocket.remote_address
        logger.info(f"New connection from {client_address}")

        # Track client address connections
        if client_address not in self.client_addresses:
            self.client_addresses[client_address] = []
        self.client_addresses[client_address].append(websocket)

        # Limit connections per IP
        if len(self.client_addresses[client_address]) > 3:
            logger.warning(
                f"Too many connections from {client_address}, closing oldest"
            )
            # Close oldest connection
            oldest = self.client_addresses[client_address].pop(0)
            if oldest in self.connected_clients:
                self.connected_clients.discard(oldest)
                try:
                    await oldest.close(1008, "Too many connections")
                except Exception as e:
                    logger.debug(f"Error closing old connection: {e}")

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
            # Clean up client tracking
            self.connected_clients.discard(websocket)

            # Clean up address tracking
            if client_address in self.client_addresses:
                if websocket in self.client_addresses[client_address]:
                    self.client_addresses[client_address].remove(websocket)
                if not self.client_addresses[client_address]:
                    del self.client_addresses[client_address]

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

        # Handle ping messages
        if data.get("type") == "ping":
            pong_msg = {
                "type": "pong",
                "timestamp": asyncio.get_event_loop().time(),
            }
            await websocket.send(json.dumps(pong_msg))
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

    async def start_server(self, host="0.0.0.0", port=8770):
        """Start the WebSocket server"""
        await self.start_agent()

        logger.info(f"Starting Smart Chatbot Bridge on {host}:{port}")

        # Find an available port if the default is in use
        try:
            port = find_available_port(port)
            logger.info(f"Using available port: {port}")
        except OSError as e:
            logger.error(f"Failed to find an available port: {e}")
            return

        try:
            # Use direct method reference for better compatibility
            async with websockets.serve(self.handle_client, host, port):
                logger.info(f"Smart Chatbot Bridge listening on ws://{host}:{port}")
                print(f"✅ Smart Agent Bridge started on port {port}")
                # Keep the server running
                await asyncio.Future()  # Run forever
        except Exception as e:
            logger.error(f"Server error: {e}")
            print(f"❌ Server error: {e}")

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

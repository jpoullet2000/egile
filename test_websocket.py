#!/usr/bin/env python3
"""
Simple test to verify the WebSocket server works
"""

import asyncio
import websockets
import json


async def test_websocket():
    """Test WebSocket connection to the bridge"""
    try:
        print("🔌 Attempting to connect to ws://localhost:8765...")

        # Connect to the WebSocket server
        websocket = await websockets.connect("ws://localhost:8765")
        print("✅ Connected successfully!")

        # Send a test message
        test_message = {"type": "chat_message", "message": "list products"}

        print("📤 Sending test message...")
        await websocket.send(json.dumps(test_message))

        # Wait for response
        print("📥 Waiting for response...")
        response = await websocket.recv()
        print(f"✅ Received response: {response}")

        await websocket.close()
        print("🔚 Connection closed")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_websocket())

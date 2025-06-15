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
        print("🔌 Attempting to connect to ws://localhost:8768...")

        # Connect to the WebSocket server
        websocket = await websockets.connect("ws://localhost:8768")
        print("✅ Connected successfully!")

        # Send a test message
        test_message = {"type": "chat_message", "message": "show me all products"}

        print("📤 Sending test message...")
        await websocket.send(json.dumps(test_message))

        # Wait for response
        print("📥 Waiting for responses...")

        # Wait for connection confirmation
        response1 = await websocket.recv()
        print(f"✅ Connection response: {response1}")

        # Wait for actual data response
        try:
            response2 = await asyncio.wait_for(websocket.recv(), timeout=15.0)
            print(f"✅ Data response: {response2[:200]}...")
        except asyncio.TimeoutError:
            print("⏰ Timeout waiting for data response")

        await websocket.close()
        print("🔚 Connection closed")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_websocket())

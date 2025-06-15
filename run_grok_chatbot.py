#!/usr/bin/env python3
"""
Launcher script for the Grok-powered E-commerce Chatbot.
This script starts the Grok agent bridge and opens the enhanced chatbot interface.
"""

import subprocess
import sys
import webbrowser
import time
import os
import threading
import http.server
import socketserver
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ["websockets", "mcp", "httpx"]
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nPlease install them with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False

    return True


def check_grok_api_key():
    """Check if XAI API key is available"""
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        print("⚠️  Warning: No XAI API key found!")
        print("   Set the XAI_API_KEY environment variable to enable full AI features.")
        print("   The chatbot will work with limited functionality without it.")
        print("\n   To set the API key:")
        print("   export XAI_API_KEY='your_api_key_here'")
        return False
    else:
        print("✅ XAI API key found")
        return True


def start_http_server(chatbot_dir, port=8080):
    """Start HTTP server to serve the Grok chatbot interface"""

    class ChatbotHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(chatbot_dir), **kwargs)

    try:
        with socketserver.TCPServer(("", port), ChatbotHTTPRequestHandler) as httpd:
            print(f"✅ HTTP server started on http://localhost:{port}")
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(
                f"⚠️  Port {port} is already in use. Please close other applications using this port."
            )
            return None
        else:
            raise


def start_grok_chatbot():
    """Start the Grok-powered chatbot system"""
    print("🚀 Starting Grok AI E-commerce Chatbot...")
    print("=" * 55)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Check API key (warn but don't exit)
    has_api_key = check_grok_api_key()

    # Check if required files exist
    script_dir = Path(__file__).parent
    bridge_file = script_dir / "chatbot-agent" / "bridge.py"
    html_file = script_dir / "chatbot-agent" / "index.html"

    if not bridge_file.exists():
        print(f"❌ Bridge server file not found: {bridge_file}")
        sys.exit(1)

    if not html_file.exists():
        print(f"❌ HTML file not found: {html_file}")
        sys.exit(1)

    print("✅ All files found")
    print("✅ Dependencies verified")

    # Start the bridge server
    print("\n🤖 Starting Grok AI agent bridge server...")
    try:
        # Start the bridge server in background
        bridge_process = subprocess.Popen(
            [sys.executable, str(bridge_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Wait a moment for server to start
        time.sleep(3)

        # Check if process is still running
        if bridge_process.poll() is not None:
            stdout, stderr = bridge_process.communicate()
            print("❌ Failed to start Grok agent bridge:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            sys.exit(1)

        print("✅ Grok agent bridge started successfully")

        # Start HTTP server in a separate thread
        chatbot_dir = script_dir / "chatbot-agent"
        http_server_thread = threading.Thread(
            target=start_http_server, args=(chatbot_dir, 8081), daemon=True
        )
        http_server_thread.start()

        # Give the HTTP server a moment to start
        time.sleep(2)

        # Open the chatbot in browser
        chatbot_url = "http://localhost:8081"
        print("\n🌐 Opening Grok chatbot in browser...")
        print(f"   URL: {chatbot_url}")

        try:
            webbrowser.open(chatbot_url)
            print("✅ Browser opened")
        except Exception as e:
            print(f"⚠️  Could not auto-open browser: {e}")
            print(f"   Please manually open: {chatbot_url}")

        print("\n" + "=" * 55)
        print("🎉 Grok AI Chatbot is ready!")
        print("=" * 55)
        print("\n📋 Features:")
        print("• 🤖 Powered by Grok 3 AI for natural conversations")
        print("• 🛍️ Complete e-commerce management")
        print("• 💬 Natural language understanding")
        print("• 🎯 Smart intent recognition")
        print("• 📊 Rich data formatting")

        if has_api_key:
            print("• ✨ Full AI capabilities enabled")
        else:
            print("• ⚠️  Limited mode (set XAI_API_KEY for full features)")

        print("\n💬 Try these natural language commands:")
        print("• 'What products do we have in stock?'")
        print("• 'Show me customers who haven't ordered recently'")
        print("• 'Create a new product for me'")
        print("• 'Which items are running low?'")
        print("• 'Help me process a new order'")

        print("\n📍 WebSocket bridge: ws://localhost:8767")
        print("📍 Web interface: http://localhost:8081")
        print("🛑 To stop the chatbot: Press Ctrl+C in this terminal")

        # Keep the script running and monitor the bridge process
        try:
            while True:
                if bridge_process.poll() is not None:
                    stdout, stderr = bridge_process.communicate()
                    print("\n❌ Grok agent bridge stopped unexpectedly")
                    if stderr:
                        print(f"Error: {stderr}")
                    break
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down Grok chatbot...")
            bridge_process.terminate()
            bridge_process.wait()
            print("✅ Grok chatbot stopped successfully")

    except Exception as e:
        print(f"❌ Error starting Grok chatbot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    start_grok_chatbot()

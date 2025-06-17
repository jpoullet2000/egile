#!/usr/bin/env python3
"""
Launcher script for the Smart Agent-powered E-commerce Chatbot.
This script starts the Smart Agent bridge and opens the enhanced chatbot interface.
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

# Global variable to track web server port
web_server_port = 8080


def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ["websockets", "mcp", "httpx", "aiofiles"]
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


def check_api_key():
    """Check if XAI API key is available"""
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        print("⚠️  Warning: No XAI API key found!")
        print("   Set the XAI_API_KEY environment variable to enable full AI features.")
        print("   The Smart Agent will work with limited functionality without it.")
        print("\n   To set the API key:")
        print("   export XAI_API_KEY='your_api_key_here'")
        return False
    else:
        print("✅ XAI API key found")
        return True


def start_web_server():
    """Start a simple HTTP server for the chatbot interface"""
    chatbot_dir = Path(__file__).parent / "chatbot-agent"
    os.chdir(chatbot_dir)

    class SilentHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # Suppress HTTP server logs

    # Try multiple ports
    ports_to_try = [8080, 8081, 8082, 8083, 8084]

    for port in ports_to_try:
        try:
            with socketserver.TCPServer(("", port), SilentHandler) as httpd:
                print(f"🌐 Web server started at http://localhost:{port}")
                # Write the port to a temporary file so main thread can read it
                with open("/tmp/smart_chatbot_port.txt", "w") as f:
                    f.write(str(port))
                httpd.serve_forever()
                break
        except OSError as e:
            if "Address already in use" in str(e) and port != ports_to_try[-1]:
                print(f"⚠️  Port {port} in use, trying next port...")
                continue
            else:
                print(f"❌ Failed to start web server: {e}")
                break


def start_smart_bridge():
    """Start the Smart Agent WebSocket bridge"""
    bridge_path = Path(__file__).parent / "chatbot-agent" / "smart_bridge.py"

    try:
        subprocess.run([sys.executable, str(bridge_path)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Smart Agent bridge: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Smart Agent bridge stopped")


def update_frontend():
    """Update the frontend to connect to the Smart Agent bridge"""
    frontend_js = Path(__file__).parent / "chatbot-agent" / "app_smart.js"

    if frontend_js.exists():
        print("✅ Frontend configured for Smart Agent bridge")
    else:
        print("⚠️  Smart frontend (app_smart.js) not found - using fallback")
        # Fall back to updating the original app.js
        fallback_js = Path(__file__).parent / "chatbot-agent" / "app.js"
        if fallback_js.exists():
            with open(fallback_js, "r") as f:
                content = f.read()

            # Update WebSocket port for Smart Agent bridge
            if "ws://localhost:8768" in content:
                content = content.replace("ws://localhost:8768", "ws://localhost:8770")
                with open(fallback_js, "w") as f:
                    f.write(content)
                print("✅ Fallback frontend updated for Smart Agent bridge")


def main():
    """Main entry point"""
    print("🚀 Starting Smart Agent E-commerce Chatbot")
    print("=" * 50)

    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first")
        sys.exit(1)

    # Check API key (warning only)
    check_api_key()

    # Update frontend configuration
    update_frontend()

    print("\n🔧 Starting services...")

    # Start web server in a separate thread
    web_thread = threading.Thread(target=start_web_server, daemon=True)
    web_thread.start()

    # Give the web server a moment to start and write port info
    time.sleep(2)

    # Read the actual port used by web server
    try:
        with open("/tmp/smart_chatbot_port.txt", "r") as f:
            web_port = f.read().strip()
        browser_url = f"http://localhost:{web_port}"
    except Exception:
        browser_url = "http://localhost:8080"  # fallback

    # Open browser
    print(f"🌍 Opening browser at {browser_url}...")
    webbrowser.open(browser_url)

    print("\n🤖 Starting Smart Agent bridge...")
    print("   (Press Ctrl+C to stop)")
    print("=" * 50)

    try:
        # Start the Smart Agent bridge (this will block)
        start_smart_bridge()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down Smart Agent Chatbot")
        print("✅ All services stopped")


if __name__ == "__main__":
    main()

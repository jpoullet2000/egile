#!/usr/bin/env python3
"""
Simple chatbot launcher that serves files via HTTP to avoid browser issues.
"""

import subprocess
import sys
import time
import webbrowser
import threading
import http.server
import socketserver
from pathlib import Path


def start_simple_chatbot():
    """Start chatbot with simple HTTP server"""
    print("🚀 Starting Simple E-commerce Chatbot...")
    print("=" * 40)

    # Check files
    script_dir = Path(__file__).parent
    bridge_file = script_dir / "chatbot" / "bridge.py"
    chatbot_dir = script_dir / "chatbot"

    if not bridge_file.exists():
        print(f"❌ Bridge file not found: {bridge_file}")
        return

    if not chatbot_dir.exists():
        print(f"❌ Chatbot directory not found: {chatbot_dir}")
        return

    print("✅ Files found")

    # Kill any existing bridge process
    try:
        subprocess.run(["pkill", "-f", "bridge.py"], check=False)
        time.sleep(1)
    except Exception:
        pass

    # Start bridge server
    print("🔗 Starting bridge server...")
    bridge_process = subprocess.Popen([sys.executable, str(bridge_file)])
    time.sleep(3)

    if bridge_process.poll() is not None:
        print("❌ Bridge server failed to start")
        return

    print("✅ Bridge server started")

    # Start HTTP server
    print("🌐 Starting HTTP server...")

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(chatbot_dir), **kwargs)

    port = 8080
    try:
        httpd = socketserver.TCPServer(("", port), Handler)
        print(f"✅ HTTP server started on http://localhost:{port}")

        # Start server in background
        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()

        # Open browser
        url = f"http://localhost:{port}"
        print(f"🌐 Opening: {url}")
        webbrowser.open(url)

        print("\n" + "=" * 40)
        print("🎉 Chatbot Ready!")
        print("=" * 40)
        print(f"🌐 URL: {url}")
        print("🔌 WebSocket: ws://localhost:8765")
        print("\n🛑 Press Ctrl+C to stop")

        # Keep running
        try:
            while bridge_process.poll() is None:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping...")
            bridge_process.terminate()
            httpd.shutdown()
            print("✅ Stopped")

    except OSError as e:
        print(f"❌ HTTP server error: {e}")
        bridge_process.terminate()


if __name__ == "__main__":
    start_simple_chatbot()

#!/usr/bin/env python3
"""
Enhanced launcher that serves the chatbot via HTTP server to avoid browser issues.
"""

import subprocess
import sys
import time
import webbrowser
import threading
import http.server
import socketserver
from pathlib import Path


def serve_chatbot_files(port=8080):
    """Serve chatbot files via HTTP server"""
    chatbot_dir = Path(__file__).parent / "chatbot"

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(chatbot_dir), **kwargs)

    try:
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f"✅ HTTP server started on http://localhost:{port}")
            httpd.serve_forever()
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"⚠️  Port {port} is busy, trying {port + 1}")
            serve_chatbot_files(port + 1)
        else:
            raise


def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ["websockets", "mcp"]
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


def kill_existing_servers():
    """Kill any existing servers on our ports"""
    import os
    import signal

    ports_to_clear = [8765, 8080, 8081, 8082]

    for port in ports_to_clear:
        try:
            # Use lsof to find processes using the port
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"], capture_output=True, text=True
            )
            if result.returncode == 0:
                pids = result.stdout.strip().split("\n")
                for pid in pids:
                    if pid:
                        print(f"🔧 Killing process {pid} using port {port}")
                        os.kill(int(pid), signal.SIGTERM)
                        time.sleep(0.5)
        except (subprocess.SubprocessError, ValueError, OSError):
            # If lsof fails or process doesn't exist, continue
            continue


def start_enhanced_chatbot():
    """Start the chatbot with HTTP server"""
    print("🚀 Starting Enhanced Egile E-commerce Chatbot...")
    print("=" * 55)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Kill existing servers
    try:
        kill_existing_servers()
        time.sleep(1)
    except Exception as e:
        print(f"⚠️  Could not clean ports: {e}")

    # Check if required files exist
    script_dir = Path(__file__).parent
    bridge_file = script_dir / "chatbot" / "bridge.py"
    html_file = script_dir / "chatbot" / "index.html"

    if not bridge_file.exists():
        print(f"❌ Bridge server file not found: {bridge_file}")
        sys.exit(1)

    if not html_file.exists():
        print(f"❌ HTML file not found: {html_file}")
        sys.exit(1)

    print("✅ All files found")
    print("✅ Dependencies verified")

    try:
        # Start the bridge server
        print("\n🔗 Starting WebSocket bridge server...")
        bridge_process = subprocess.Popen(
            [sys.executable, str(bridge_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Wait for bridge to start
        time.sleep(3)

        # Check if bridge is running
        if bridge_process.poll() is not None:
            stdout, stderr = bridge_process.communicate()
            print("❌ Failed to start bridge server:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            sys.exit(1)

        print("✅ Bridge server started on ws://localhost:8765")

        # Start HTTP server in background thread
        print("\n🌐 Starting HTTP server for chatbot...")
        http_thread = threading.Thread(
            target=serve_chatbot_files, args=(8080,), daemon=True
        )
        http_thread.start()

        time.sleep(2)  # Let HTTP server start

        # Open browser
        chatbot_url = "http://localhost:8080"
        print(f"🌐 Opening chatbot at: {chatbot_url}")

        try:
            webbrowser.open(chatbot_url)
            print("✅ Browser opened")
        except Exception as e:
            print(f"⚠️  Could not auto-open browser: {e}")
            print(f"   Please manually open: {chatbot_url}")

        print("\n" + "=" * 55)
        print("🎉 Enhanced Chatbot is ready!")
        print("=" * 55)
        print(f"\n🌐 Chatbot URL: {chatbot_url}")
        print("🔌 WebSocket Bridge: ws://localhost:8765")
        print("📱 HTTP Server: http://localhost:8080")

        print("\n💬 Try these commands in the chatbot:")
        print("• 'list products' - Show all products")
        print(
            "• 'create product \"Widget\" 29.99 WID-001 Electronics 50' - Create a product"
        )
        print("• 'list customers' - Show all customers")
        print("• 'help' - See all available commands")

        print("\n🛑 To stop the chatbot: Press Ctrl+C in this terminal")

        # Keep running and monitor bridge process
        try:
            while True:
                if bridge_process.poll() is not None:
                    stdout, stderr = bridge_process.communicate()
                    print("\n❌ Bridge server stopped unexpectedly")
                    if stderr:
                        print(f"Error: {stderr}")
                    break
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down chatbot...")
            bridge_process.terminate()
            bridge_process.wait()
            print("✅ Chatbot stopped successfully")

    except Exception as e:
        print(f"❌ Error starting chatbot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    start_enhanced_chatbot()

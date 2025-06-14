#!/usr/bin/env python3
"""
Stable chatbot launcher with better connection handling and debugging.
"""

import subprocess
import sys
import time
import webbrowser
import threading
import http.server
import socketserver
import signal
import os
from pathlib import Path


def serve_chatbot_files(port=8080):
    """Serve chatbot files via HTTP server"""
    chatbot_dir = Path(__file__).parent / "chatbot"

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(chatbot_dir), **kwargs)

        def log_message(self, format, *args):
            # Suppress HTTP server logs to reduce noise
            pass

    try:
        with socketserver.TCPServer(("", port), Handler) as httpd:
            httpd.allow_reuse_address = True
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
    ports_to_clear = [8765, 8080, 8081, 8082]

    for port in ports_to_clear:
        try:
            # Use netstat to find processes using the port
            result = subprocess.run(
                ["netstat", "-tulpn"], capture_output=True, text=True
            )
            if result.returncode == 0:
                lines = result.stdout.split("\n")
                for line in lines:
                    if f":{port} " in line and "LISTEN" in line:
                        # Extract PID from netstat output
                        parts = line.split()
                        if len(parts) > 6:
                            pid_info = parts[6]
                            if "/" in pid_info:
                                pid = pid_info.split("/")[0]
                                if pid.isdigit():
                                    print(f"🔧 Killing process {pid} using port {port}")
                                    os.kill(int(pid), signal.SIGTERM)
                                    time.sleep(0.5)
        except (subprocess.SubprocessError, ValueError, OSError, ProcessLookupError):
            continue

    # Also try pkill as backup
    try:
        subprocess.run(["pkill", "-f", "bridge.py"], check=False)
        time.sleep(1)
    except Exception:
        pass


def start_stable_chatbot():
    """Start the chatbot with better stability"""
    print("🚀 Starting Stable Egile E-commerce Chatbot...")
    print("=" * 50)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Kill existing servers
    print("🔧 Cleaning up existing processes...")
    kill_existing_servers()
    time.sleep(2)

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
    print("✅ Ports cleaned")

    try:
        # Start the bridge server with better logging
        print("\n🔗 Starting WebSocket bridge server...")
        bridge_env = os.environ.copy()
        bridge_env["PYTHONUNBUFFERED"] = "1"  # Force unbuffered output

        bridge_process = subprocess.Popen(
            [sys.executable, str(bridge_file)],
            env=bridge_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Combine stderr with stdout
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True,
        )

        # Monitor bridge startup with timeout
        startup_timeout = 10
        start_time = time.time()
        bridge_started = False

        print("📋 Bridge server startup log:")
        while time.time() - start_time < startup_timeout:
            if bridge_process.poll() is not None:
                # Process has terminated
                output, _ = bridge_process.communicate()
                print("❌ Bridge server terminated during startup:")
                print(output)
                sys.exit(1)

            # Check if we can connect to the WebSocket port
            try:
                import socket

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(("localhost", 8765))
                sock.close()
                if result == 0:
                    bridge_started = True
                    break
            except Exception:
                pass

            time.sleep(0.5)

        if not bridge_started:
            print("❌ Bridge server failed to start within timeout")
            bridge_process.terminate()
            sys.exit(1)

        print("✅ Bridge server started and listening on ws://localhost:8765")

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

        print("\n" + "=" * 50)
        print("🎉 Stable Chatbot is ready!")
        print("=" * 50)
        print(f"\n🌐 Chatbot URL: {chatbot_url}")
        print("🔌 WebSocket Bridge: ws://localhost:8765")
        print("📱 HTTP Server: http://localhost:8080")

        print("\n💬 Try these commands in the chatbot:")
        print("• 'list products' - Show all products")
        print("• 'list customers' - Show all customers")
        print("• 'help' - See all available commands")

        print("\n📊 Connection Status:")
        print("   Monitoring bridge process for stability...")
        print("\n🛑 To stop the chatbot: Press Ctrl+C in this terminal")

        # Monitor bridge process with detailed logging
        restart_count = 0
        max_restarts = 3

        try:
            while True:
                if bridge_process.poll() is not None:
                    # Bridge process has died
                    restart_count += 1
                    print(f"\n⚠️  Bridge server stopped (restart #{restart_count})")

                    if restart_count > max_restarts:
                        print("❌ Too many restarts, giving up")
                        break

                    print("🔄 Attempting to restart bridge server...")
                    time.sleep(2)

                    # Restart bridge
                    bridge_process = subprocess.Popen(
                        [sys.executable, str(bridge_file)],
                        env=bridge_env,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        universal_newlines=True,
                    )
                    time.sleep(3)

                    if bridge_process.poll() is None:
                        print("✅ Bridge server restarted successfully")
                    else:
                        print("❌ Failed to restart bridge server")
                        break

                time.sleep(2)  # Check every 2 seconds

        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down chatbot...")
            bridge_process.terminate()
            bridge_process.wait()
            print("✅ Chatbot stopped successfully")

    except Exception as e:
        print(f"❌ Error starting chatbot: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    start_stable_chatbot()

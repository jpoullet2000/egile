#!/usr/bin/env python3
"""
Launcher script for the Egile E-commerce Chatbot.
This script starts the WebSocket bridge and provides instructions for using the chatbot.
"""

import subprocess
import sys
import webbrowser
import time
from pathlib import Path


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


def start_chatbot():
    """Start the chatbot system"""
    print("🚀 Starting Egile E-commerce Chatbot...")
    print("=" * 50)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Check if MCP server files exist
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

    # Start the bridge server
    print("\n🔗 Starting WebSocket bridge server...")
    try:
        # Start the bridge server in background
        bridge_process = subprocess.Popen(
            [sys.executable, str(bridge_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Wait a moment for server to start
        time.sleep(2)

        # Check if process is still running
        if bridge_process.poll() is not None:
            stdout, stderr = bridge_process.communicate()
            print("❌ Failed to start bridge server:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            sys.exit(1)

        print("✅ Bridge server started successfully")

        # Open the chatbot in browser
        html_path = html_file.absolute().as_uri()
        print("\n🌐 Opening chatbot in browser...")
        print(f"   URL: {html_path}")

        try:
            webbrowser.open(html_path)
            print("✅ Browser opened")
        except Exception as e:
            print(f"⚠️  Could not auto-open browser: {e}")
            print(f"   Please manually open: {html_path}")

        print("\n" + "=" * 50)
        print("🎉 Chatbot is ready!")
        print("=" * 50)
        print("\n📋 Usage Instructions:")
        print("1. The chatbot should now be open in your browser")
        print("2. If not, open the following file in your browser:")
        print(f"   {html_file}")
        print("\n💬 Try these commands in the chatbot:")
        print("• 'list products' - Show all products")
        print(
            "• 'create product \"Widget\" 29.99 WID-001 Electronics 50' - Create a product"
        )
        print("• 'list customers' - Show all customers")
        print("• 'help' - See all available commands")

        print("\n🛑 To stop the chatbot:")
        print("   Press Ctrl+C in this terminal")

        # Keep the script running and monitor the bridge process
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
    start_chatbot()

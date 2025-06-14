#!/usr/bin/env python3
"""
Quick test script to verify the basic chatbot setup.
Run this to check if all components work together.
"""

import subprocess
import sys
import time
from pathlib import Path


def test_basic_chatbot():
    """Test the basic chatbot system"""
    print("🔧 Testing Basic Chatbot Setup...")
    print("=" * 40)

    # Check if files exist
    script_dir = Path(__file__).parent
    bridge_file = script_dir / "chatbot" / "bridge.py"
    html_file = script_dir / "chatbot" / "index.html"

    print(f"Checking bridge file: {bridge_file}")
    if not bridge_file.exists():
        print("❌ Bridge file not found!")
        return False
    print("✅ Bridge file found")

    print(f"Checking HTML file: {html_file}")
    if not html_file.exists():
        print("❌ HTML file not found!")
        return False
    print("✅ HTML file found")

    # Test import
    try:
        sys.path.insert(0, str(script_dir))
        import importlib.util

        spec = importlib.util.find_spec("egile.agent")
        if spec is None:
            raise ImportError("egile.agent module not found")
        print("✅ EcommerceAgent import successful")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

    print("\n🚀 Starting bridge server...")
    try:
        # Start bridge server
        bridge_process = subprocess.Popen(
            [sys.executable, str(bridge_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Wait for startup
        time.sleep(2)

        # Check if running
        if bridge_process.poll() is not None:
            stdout, stderr = bridge_process.communicate()
            print("❌ Bridge server failed to start:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False

        print("✅ Bridge server started on port 8765")
        print(f"📄 HTML file: {html_file}")
        print("\n📋 Next steps:")
        print("1. Open the HTML file in your browser:")
        print(f"   chromium-browser {html_file}")
        print("2. Or use the launcher:")
        print("   python run_chatbot.py")
        print("\n⏹️  Press Ctrl+C to stop the test server")

        # Keep running until interrupted
        try:
            while bridge_process.poll() is None:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping test server...")
            bridge_process.terminate()
            bridge_process.wait()
            print("✅ Test completed")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    test_basic_chatbot()

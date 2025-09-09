#!/usr/bin/env python3
"""
HarmWatch System Startup Script
This script helps you start both the bridge server and the main application.
"""

import subprocess
import sys
import time
import os
import requests
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = ['streamlit', 'fastapi', 'uvicorn', 'websockets', 'requests', 'beautifulsoup4']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def start_bridge_server():
    """Start the bridge server in the background."""
    print("🚀 Starting bridge server...")
    
    # Change to app directory
    app_dir = Path(__file__).parent / "app"
    os.chdir(app_dir)
    
    try:
        # Start bridge server
        process = subprocess.Popen([
            sys.executable, "bridge.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for server to start
        time.sleep(3)
        
        # Check if server is running
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Bridge server started successfully on http://localhost:8000")
                return process
            else:
                print(f"❌ Bridge server returned status: {response.status_code}")
                process.terminate()
                return None
        except requests.exceptions.RequestException:
            print("❌ Bridge server failed to start")
            process.terminate()
            return None
            
    except Exception as e:
        print(f"❌ Error starting bridge server: {e}")
        return None

def start_streamlit_app():
    """Start the Streamlit application."""
    print("🌐 Starting Streamlit application...")
    
    # Change to app directory
    app_dir = Path(__file__).parent / "app"
    os.chdir(app_dir)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py"
        ])
    except KeyboardInterrupt:
        print("\n👋 Streamlit application stopped")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")

def main():
    """Main startup function."""
    print("🛡️ HarmWatch Enhanced System Startup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Start bridge server
    bridge_process = start_bridge_server()
    if not bridge_process:
        print("❌ Failed to start bridge server. Exiting.")
        sys.exit(1)
    
    try:
        # Start Streamlit app
        start_streamlit_app()
    finally:
        # Clean up bridge server
        if bridge_process:
            print("🛑 Stopping bridge server...")
            bridge_process.terminate()
            bridge_process.wait()
            print("✅ Bridge server stopped")

if __name__ == "__main__":
    main()

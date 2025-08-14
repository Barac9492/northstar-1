#!/usr/bin/env python3
"""
Quick Start Script for NorthStar AI
Automatically opens the application in your browser
"""

import subprocess
import time
import webbrowser
import requests
import os
import sys

def check_port_available(port):
    """Check if a port is available"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result != 0
    except:
        return True

def wait_for_service(url, timeout=30):
    """Wait for service to be ready"""
    for _ in range(timeout):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

def main():
    print("🚀 Starting NorthStar AI - Social Media Automation")
    print("=" * 60)
    
    # Kill any existing processes
    print("📋 Cleaning up existing processes...")
    subprocess.run(['pkill', '-f', 'streamlit'], capture_output=True)
    subprocess.run(['pkill', '-f', 'app.py'], capture_output=True)
    time.sleep(2)
    
    # Find available ports
    flask_port = 5001
    streamlit_port = 8501
    
    while not check_port_available(flask_port):
        flask_port += 1
    
    while not check_port_available(streamlit_port):
        streamlit_port += 1
    
    print(f"📡 Starting Flask API on port {flask_port}...")
    
    # Start Flask backend
    flask_env = os.environ.copy()
    flask_env['PORT'] = str(flask_port)
    flask_process = subprocess.Popen(
        [sys.executable, 'app.py'],
        env=flask_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for Flask to start
    flask_url = f"http://localhost:{flask_port}/health"
    if wait_for_service(flask_url):
        print(f"✅ Flask API ready at http://localhost:{flask_port}")
    else:
        print("❌ Flask API failed to start")
        return
    
    print(f"🎨 Starting Streamlit dashboard on port {streamlit_port}...")
    
    # Start Streamlit dashboard
    streamlit_env = os.environ.copy()
    streamlit_env['API_BASE_URL'] = f"http://localhost:{flask_port}"
    
    streamlit_process = subprocess.Popen(
        [sys.executable, '-m', 'streamlit', 'run', 'dashboard.py', 
         '--server.port', str(streamlit_port), '--server.headless', 'true'],
        env=streamlit_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for Streamlit to start
    streamlit_url = f"http://localhost:{streamlit_port}"
    if wait_for_service(streamlit_url):
        print(f"✅ Streamlit dashboard ready at {streamlit_url}")
    else:
        print("❌ Streamlit dashboard failed to start")
        return
    
    print("=" * 60)
    print("🎉 NorthStar AI is ready!")
    print(f"📊 Dashboard: http://localhost:{streamlit_port}")
    print(f"🔧 API: http://localhost:{flask_port}")
    print("")
    print("💡 Click 'Start Free Demo' to try the AI features")
    print("🔗 Opening dashboard in your browser...")
    print("=" * 60)
    
    # Open browser
    webbrowser.open(streamlit_url)
    
    try:
        # Keep processes running
        print("⌨️  Press Ctrl+C to stop all services")
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if flask_process.poll() is not None:
                print("❌ Flask process died")
                break
            if streamlit_process.poll() is not None:
                print("❌ Streamlit process died")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        flask_process.terminate()
        streamlit_process.terminate()
        
        # Wait for graceful shutdown
        time.sleep(2)
        
        # Force kill if needed
        try:
            flask_process.kill()
            streamlit_process.kill()
        except:
            pass
        
        print("✅ All services stopped")

if __name__ == "__main__":
    main()
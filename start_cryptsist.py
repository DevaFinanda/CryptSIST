#!/usr/bin/env python3
"""
CryptSIST Safe Startup Script
=============================
Startup script yang lebih aman dengan port management
"""

import sys
import time
import socket
import subprocess
from pathlib import Path

def check_port_available(port):
    """Check if port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('127.0.0.1', port))
            return result != 0  # Port available if connection fails
    except Exception:
        return True

def wait_for_port_free(port, timeout=30):
    """Wait for port to become available"""
    print(f"⏳ Waiting for port {port} to become available...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if check_port_available(port):
            print(f"✅ Port {port} is now available")
            return True
        time.sleep(1)
    
    print(f"❌ Timeout waiting for port {port}")
    return False

def kill_existing_processes():
    """Kill existing CryptSIST processes"""
    try:
        # Windows
        subprocess.run(['taskkill', '/F', '/IM', 'python.exe', '/FI', 'WINDOWTITLE eq *CryptSIST*'], 
                      capture_output=True, check=False)
        subprocess.run(['taskkill', '/F', '/IM', 'uvicorn.exe'], 
                      capture_output=True, check=False)
    except Exception as e:
        print(f"⚠️ Error killing processes: {e}")

def main():
    print("🚀 CryptSIST Safe Startup")
    print("=" * 40)
    
    # Kill existing processes
    print("🧹 Cleaning up existing processes...")
    kill_existing_processes()
    time.sleep(3)
    
    # Wait for port to be free
    if not wait_for_port_free(8000):
        print("❌ Unable to free port 8000. Please restart your computer.")
        sys.exit(1)
    
    # Start main launcher
    print("🚀 Starting CryptSIST...")
    try:
        subprocess.run([sys.executable, 'main.py'], cwd=Path(__file__).parent)
    except KeyboardInterrupt:
        print("\n👋 Shutdown requested by user")
    except Exception as e:
        print(f"❌ Error starting CryptSIST: {e}")

if __name__ == "__main__":
    main()

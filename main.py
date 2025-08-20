#!/usr/bin/env python3
"""
CryptSIST MT5 Integration Main Launcher
=======================================
Main entry point for MT5 integration system
"""

import os
import sys
import subprocess
import time
import signal
import socket
import psutil
from pathlib import Path

# Add current directory and subdirectories to path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / 'dependencies'))
sys.path.insert(0, str(current_dir / 'config'))

class MT5Launcher:
    def __init__(self):
        self.server_process = None
        self.bridge_process = None
        self.running = False
        self.server_port = 8000
        
    def check_port_available(self, port):
        """Check if port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return True
        except socket.error:
            return False
    
    def kill_processes_using_port(self, port):
        """Kill processes using specific port"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    if proc.info['connections']:
                        for conn in proc.info['connections']:
                            if conn.laddr.port == port:
                                print(f"🔫 Killing process {proc.info['pid']} ({proc.info['name']}) using port {port}")
                                proc.kill()
                                time.sleep(1)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"⚠️ Error killing processes: {e}")
    
    def cleanup_previous_instances(self):
        """Clean up any previous instances"""
        print("🧹 Cleaning up previous instances...")
        
        # Kill processes using our port
        if not self.check_port_available(self.server_port):
            print(f"⚠️ Port {self.server_port} is in use. Cleaning up...")
            self.kill_processes_using_port(self.server_port)
            time.sleep(2)
            
        # Double check
        if not self.check_port_available(self.server_port):
            print(f"❌ Unable to free port {self.server_port}. Please restart your computer or manually kill processes.")
            return False
            
        print("✅ Cleanup completed")
        return True
        
    def start_server(self):
        """Start MT5 server"""
        try:
            print("🚀 Starting MT5 Server...")
            server_script = current_dir / 'server' / 'mt5_server.py'
            
            if not server_script.exists():
                print(f"❌ Server script not found: {server_script}")
                return False
                
            self.server_process = subprocess.Popen([
                sys.executable, str(server_script)
            ], cwd=str(current_dir))
            
            print(f"✅ MT5 Server started (PID: {self.server_process.pid})")
            time.sleep(3)  # Wait for server to start
            return True
            
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def start_bridge(self):
        """Start MT5 bridge"""
        try:
            print("🌉 Starting MT5 Bridge...")
            bridge_script = current_dir / 'bridge' / 'mt5_bridge.py'
            
            if not bridge_script.exists():
                print(f"❌ Bridge script not found: {bridge_script}")
                return False
                
            self.bridge_process = subprocess.Popen([
                sys.executable, str(bridge_script)
            ], cwd=str(current_dir))
            
            print(f"✅ MT5 Bridge started (PID: {self.bridge_process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start bridge: {e}")
            return False
    
    def stop_all(self):
        """Stop all processes"""
        print("\n🛑 Stopping MT5 Integration...")
        
        if self.bridge_process:
            try:
                self.bridge_process.terminate()
                self.bridge_process.wait(timeout=5)
                print("✅ Bridge stopped")
            except:
                self.bridge_process.kill()
                print("⚠️ Bridge force killed")
        
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                print("✅ Server stopped")
            except:
                self.server_process.kill()
                print("⚠️ Server force killed")
        
        self.running = False
        print("👋 MT5 Integration stopped")
    
    def run(self):
        """Main run method"""
        print("🔷 CryptSIST MT5 Integration Launcher")
        print("=" * 50)
        
        # Cleanup previous instances first
        if not self.cleanup_previous_instances():
            return
        
        # Setup signal handlers
        def signal_handler(signum, frame):
            self.stop_all()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            # Start server first
            if not self.start_server():
                print("❌ Failed to start server. Exiting.")
                return
            
            # Start bridge
            if not self.start_bridge():
                print("❌ Failed to start bridge. Stopping server.")
                self.stop_all()
                return
            
            self.running = True
            print("\n✅ MT5 Integration running successfully!")
            print("📡 Server: http://127.0.0.1:8000")
            print("🌉 Bridge: Monitoring symbols")
            print("⏸️ Press Ctrl+C to stop")
            print()
            
            # Keep running
            while self.running:
                time.sleep(1)
                
                # Check if processes are still alive
                if self.server_process and self.server_process.poll() is not None:
                    print("⚠️ Server process died. Restarting...")
                    self.start_server()
                
                if self.bridge_process and self.bridge_process.poll() is not None:
                    print("⚠️ Bridge process died. Restarting...")
                    self.start_bridge()
            
        except KeyboardInterrupt:
            self.stop_all()
        except Exception as e:
            print(f"❌ Error in main loop: {e}")
            self.stop_all()

def main():
    """Main entry point"""
    launcher = MT5Launcher()
    launcher.run()

if __name__ == "__main__":
    main()

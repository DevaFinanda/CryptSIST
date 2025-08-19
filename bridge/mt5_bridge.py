#!/usr/bin/env python3
"""
CryptSIST MT5 Bridge - Real-Time Integration
Handles communication between CryptSIST server and MetaTrader 5
"""

import requests
import json
import time
import os
import csv
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MT5Bridge:
    def __init__(self):
        self.server_url = "http://127.0.0.1:8000"
        self.mt5_data_folder = self.get_mt5_data_folder()
        self.signals_file = os.path.join(self.mt5_data_folder, "cryptsist_signals.csv")
        self.connection_file = os.path.join(self.mt5_data_folder, "mt5_connection_status.txt")
        self.last_signal = None
        self.last_update = None
        
        logger.info("🌉 CryptSIST MT5 Bridge initialized")
        logger.info(f"📁 MT5 Data folder: {self.mt5_data_folder}")
        logger.info(f"📊 Signals file: {self.signals_file}")
        
        # Create data files
        self.setup_data_files()
        
    def get_mt5_data_folder(self):
        """Get MT5 data folder path"""
        possible_paths = [
            os.path.expanduser("~/AppData/Roaming/MetaQuotes/Terminal/Common/Files"),
            "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files",
            "C:/ProgramData/MetaQuotes/Terminal/Common/Files"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Fallback - create in current directory
        fallback_path = "./mt5_data"
        os.makedirs(fallback_path, exist_ok=True)
        logger.warning(f"⚠️ Using fallback data folder: {fallback_path}")
        return fallback_path
    
    def setup_data_files(self):
        """Setup data files for MT5 communication"""
        try:
            # Create signals CSV file
            if not os.path.exists(self.signals_file):
                with open(self.signals_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['timestamp', 'symbol', 'signal', 'confidence', 'price', 'sentiment', 'analysis'])
                logger.info("📄 Signals CSV file created")
            
            # Create connection status file
            with open(self.connection_file, 'w', encoding='utf-8') as f:
                f.write(f"CONNECTED|{datetime.now().isoformat()}|CryptSIST Bridge Running")
            logger.info("📄 Connection status file created")
            
        except Exception as e:
            logger.error(f"❌ Error setting up data files: {e}")
    
    def test_server_connection(self):
        """Test connection to CryptSIST server"""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ CryptSIST server connection successful")
                return True
            else:
                logger.error(f"❌ Server returned status code: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Cannot connect to CryptSIST server: {e}")
            return False
    
    def get_signal(self, symbol):
        """Get trading signal for a symbol"""
        try:
            response = requests.get(f"{self.server_url}/signal/{symbol}", timeout=3)
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"⚠️ Failed to get signal for {symbol}: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"❌ Error getting signal for {symbol}: {e}")
            return None
    
    def write_signal_to_file(self, symbol, signal_data):
        """Write signal data to CSV file for MT5 to read"""
        try:
            timestamp = datetime.now().isoformat()
            
            # Extract signal information
            signal_type = signal_data.get('signal', 'NONE')
            confidence = signal_data.get('confidence', 0.0)
            price = signal_data.get('price', 0.0)
            sentiment = signal_data.get('sentiment', 'NEUTRAL')
            analysis = signal_data.get('analysis', 'No analysis')
            
            # Quality control - only write meaningful signals
            if confidence < 0.55:
                logger.info(f"⚠️ Low confidence signal ignored: {symbol} {signal_type} ({confidence:.1%})")
                return
                
            if signal_type == "NONE":
                logger.info(f"🔄 Neutral signal for {symbol}, converting to HOLD")
                signal_type = "HOLD"
            
            # Write to CSV
            with open(self.signals_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, symbol, signal_type, confidence, price, sentiment, analysis])
            
            logger.info(f"📊 Signal written: {symbol} {signal_type} ({confidence:.1%}) at ${price:,.2f}")
            
        except Exception as e:
            logger.error(f"❌ Error writing signal to file: {e}")
    
    def update_connection_status(self, status):
        """Update connection status file"""
        try:
            with open(self.connection_file, 'w', encoding='utf-8') as f:
                f.write(f"{status}|{datetime.now().isoformat()}|CryptSIST Bridge")
        except Exception as e:
            logger.error(f"❌ Error updating connection status: {e}")
    
    def monitor_symbols(self, symbols=['BTCUSD', 'ETHUSD', 'LTCUSD'], interval=5):
        """Monitor symbols and update signals"""
        logger.info(f"🔍 Starting monitoring for symbols: {symbols}")
        logger.info(f"⏱️ Update interval: {interval} seconds")
        
        while True:
            try:
                # Test server connection
                if not self.test_server_connection():
                    self.update_connection_status("DISCONNECTED")
                    logger.warning("⚠️ Server disconnected, retrying in 10 seconds...")
                    time.sleep(10)
                    continue
                
                self.update_connection_status("CONNECTED")
                
                # Get signals for each symbol
                for symbol in symbols:
                    signal_data = self.get_signal(symbol)
                    if signal_data:
                        # Only write if signal changed significantly
                        current_signal = f"{symbol}_{signal_data.get('signal')}_{signal_data.get('confidence', 0):.1f}"
                        
                        # Check if signal actually changed (different type or confidence changed by >5%)
                        if (current_signal != self.last_signal or 
                            not hasattr(self, 'last_signal_time') or 
                            (time.time() - getattr(self, 'last_signal_time', 0)) > 30):  # Force update every 30 seconds
                            
                            self.write_signal_to_file(symbol, signal_data)
                            self.last_signal = current_signal
                            self.last_signal_time = time.time()
                
                # Wait for next update
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 Bridge stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                time.sleep(5)
    
    def start_real_time_mode(self, symbols=['BTCUSD'], interval=1):
        """Start real-time monitoring mode (1 second updates)"""
        logger.info("⚡ Starting REAL-TIME mode")
        logger.info(f"🎯 Symbols: {symbols}")
        logger.info(f"⏱️ Update interval: {interval} second(s)")
        
        self.monitor_symbols(symbols, interval)

def main():
    """Main function"""
    print("🌉 CryptSIST-MT5 Bridge")
    print("=" * 50)
    
    # Initialize bridge
    bridge = MT5Bridge()
    
    # Test connection
    if not bridge.test_server_connection():
        print("❌ Cannot connect to CryptSIST server")
        print("💡 Make sure the server is running: python mt5_server.py")
        input("Press Enter to exit...")
        return
    
    print("✅ Server connection established")
    print("🔄 Starting real-time monitoring...")
    print("⏸️ Press Ctrl+C to stop")
    print()
    
    try:
        # Start monitoring in real-time mode
        bridge.start_real_time_mode(['BTCUSD', 'ETHUSD'], interval=2)
    except KeyboardInterrupt:
        print("\n🛑 Bridge stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("👋 Goodbye!")

if __name__ == "__main__":
    main()

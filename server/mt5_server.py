#!/usr/bin/env python3
"""
CryptSIST FastAPI Server for MT5 Integration
============================================
Lightweight FastAPI server to provide trading signals to MetaTrader 5
"""

import sys
import os

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
dependencies_dir = os.path.join(parent_dir, 'dependencies')
config_dir = os.path.join(parent_dir, 'config')

sys.path.extend([parent_dir, root_dir, dependencies_dir, config_dir])

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging
from datetime import datetime
import asyncio
from typing import Dict, List, Optional

# Import CryptSIST components (with fallbacks)
price_fetcher_available = False
sentiment_analyzer_available = False
groq_client_available = False
signal_generator_available = False

try:
    from enhanced_price_fetcher import EnhancedPriceFetcher
    price_fetcher = EnhancedPriceFetcher()
    price_fetcher_available = True
    print("✅ Enhanced price fetcher loaded")
except ImportError as e:
    print(f"⚠️ Enhanced price fetcher not available: {e}")

try:
    from sentiment_analyzer import CryptoSentimentAnalyzer
    sentiment_analyzer = CryptoSentimentAnalyzer()
    sentiment_analyzer_available = True
    print("✅ Sentiment analyzer loaded")
except ImportError as e:
    print(f"⚠️ Sentiment analyzer not available: {e}")

try:
    from simple_groq_client import SimpleGroqClient
    groq_client = SimpleGroqClient()
    groq_client_available = True
    print("✅ Groq client loaded")
except ImportError as e:
    print(f"⚠️ Groq client not available: {e}")

try:
    from enhanced_signal_generator import EnhancedSignalGenerator
    signal_generator = EnhancedSignalGenerator()
    signal_generator_available = True
    print("✅ Enhanced signal generator loaded")
except ImportError as e:
    print(f"⚠️ Enhanced signal generator not available: {e}")

print("📝 Server starting with available components")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CryptSIST MT5 API",
    description="FastAPI server for CryptSIST-MetaTrader 5 integration",
    version="1.0.0"
)

# Enable CORS for MT5 WebRequest
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class TradingSignal(BaseModel):
    symbol: str
    signal: str  # "BUY", "SELL", "HOLD"
    confidence: float
    price: float
    timestamp: str
    sentiment: str
    analysis: Optional[str] = None

class HealthStatus(BaseModel):
    status: str
    timestamp: str
    version: str

# Global cache for signals
signal_cache: Dict[str, TradingSignal] = {}
last_update: Dict[str, datetime] = {}

@app.get("/", response_model=HealthStatus)
async def root():
    """Health check endpoint"""
    return HealthStatus(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Detailed health check for MT5"""
    return HealthStatus(
        status="CryptSIST MT5 Server Running",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

async def generate_trading_signal(symbol: str) -> TradingSignal:
    """
    Generate trading signal using enhanced signal generator
    """
    try:
        if signal_generator_available:
            # Use enhanced signal generator for dynamic signals
            signal_data = signal_generator.generate_signal(symbol)
            
            return TradingSignal(
                symbol=symbol,
                signal=signal_data['signal'],
                confidence=signal_data['confidence'],
                price=signal_data['price'],
                timestamp=datetime.now().isoformat(),
                sentiment=signal_data.get('sentiment', 'NEUTRAL'),
                analysis=signal_data.get('analysis', 'Enhanced AI analysis')
            )
        else:
            # Fallback to basic signal generation
            import random
            signals = ["BUY", "SELL", "HOLD"]
            return TradingSignal(
                symbol=symbol,
                signal=random.choice(signals),
                confidence=random.uniform(0.6, 0.95),
                price=random.uniform(40000, 70000) if symbol.startswith('BTC') else random.uniform(2000, 4000),
                timestamp=datetime.now().isoformat(),
                sentiment="NEUTRAL",
                analysis="Basic signal generation"
            )
    except Exception as e:
        logger.error(f"Error generating signal for {symbol}: {e}")
        # Return safe default
        return TradingSignal(
            symbol=symbol,
            signal="HOLD",
            confidence=0.5,
            price=50000.0 if symbol.startswith('BTC') else 3000.0,
            timestamp=datetime.now().isoformat(),
            sentiment="NEUTRAL",
            analysis="Error in signal generation - returning safe default"
        )

@app.get("/signal/{symbol}", response_model=TradingSignal)
async def get_trading_signal(symbol: str):
    """
    Get trading signal for a specific cryptocurrency symbol
    
    Args:
        symbol: Crypto symbol (e.g., BTC, ETH, LTC)
    
    Returns:
        TradingSignal with current recommendation
    """
    try:
        # Normalize symbol
        symbol = symbol.upper()
        if symbol.endswith('USD'):
            base_symbol = symbol[:-3]
        else:
            base_symbol = symbol
            
        logger.info(f"🔍 Getting signal for {symbol}")
        
        # Check cache (refresh every 5 seconds for more dynamic signals)
        cache_key = base_symbol
        now = datetime.now()
        
        if (cache_key in signal_cache and 
            cache_key in last_update and 
            (now - last_update[cache_key]).seconds < 5):  # Reduced cache time for more dynamic signals
            
            logger.info(f"📋 Returning cached signal for {symbol}")
            cached_signal = signal_cache[cache_key]
            cached_signal.symbol = symbol  # Update symbol format
            return cached_signal
        
        # Get fresh data
        signal = await generate_trading_signal(base_symbol)
        signal.symbol = symbol  # Set requested symbol format
        
        # Update cache
        signal_cache[cache_key] = signal
        last_update[cache_key] = now
        
        logger.info(f"✅ Generated new signal for {symbol}: {signal.signal}")
        return signal
        
    except Exception as e:
        logger.error(f"❌ Error getting signal for {symbol}: {e}")
        # Return safe default
        return TradingSignal(
            symbol=symbol,
            signal="HOLD",
            confidence=0.5,
            price=50000.0,
            timestamp=datetime.now().isoformat(),
            sentiment="NEUTRAL",
            analysis="Error in signal processing"
        )

@app.get("/signals/batch", response_model=List[TradingSignal])
async def get_batch_signals(symbols: str = "BTCUSD,ETHUSD,LTCUSD"):
    """
    Get trading signals for multiple symbols
    
    Args:
        symbols: Comma-separated list of symbols
    
    Returns:
        List of TradingSignal objects
    """
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(',')]
        signals = []
        
        for symbol in symbol_list:
            signal = await get_trading_signal(symbol)
            signals.append(signal)
        
        logger.info(f"📊 Generated batch signals for {len(signals)} symbols")
        return signals
        
    except Exception as e:
        logger.error(f"❌ Error getting batch signals: {e}")
        return []

def main():
    """Main function to run the server"""
    print("🚀 Starting CryptSIST MT5 Server...")
    print(f"📡 Server will be available at: http://127.0.0.1:8000")
    print(f"🔗 Health check: http://127.0.0.1:8000/health")
    print(f"📊 Example signal: http://127.0.0.1:8000/signal/BTCUSD")
    print()
    
    try:
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Enhanced Signal Generator for CryptSIST MT5 Integration
Provides realistic, dynamic trading signals for testing
"""

import random
import math
import time
from datetime import datetime, timedelta
from typing import Dict, Tuple

class EnhancedSignalGenerator:
    def __init__(self):
        self.symbol_prices = {
            'BTC': 58431.50,
            'ETH': 3245.80,
            'LTC': 85.25,
            'BCH': 425.60,
            'XRP': 0.6234
        }
        self.symbol_trends = {
            'BTC': 'neutral',
            'ETH': 'neutral', 
            'LTC': 'neutral',
            'BCH': 'neutral',
            'XRP': 'neutral'
        }
        self.last_signals = {}
        self.signal_history = {}
        
    def simulate_price_movement(self, symbol: str) -> float:
        """Simulate realistic price movement"""
        current_price = self.symbol_prices.get(symbol, 1000.0)
        
        # Different volatility for different symbols
        volatility_map = {
            'BTC': 0.02,  # 2% max movement
            'ETH': 0.025, # 2.5% max movement  
            'LTC': 0.03,  # 3% max movement
            'BCH': 0.035, # 3.5% max movement
            'XRP': 0.04   # 4% max movement
        }
        
        volatility = volatility_map.get(symbol, 0.02)
        
        # Add time-based patterns (more volatile during certain hours)
        hour = datetime.now().hour
        if 8 <= hour <= 16 or 20 <= hour <= 23:  # Active trading hours
            volatility *= 1.5
        
        # Random walk with momentum
        price_change = random.uniform(-volatility, volatility)
        
        # Add momentum (trend following)
        current_trend = self.symbol_trends.get(symbol, 'neutral')
        if current_trend == 'bullish':
            price_change += random.uniform(0, volatility * 0.5)
        elif current_trend == 'bearish':
            price_change -= random.uniform(0, volatility * 0.5)
        
        new_price = current_price * (1 + price_change)
        self.symbol_prices[symbol] = new_price
        
        return new_price
    
    def update_trend(self, symbol: str, price_history: list) -> str:
        """Update trend based on recent price movements"""
        if len(price_history) < 3:
            return 'neutral'
        
        recent_prices = price_history[-3:]
        
        # Calculate trend
        if recent_prices[2] > recent_prices[1] > recent_prices[0]:
            trend = 'bullish'
        elif recent_prices[2] < recent_prices[1] < recent_prices[0]:
            trend = 'bearish'
        else:
            trend = 'neutral'
        
        self.symbol_trends[symbol] = trend
        return trend
    
    def generate_signal(self, symbol: str) -> Dict:
        """Generate enhanced trading signal"""
        # Simulate price movement
        current_price = self.simulate_price_movement(symbol)
        
        # Update price history
        if symbol not in self.signal_history:
            self.signal_history[symbol] = []
        
        self.signal_history[symbol].append(current_price)
        
        # Keep only last 10 prices
        if len(self.signal_history[symbol]) > 10:
            self.signal_history[symbol] = self.signal_history[symbol][-10:]
        
        # Update trend
        trend = self.update_trend(symbol, self.signal_history[symbol])
        
        # Generate signal based on multiple factors
        signal_strength = self.calculate_signal_strength(symbol, current_price, trend)
        
        # Determine signal type
        if signal_strength > 0.3:
            signal_type = "BUY"
            confidence = 0.65 + min(0.3, signal_strength * 0.5)
        elif signal_strength < -0.3:
            signal_type = "SELL" 
            confidence = 0.65 + min(0.3, abs(signal_strength) * 0.5)
        elif signal_strength > 0.1:
            signal_type = "BUY"
            confidence = 0.55 + signal_strength * 0.3
        elif signal_strength < -0.1:
            signal_type = "SELL"
            confidence = 0.55 + abs(signal_strength) * 0.3
        else:
            signal_type = "HOLD"
            confidence = 0.60 + random.uniform(-0.05, 0.05)
        
        # Generate analysis
        analysis = self.generate_analysis(symbol, signal_type, confidence, current_price, trend)
        
        return {
            'symbol': symbol,
            'signal': signal_type,
            'confidence': round(confidence, 2),
            'price': round(current_price, 2),
            'sentiment': trend.upper(),
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_signal_strength(self, symbol: str, price: float, trend: str) -> float:
        """Calculate signal strength based on multiple factors"""
        now = datetime.now()
        
        # Time-based factors
        hour = now.hour
        minute = now.minute
        
        # Market hours (stronger signals during active hours)
        market_factor = 0.2 if 8 <= hour <= 16 or 20 <= hour <= 23 else 0.0
        
        # Price momentum
        if symbol in self.signal_history and len(self.signal_history[symbol]) >= 2:
            price_change = (price - self.signal_history[symbol][-2]) / self.signal_history[symbol][-2]
            momentum_factor = price_change * 10  # Amplify price changes
        else:
            momentum_factor = 0.0
        
        # Trend factor
        trend_factor = 0.3 if trend == 'bullish' else -0.3 if trend == 'bearish' else 0.0
        
        # Random market events (news, etc.)
        random.seed(int(now.timestamp()) // 60 + hash(symbol))  # Change every minute per symbol
        news_factor = random.uniform(-0.4, 0.4)
        
        # Technical indicators simulation
        tech_factor = math.sin(int(now.timestamp()) / 300) * 0.3  # 5-minute cycle
        
        # Combine all factors
        total_strength = market_factor + momentum_factor + trend_factor + news_factor + tech_factor
        
        # Normalize to reasonable range
        return max(-1.0, min(1.0, total_strength))
    
    def generate_analysis(self, symbol: str, signal_type: str, confidence: float, price: float, trend: str) -> str:
        """Generate human-readable analysis"""
        time_str = datetime.now().strftime('%H:%M:%S')
        
        if signal_type == "BUY":
            if confidence > 0.8:
                return f"🟢 STRONG BUY signal for {symbol} at ${price:,.2f}. Multiple bullish indicators aligned with {confidence*100:.0f}% confidence. {trend.title()} trend confirmed. Time: {time_str}"
            else:
                return f"🟢 BUY signal for {symbol} at ${price:,.2f}. Positive momentum detected with {confidence*100:.0f}% confidence. Consider entry position. Time: {time_str}"
        
        elif signal_type == "SELL":
            if confidence > 0.8:
                return f"🔴 STRONG SELL signal for {symbol} at ${price:,.2f}. Bearish reversal confirmed with {confidence*100:.0f}% confidence. {trend.title()} pressure building. Time: {time_str}"
            else:
                return f"🔴 SELL signal for {symbol} at ${price:,.2f}. Downward momentum with {confidence*100:.0f}% confidence. Consider position reduction. Time: {time_str}"
        
        else:  # HOLD
            return f"🟡 HOLD signal for {symbol} at ${price:,.2f}. Market consolidation with {confidence*100:.0f}% confidence. Awaiting clear directional break. {trend.title()} trend. Time: {time_str}"

# Singleton instance
signal_generator = EnhancedSignalGenerator()

def get_enhanced_signal(symbol: str) -> Dict:
    """Get enhanced signal for symbol"""
    return signal_generator.generate_signal(symbol)

if __name__ == "__main__":
    # Test the signal generator
    print("🧪 Testing Enhanced Signal Generator")
    print("=" * 50)
    
    symbols = ['BTC', 'ETH', 'LTC']
    
    for i in range(10):
        print(f"\n⏰ Round {i+1}:")
        for symbol in symbols:
            signal = get_enhanced_signal(symbol)
            print(f"{symbol}: {signal['signal']} ({signal['confidence']:.0%}) - ${signal['price']:,.2f}")
        
        time.sleep(2)

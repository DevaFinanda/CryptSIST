"""
API Keys Configuration for CryptoAgents
========================================

File ini berisi konfigurasi API keys yang tersedia untuk sistem CryptoAgents.
Jangan commit file ini ke repository public untuk keamanan.

API Keys yang Tersedia:
"""

import os
from typing import Dict, List

# ============================================================================
# API KEYS CONFIGURATION
# ============================================================================

# 1. CoinDesk API
# Fungsi: Data harga cryptocurrency, market data
# Dokumentasi: https://www.coindesk.com/coindesk-api
COINDESK_API_KEY = "6d12bba6674c2b143630614d947500ccb0751d1c5552f09e42ac2748e9a5eb96"

# 2. Alpha Vantage API  
# Fungsi: Financial data, forex, cryptocurrency, stocks
# Dokumentasi: https://www.alphavantage.co/documentation/
# Rate limit: 5 calls per minute, 500 calls per day (free tier)
ALPHA_VANTAGE_API_KEY = "BRIAVW9B5B39DNVT"

# 3. NewsAPI
# Fungsi: Global news articles dari berbagai sumber
# Dokumentasi: https://newsapi.org/docs
# Rate limit: 1000 requests per day (free tier)
NEWS_API_KEY = "8185e9b282f64bcbadf6bb508608da65"

# 4. CryptoPanic API
# Fungsi: Cryptocurrency news aggregator, sentiment analysis
# Dokumentasi: https://cryptopanic.com/developers/api/
# Rate limit: 1000 requests per day (free tier)
CRYPTOPANIC_API_KEY = "4032624c630963750e5e52e47190b56580d4039c"

# 5. Binance API Key
# Fungsi: Real-time cryptocurrency trading data, market depth, price tickers
# Dokumentasi: https://binance-docs.github.io/apidocs/spot/en/
# Note: This is API Key only (for public data), no secret key needed for market data
BINANCE_API_KEY = "DPtNEKd5SsQSepWAq5j5N5C1AmXqFzOyPdV6wwyxio9UewHgcHGUIcSaX0ChqnUs"

# 6. CoinMarketCap API Key
# Fungsi: Real-time cryptocurrency data, market cap, rankings, historical data
# Dokumentasi: https://coinmarketcap.com/api/documentation/v1/
# Rate limit: 333 calls per day (free tier), professional features available
COINMARKETCAP_API_KEY = "5eb3dd16-b5f6-4d49-807a-2847fba9a0e8"

# ============================================================================
# API ENDPOINTS AND CONFIGURATIONS
# ============================================================================

API_CONFIGURATIONS = {
    "coindesk": {
        "api_key": COINDESK_API_KEY,
        "base_url": "https://api.coindesk.com/v1",
        "description": "CoinDesk API untuk data harga Bitcoin dan market data",
        "features": [
            "Real-time Bitcoin price",
            "Historical price data", 
            "Market trends",
            "Price index data"
        ],
        "rate_limit": "No specific limit mentioned",
        "free_tier": True
    },
    
    "alpha_vantage": {
        "api_key": ALPHA_VANTAGE_API_KEY,
        "base_url": "https://www.alphavantage.co/query",
        "description": "Alpha Vantage untuk data finansial dan cryptocurrency",
        "features": [
            "Daily/Weekly/Monthly crypto data",
            "Intraday data",
            "Technical indicators",
            "Forex data",
            "Stock market data"
        ],
        "rate_limit": "5 calls/minute, 500 calls/day",
        "free_tier": True
    },
    
    "newsapi": {
        "api_key": NEWS_API_KEY,
        "base_url": "https://newsapi.org/v2",
        "description": "NewsAPI untuk berita global dan cryptocurrency",
        "features": [
            "Everything endpoint (search)",
            "Top headlines",
            "Sources management", 
            "Multi-language support",
            "Date filtering"
        ],
        "rate_limit": "1000 requests/day",
        "free_tier": True
    },
    
    "cryptopanic": {
        "api_key": CRYPTOPANIC_API_KEY,
        "base_url": "https://cryptopanic.com/api/v1",
        "description": "CryptoPanic untuk berita cryptocurrency dan sentiment",
        "features": [
            "Crypto-specific news",
            "Sentiment analysis",
            "Social media posts",
            "Reddit/Twitter integration",
            "Currency filtering",
            "News categorization"
        ],
        "rate_limit": "1000 requests/day",
        "free_tier": True
    },
    
    "binance": {
        "api_key": BINANCE_API_KEY,
        "base_url": "https://api.binance.com/api/v3",
        "description": "Binance API untuk data market real-time cryptocurrency",
        "features": [
            "Real-time price tickers",
            "24hr price change statistics", 
            "Market depth/order book",
            "Recent trades",
            "Historical klines/candlestick",
            "Exchange information",
            "Symbol price ticker"
        ],
        "rate_limit": "1200 requests/minute for most endpoints",
        "free_tier": True,
        "note": "Public data only - no trading functionality"
    },
    
    "coinmarketcap": {
        "api_key": COINMARKETCAP_API_KEY,
        "base_url": "https://pro-api.coinmarketcap.com/v1",
        "description": "CoinMarketCap API untuk data market cap dan ranking cryptocurrency",
        "features": [
            "Real-time cryptocurrency prices",
            "Market capitalization data",
            "Volume data",
            "Cryptocurrency rankings",
            "Historical data",
            "Metadata",
            "Global market metrics"
        ],
        "rate_limit": "333 calls/day (free tier)",
        "free_tier": True,
        "note": "Professional market data with high accuracy"
    }
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_api_key(service_name: str) -> str:
    """
    Mendapatkan API key untuk service tertentu
    
    Args:
        service_name (str): Nama service ('coindesk', 'alpha_vantage', 'newsapi', 'cryptopanic')
    
    Returns:
        str: API key atau None jika tidak ditemukan
    """
    config = API_CONFIGURATIONS.get(service_name)
    return config.get('api_key') if config else None

def get_base_url(service_name: str) -> str:
    """
    Mendapatkan base URL untuk service tertentu
    
    Args:
        service_name (str): Nama service
    
    Returns:
        str: Base URL atau None jika tidak ditemukan
    """
    config = API_CONFIGURATIONS.get(service_name)
    return config.get('base_url') if config else None

def list_available_apis() -> List[str]:
    """
    Mendapatkan daftar API yang tersedia
    
    Returns:
        List[str]: Daftar nama API yang tersedia
    """
    return list(API_CONFIGURATIONS.keys())

def get_api_info(service_name: str) -> Dict:
    """
    Mendapatkan informasi lengkap tentang API tertentu
    
    Args:
        service_name (str): Nama service
    
    Returns:
        Dict: Informasi lengkap API atau None jika tidak ditemukan
    """
    return API_CONFIGURATIONS.get(service_name)

def check_api_availability() -> Dict[str, bool]:
    """
    Mengecek ketersediaan semua API keys
    
    Returns:
        Dict[str, bool]: Status ketersediaan masing-masing API
    """
    availability = {}
    for service_name, config in API_CONFIGURATIONS.items():
        api_key = config.get('api_key')
        availability[service_name] = bool(api_key and api_key.strip())
    
    return availability

# ============================================================================
# ENVIRONMENT VARIABLES SETUP
# ============================================================================

def setup_environment_variables():
    """
    Setup environment variables untuk API keys
    Berguna jika aplikasi lain membutuhkan environment variables
    """
    os.environ['COINDESK_API_KEY'] = COINDESK_API_KEY
    os.environ['ALPHA_VANTAGE_API_KEY'] = ALPHA_VANTAGE_API_KEY
    os.environ['NEWS_API_KEY'] = NEWS_API_KEY
    os.environ['CRYPTOPANIC_API_KEY'] = CRYPTOPANIC_API_KEY
    os.environ['BINANCE_API_KEY'] = BINANCE_API_KEY
    
    print("✅ Environment variables telah di-setup")

# ============================================================================
# TESTING FUNCTIONS
# ============================================================================

def test_api_keys():
    """
    Test sederhana untuk memastikan API keys tersedia
    """
    print("🔑 Testing API Keys Availability...")
    print("=" * 50)
    
    availability = check_api_availability()
    
    for service_name, is_available in availability.items():
        config = API_CONFIGURATIONS[service_name]
        status = "✅ Available" if is_available else "❌ Missing"
        print(f"{service_name.upper():15} : {status}")
        print(f"                Description: {config['description']}")
        print(f"                Rate Limit : {config['rate_limit']}")
        print("-" * 50)
    
    available_count = sum(availability.values())
    total_count = len(availability)
    
    print(f"\n📊 Summary: {available_count}/{total_count} API keys available")
    
    if available_count == total_count:
        print("🎉 Semua API keys tersedia! Sistem siap untuk analisis lengkap.")
    elif available_count > 0:
        print("⚠️  Beberapa API keys tersedia. Sistem dapat berjalan dengan fitur terbatas.")
    else:
        print("❌ Tidak ada API keys yang tersedia. Sistem akan menggunakan data simulasi.")
    
    return availability

# ============================================================================
# USAGE RECOMMENDATIONS
# ============================================================================

"""
REKOMENDASI PENGGUNAAN API:

1. UNTUK DATA HARGA:
   - Binance: Real-time data dengan akurasi tinggi, rate limit generous (PRIORITY)
   - CoinDesk: Bitcoin price data (real-time & historical)
   - Alpha Vantage: Multi-crypto data dengan technical indicators

2. UNTUK BERITA & SENTIMENT:
   - NewsAPI: Berita global, search flexibility tinggi
   - CryptoPanic: Berita crypto-specific, built-in sentiment

3. KOMBINASI OPTIMAL:
   - Primary price data: Binance (real-time, accurate, high rate limit)
   - Secondary price data: Alpha Vantage (lebih comprehensive untuk analysis)
   - Backup price data: CoinDesk (khusus Bitcoin)
   - Primary news: CryptoPanic (crypto-focused)
   - Secondary news: NewsAPI (broader coverage)

4. RATE LIMITING STRATEGY:
   - Binance: 1200 requests/minute (sangat generous untuk real-time)
   - Alpha Vantage: Cache data karena limit ketat (5/minute)
   - NewsAPI: Batch requests untuk efisiensi
   - CryptoPanic: Real-time updates dengan reasonable limit
   - CoinDesk: Real-time karena tidak ada limit strict

5. DATA QUALITY:
   - Highest: Binance (exchange-grade real-time data)
   - Financial grade: Alpha Vantage (comprehensive analysis)
   - Good: CoinDesk (industry standard)
   - Excellent for news: CryptoPanic (crypto-specific)
   - Broad coverage: NewsAPI (global sources)

6. AKURASI TRADING:
   - Binance API memberikan data paling akurat untuk trading decisions
   - Real-time price, volume, dan market depth
   - Mendukung semua major cryptocurrencies
"""

if __name__ == "__main__":
    # Test API keys saat file dijalankan langsung
    test_api_keys()
    
    # Setup environment variables
    setup_environment_variables()
    
    print("\n🔧 API configuration loaded successfully!")
    print("📝 File ini berisi semua API keys yang tersedia untuk CryptoAgents.")
    print("🔒 JANGAN commit file ini ke repository public!")

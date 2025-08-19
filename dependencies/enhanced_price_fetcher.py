"""
Enhanced Price Fetcher with Real API Keys
Menggunakan CoinDesk API dan Alpha Vantage API untuk data harga real-time
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time
import logging

# Import API keys
from api_keys_config import (
    COINDESK_API_KEY, 
    ALPHA_VANTAGE_API_KEY,
    BINANCE_API_KEY,
    COINMARKETCAP_API_KEY,
    get_api_key,
    get_base_url
)

class EnhancedPriceFetcher:
    def __init__(self):
        self.coindesk_key = "6d12bba6674c2b143630614d947500ccb0751d1c5552f09e42ac2748e9a5eb96"
        self.alpha_vantage_key = "BRIAVW9B5B39DNVT"
        self.binance_key = "DPtNEKd5SsQSepWAq5j5N5C1AmXqFzOyPdV6wwyxio9UewHgcHGUIcSaX0ChqnUs"
        self.coinmarketcap_key = "4032624c630963750e5e52e47190b56580d4039c"
        self.coindesk_base = "https://api.coindesk.com/v1"
        self.alpha_vantage_base = "https://www.alphavantage.co/query"
        self.binance_base = "https://api.binance.com/api/v3"
        self.coinmarketcap_base = "https://pro-api.coinmarketcap.com/v1"
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Cache untuk menghindari rate limiting
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
        
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache:
            return False
        
        cache_time = self.cache[key].get('timestamp', 0)
        return time.time() - cache_time < self.cache_duration
    
    def _cache_data(self, key: str, data: Dict) -> None:
        """Cache data with timestamp"""
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def _get_cached_data(self, key: str) -> Optional[Dict]:
        """Get cached data if valid"""
        if self._is_cache_valid(key):
            return self.cache[key]['data']
        return None

    def get_coindesk_bitcoin_price(self) -> Dict[str, Any]:
        """
        Get Bitcoin price from CoinDesk API - dengan fallback handling
        """
        cache_key = "coindesk_btc"
        cached = self._get_cached_data(cache_key)
        if cached:
            return cached
            
        try:
            # CoinDesk Bitcoin Price Index - use working endpoint
            url = "https://api.coindesk.com/v1/bpi/currentprice.json"
            
            # Add headers to mimic browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract price information
            usd_data = data['bpi']['USD']
            
            # Parse price string and remove commas
            price_str = usd_data['rate'].replace(',', '').replace('$', '')
            current_price = float(price_str)
            
            result = {
                'symbol': 'BTC',
                'current_price': current_price,
                'currency': 'USD',
                'last_updated': data['time']['updated'],
                'source': 'CoinDesk',
                'api_source': 'coindesk',
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'raw_data': data
            }
            
            # Cache the result
            self._cache_data(cache_key, result)
            
            self.logger.info(f"✅ CoinDesk: BTC price fetched successfully: ${result['current_price']:,.2f}")
            return result
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error fetching CoinDesk data: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'source': 'CoinDesk',
                'api_source': 'coindesk'
            }
        except Exception as e:
            error_msg = f"Error processing CoinDesk data: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'source': 'CoinDesk',
                'api_source': 'coindesk'
            }

    def get_alpha_vantage_crypto_data(self, symbol: str, market: str = "USD") -> Dict[str, Any]:
        """
        Get cryptocurrency data from Alpha Vantage API - dengan handling yang lebih robust
        """
        cache_key = f"alpha_vantage_{symbol}_{market}"
        cached = self._get_cached_data(cache_key)
        if cached:
            return cached
            
        try:
            if not self.alpha_vantage_key:
                return {
                    'success': False,
                    'error': 'Alpha Vantage API key not available',
                    'source': 'Alpha Vantage'
                }
            
            # Use CURRENCY_EXCHANGE_RATE for real-time data - more reliable
            params = {
                'function': 'CURRENCY_EXCHANGE_RATE',
                'from_currency': symbol,
                'to_currency': 'USD',
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(self.alpha_vantage_base, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if 'Error Message' in data:
                return {
                    'success': False,
                    'error': data['Error Message'],
                    'source': 'Alpha Vantage',
                    'api_source': 'alpha_vantage'
                }
            
            if 'Note' in data:
                return {
                    'success': False,
                    'error': 'API rate limit exceeded. Please try again later.',
                    'source': 'Alpha Vantage',
                    'api_source': 'alpha_vantage'
                }
            
            # Extract exchange rate data
            if 'Realtime Currency Exchange Rate' in data:
                exchange_data = data['Realtime Currency Exchange Rate']
                
                current_price = float(exchange_data['5. Exchange Rate'])
                last_refreshed = exchange_data['6. Last Refreshed']
                
                # For change calculation, we'll use a simple simulation
                # In production, you might want to store previous values
                price_change_24h = 2.5  # Default placeholder
                
                result = {
                    'symbol': symbol,
                    'current_price': current_price,
                    'price_change_24h': price_change_24h,
                    'last_updated': last_refreshed,
                    'currency': market,
                    'source': 'Alpha Vantage',
                    'api_source': 'alpha_vantage',
                    'success': True,
                    'timestamp': datetime.now().isoformat(),
                    'metadata': exchange_data
                }
                
                # Cache the result
                self._cache_data(cache_key, result)
                
                self.logger.info(f"✅ Alpha Vantage: {symbol} data fetched successfully: ${result['current_price']:,.2f}")
                return result
            
            else:
                return {
                    'success': False,
                    'error': 'No exchange rate data found',
                    'source': 'Alpha Vantage',
                    'api_source': 'alpha_vantage'
                }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error fetching Alpha Vantage data: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'source': 'Alpha Vantage',
                'api_source': 'alpha_vantage'
            }
        except Exception as e:
            error_msg = f"Error processing Alpha Vantage data: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'source': 'Alpha Vantage',
                'api_source': 'alpha_vantage'
            }

    def get_binance_crypto_data(self, symbol: str, market: str = "USDT") -> Dict[str, Any]:
        """
        Get cryptocurrency data from Binance API - PRIORITY source for real-time accuracy
        """
        cache_key = f"binance_{symbol}_{market}"
        cached = self._get_cached_data(cache_key)
        if cached:
            return cached
            
        try:
            if not self.binance_key:
                return {
                    'success': False,
                    'error': 'Binance API key not available',
                    'source': 'Binance'
                }
            
            # Construct the trading pair symbol
            trading_pair = f"{symbol.upper()}{market.upper()}"
            
            # Get 24hr ticker statistics
            params = {
                'symbol': trading_pair
            }
            
            headers = {
                'X-MBX-APIKEY': self.binance_key
            }
            
            response = requests.get(
                f"{self.binance_base}/ticker/24hr",
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract price information
                current_price = float(data.get('lastPrice', 0))
                price_change_24h = float(data.get('priceChangePercent', 0))
                volume_24h = float(data.get('volume', 0))
                high_24h = float(data.get('highPrice', 0))
                low_24h = float(data.get('lowPrice', 0))
                
                result = {
                    'success': True,
                    'current_price': current_price,
                    'price_change_24h': price_change_24h,
                    'volume_24h': volume_24h,
                    'high_24h': high_24h,
                    'low_24h': low_24h,
                    'market_cap': None,  # Will be enriched from CoinGecko
                    'market_cap_rank': None,  # Will be enriched from CoinGecko
                    'source': 'Binance',
                    'api_source': 'binance',
                    'symbol': symbol,
                    'trading_pair': trading_pair,
                    'last_updated': datetime.now().isoformat(),
                    'raw_data': data,
                    'needs_market_cap_enrichment': True
                }
                
                # Cache the result
                self._cache_data(cache_key, result)
                
                self.logger.info(f"✅ Binance: {trading_pair} data fetched successfully: ${current_price:,.8f}")
                return result
                
            else:
                error_msg = f"Binance API error: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'source': 'Binance',
                    'api_source': 'binance'
                }
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error fetching Binance data: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'source': 'Binance',
                'api_source': 'binance'
            }
        except Exception as e:
            error_msg = f"Error processing Binance data: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'source': 'Binance',
                'api_source': 'binance'
            }

    def get_binance_multiple_tickers(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Get price data for multiple symbols from Binance API
        """
        try:
            if not self.binance_key:
                return {
                    'success': False,
                    'error': 'Binance API key not available',
                    'source': 'Binance'
                }
            
            headers = {
                'X-MBX-APIKEY': self.binance_key
            }
            
            # Get all price tickers
            response = requests.get(
                f"{self.binance_base}/ticker/price",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                all_tickers = response.json()
                
                # Filter for requested symbols
                filtered_data = {}
                for symbol in symbols:
                    trading_pairs = [f"{symbol.upper()}USDT", f"{symbol.upper()}BUSD", f"{symbol.upper()}BTC"]
                    
                    for ticker in all_tickers:
                        if ticker['symbol'] in trading_pairs:
                            filtered_data[symbol] = {
                                'symbol': ticker['symbol'],
                                'price': float(ticker['price']),
                                'source': 'Binance'
                            }
                            break
                
                result = {
                    'success': True,
                    'data': filtered_data,
                    'source': 'Binance',
                    'api_source': 'binance',
                    'last_updated': datetime.now().isoformat(),
                    'total_symbols': len(filtered_data)
                }
                
                self.logger.info(f"✅ Binance: Multi-ticker data fetched for {len(filtered_data)} symbols")
                return result
                
            else:
                error_msg = f"Binance multi-ticker API error: {response.status_code}"
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'source': 'Binance',
                    'api_source': 'binance'
                }
                
        except Exception as e:
            error_msg = f"Error fetching Binance multi-ticker data: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'source': 'Binance',
                'api_source': 'binance'
            }

    def get_coinmarketcap_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get cryptocurrency data from CoinMarketCap API (includes market cap, price, volume)
        """
        cache_key = f"coinmarketcap_{symbol}"
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            # CoinMarketCap API endpoint untuk quotes
            url = f"{self.coinmarketcap_base}/cryptocurrency/quotes/latest"
            
            headers = {
                'Accepts': 'application/json',
                'X-CMC_PRO_API_KEY': self.coinmarketcap_key,
            }
            
            params = {
                'symbol': symbol.upper(),
                'convert': 'USD'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data and symbol.upper() in data['data']:
                    coin_data = data['data'][symbol.upper()]
                    quote_data = coin_data['quote']['USD']
                    
                    result = {
                        'success': True,
                        'symbol': symbol.upper(),
                        'name': coin_data['name'],
                        'current_price': quote_data['price'],
                        'market_cap': quote_data['market_cap'],
                        'market_cap_rank': coin_data['cmc_rank'],
                        'volume_24h': quote_data['volume_24h'],
                        'price_change_24h': quote_data['percent_change_24h'],
                        'price_change_7d': quote_data['percent_change_7d'],
                        'circulating_supply': coin_data['circulating_supply'],
                        'total_supply': coin_data['total_supply'],
                        'max_supply': coin_data['max_supply'],
                        'last_updated': quote_data['last_updated'],
                        'source': 'CoinMarketCap',
                        'api_source': 'coinmarketcap',
                        'api_url': url
                    }
                    
                    # Cache the result
                    self._cache_data(cache_key, result)
                    
                    self.logger.info(f"✅ CoinMarketCap: {symbol} = ${result['current_price']:,.2f}, Market Cap: ${result['market_cap']:,.0f}")
                    return result
                    
                else:
                    error_msg = f"Symbol {symbol} not found in CoinMarketCap response"
                    self.logger.warning(f"⚠️ CoinMarketCap: {error_msg}")
                    return {
                        'success': False,
                        'error': error_msg,
                        'source': 'CoinMarketCap',
                        'api_source': 'coinmarketcap'
                    }
            
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                self.logger.error(f"❌ CoinMarketCap API error: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'source': 'CoinMarketCap',
                    'api_source': 'coinmarketcap'
                }
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            self.logger.error(f"❌ CoinMarketCap network error: {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'source': 'CoinMarketCap',
                'api_source': 'coinmarketcap'
            }
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(f"❌ CoinMarketCap unexpected error: {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'source': 'CoinMarketCap',
                'api_source': 'coinmarketcap'
            }

    def get_coingecko_market_cap(self, symbol: str) -> Dict[str, Any]:
        """
        Get market cap data from CoinGecko API (free, no API key required)
        """
        try:
            # CoinGecko symbol mapping
            symbol_map = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum', 
                'BNB': 'binancecoin',
                'ADA': 'cardano',
                'SOL': 'solana',
                'DOT': 'polkadot',
                'LINK': 'chainlink',
                'MATIC': 'polygon',
                'UNI': 'uniswap',
                'LTC': 'litecoin'
            }
            
            coin_id = symbol_map.get(symbol.upper())
            if not coin_id:
                return {
                    'success': False,
                    'error': f'Symbol {symbol} not supported for market cap lookup'
                }
            
            # CoinGecko API endpoint
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_market_cap': 'true',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true',
                'include_last_updated_at': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if coin_id in data:
                    coin_data = data[coin_id]
                    
                    return {
                        'success': True,
                        'market_cap': coin_data.get('usd_market_cap'),
                        'current_price': coin_data.get('usd'),
                        'price_change_24h': coin_data.get('usd_24h_change', 0),
                        'volume_24h': coin_data.get('usd_24h_vol'),
                        'last_updated': coin_data.get('last_updated_at'),
                        'source': 'CoinGecko',
                        'coin_id': coin_id
                    }
                else:
                    return {
                        'success': False,
                        'error': f'No data found for {symbol} on CoinGecko'
                    }
            else:
                return {
                    'success': False,
                    'error': f'CoinGecko API error: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error fetching CoinGecko data: {str(e)}'
            }

    def enrich_with_market_cap(self, price_data: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """
        Enrich price data with market cap information from CoinGecko
        """
        if not price_data.get('success') or not price_data.get('needs_market_cap_enrichment'):
            return price_data
            
        try:
            # Get market cap from CoinGecko
            market_cap_data = self.get_coingecko_market_cap(symbol)
            
            if market_cap_data.get('success'):
                # Enrich the original data
                price_data['market_cap'] = market_cap_data.get('market_cap')
                price_data['market_cap_rank'] = self._estimate_market_cap_rank(market_cap_data.get('market_cap', 0))
                price_data['market_cap_source'] = 'CoinGecko'
                price_data['data_sources'] = [price_data.get('source', 'Unknown'), 'CoinGecko']
                
                # Remove the enrichment flag
                price_data.pop('needs_market_cap_enrichment', None)
                
                self.logger.info(f"✅ Market cap enriched for {symbol}: ${price_data['market_cap']:,.0f}")
            else:
                self.logger.warning(f"⚠️ Could not enrich market cap for {symbol}: {market_cap_data.get('error')}")
                
        except Exception as e:
            self.logger.error(f"❌ Error enriching market cap for {symbol}: {str(e)}")
            
        return price_data
    
    def _estimate_market_cap_rank(self, market_cap: float) -> int:
        """
        Estimate market cap rank based on approximate thresholds
        """
        if market_cap > 1_000_000_000_000:  # > $1T
            return 1
        elif market_cap > 500_000_000_000:  # > $500B
            return 2
        elif market_cap > 100_000_000_000:  # > $100B
            return 3
        elif market_cap > 50_000_000_000:   # > $50B
            return 4
        elif market_cap > 20_000_000_000:   # > $20B
            return 5
        elif market_cap > 10_000_000_000:   # > $10B
            return 10
        elif market_cap > 5_000_000_000:    # > $5B
            return 20
        elif market_cap > 1_000_000_000:    # > $1B
            return 50
        else:
            return 100

    def get_comprehensive_price_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get comprehensive price data using multiple sources with CoinMarketCap as priority for market cap
        """
        results = {}
        
        # PRIORITY 1: Use CoinMarketCap for complete data (price + market cap)
        coinmarketcap_data = self.get_coinmarketcap_data(symbol)
        if coinmarketcap_data.get('success'):
            results['coinmarketcap'] = coinmarketcap_data
        
        # PRIORITY 2: Use Binance for real-time trading data (high accuracy price)
        binance_data = self.get_binance_crypto_data(symbol)
        if binance_data.get('success'):
            results['binance'] = binance_data
        
        # PRIORITY 3: For Bitcoin, use CoinDesk as backup source
        if symbol.upper() == 'BTC':
            coindesk_data = self.get_coindesk_bitcoin_price()
            if coindesk_data.get('success'):
                results['coindesk'] = coindesk_data
        
        # PRIORITY 4: Use Alpha Vantage as additional source
        alpha_vantage_data = self.get_alpha_vantage_crypto_data(symbol)
        if alpha_vantage_data.get('success'):
            results['alpha_vantage'] = alpha_vantage_data
        
        # Determine primary data source based on priority
        primary_data = None
        if 'coinmarketcap' in results:
            # CoinMarketCap is highest priority (has market cap data)
            primary_data = results['coinmarketcap']
            primary_data['backup_sources'] = [k for k in results.keys() if k != 'coinmarketcap']
            self.logger.info(f"🥇 Using CoinMarketCap as primary source for {symbol}")
        elif 'binance' in results:
            # Binance for real-time price, enrich with market cap
            primary_data = results['binance']
            primary_data['backup_sources'] = [k for k in results.keys() if k != 'binance']
            primary_data = self.enrich_with_market_cap(primary_data, symbol)
            self.logger.info(f"� Using Binance as primary source for {symbol}")
        elif symbol.upper() == 'BTC' and 'coindesk' in results:
            # CoinDesk for Bitcoin if others fail
            primary_data = results['coindesk']
            primary_data['backup_sources'] = [k for k in results.keys() if k != 'coindesk']
            primary_data = self.enrich_with_market_cap(primary_data, symbol)
            self.logger.info(f"� Using CoinDesk as primary source for {symbol}")
        elif 'alpha_vantage' in results:
            # Alpha Vantage as last resort
            primary_data = results['alpha_vantage']
            primary_data['backup_sources'] = [k for k in results.keys() if k != 'alpha_vantage']
            primary_data = self.enrich_with_market_cap(primary_data, symbol)
            self.logger.info(f"🥉 Using Alpha Vantage as primary source for {symbol}")
        
        if primary_data:
            primary_data['all_sources'] = results
            primary_data['sources_available'] = len(results)
            primary_data['data_quality'] = 'Excellent' if 'coinmarketcap' in results else 'High' if 'binance' in results else 'Medium'
            return primary_data
        else:
            return {
                'success': False,
                'error': 'No data sources available',
                'symbol': symbol,
                'attempted_sources': ['binance', 'coindesk', 'alpha_vantage'],
                'timestamp': datetime.now().isoformat()
            }

    def get_historical_data(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        """
        Get historical price data using Alpha Vantage
        """
        try:
            if not self.alpha_vantage_key:
                return {
                    'success': False,
                    'error': 'Alpha Vantage API key not available'
                }
            
            params = {
                'function': 'DIGITAL_CURRENCY_DAILY',
                'symbol': symbol,
                'market': 'USD',
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(self.alpha_vantage_base, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for errors
            if 'Error Message' in data or 'Note' in data:
                return {
                    'success': False,
                    'error': data.get('Error Message', 'API rate limit exceeded'),
                    'source': 'Alpha Vantage'
                }
            
            time_series_key = 'Time Series (Digital Currency Daily)'
            if time_series_key not in data:
                return {
                    'success': False,
                    'error': 'No historical data found'
                }
            
            time_series = data[time_series_key]
            
            # Sort dates and get last N days
            dates = sorted(time_series.keys(), reverse=True)[:days]
            
            historical_data = {
                'dates': [],
                'prices': [],
                'volumes': [],
                'high': [],
                'low': []
            }
            
            for date in reversed(dates):  # Reverse to get chronological order
                day_data = time_series[date]
                historical_data['dates'].append(date)
                historical_data['prices'].append(float(day_data['4a. close (USD)']))
                historical_data['volumes'].append(float(day_data['5. volume']))
                historical_data['high'].append(float(day_data['2a. high (USD)']))
                historical_data['low'].append(float(day_data['3a. low (USD)']))
            
            return {
                'success': True,
                'symbol': symbol,
                'data': historical_data,
                'days_requested': days,
                'days_received': len(historical_data['dates']),
                'source': 'Alpha Vantage',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error fetching historical data: {str(e)}",
                'source': 'Alpha Vantage'
            }

    def get_market_overview(self, symbols: List[str] = None) -> Dict[str, Any]:
        """
        Get market overview for multiple cryptocurrencies
        """
        if symbols is None:
            symbols = ['BTC', 'ETH', 'ADA', 'DOT', 'LTC']
        
        market_data = {}
        
        for symbol in symbols:
            try:
                data = self.get_comprehensive_price_data(symbol)
                market_data[symbol] = data
                
                # Rate limiting - Alpha Vantage allows 5 calls per minute
                time.sleep(12)  # 12 seconds between calls = 5 calls per minute
                
            except Exception as e:
                market_data[symbol] = {
                    'success': False,
                    'error': str(e),
                    'symbol': symbol
                }
        
        successful_fetches = sum(1 for data in market_data.values() if data.get('success'))
        
        return {
            'market_overview': market_data,
            'timestamp': datetime.now().isoformat(),
            'total_symbols': len(symbols),
            'successful_fetches': successful_fetches,
            'success_rate': f"{(successful_fetches/len(symbols)*100):.1f}%"
        }

def test_enhanced_price_apis():
    """
    Test function untuk enhanced price APIs dengan CoinMarketCap dan Binance integration
    """
    print("🧪 Testing Enhanced Price APIs dengan API Keys Real (termasuk CoinMarketCap & Binance)...")
    print("=" * 80)
    
    fetcher = EnhancedPriceFetcher()
    
    # Test Bitcoin data (CoinMarketCap priority, Binance, CoinDesk + Alpha Vantage backup)
    print("1️⃣ Testing Bitcoin Price Data (Multi-source dengan CoinMarketCap)...")
    btc_data = fetcher.get_comprehensive_price_data('BTC')
    
    if btc_data.get('success'):
        print(f"   ✅ BTC Price: ${btc_data['current_price']:,.2f}")
        print(f"   📊 Primary Source: {btc_data['source']}")
        print(f"   💰 Market Cap: ${btc_data.get('market_cap', 0):,.0f}")
        print(f"   🏆 Market Cap Rank: #{btc_data.get('market_cap_rank', 'N/A')}")
        print(f"   🔄 Sources Available: {btc_data.get('sources_available', 0)}")
        print(f"   📈 Data Quality: {btc_data.get('data_quality', 'Unknown')}")
        if btc_data.get('price_change_24h'):
            print(f"   📈 24h Change: {btc_data['price_change_24h']:+.2f}%")
    else:
        print(f"   ❌ Error: {btc_data.get('error', 'Unknown error')}")
    
    print()
    
    # Test Ethereum data dengan CoinMarketCap
    print("2️⃣ Testing Ethereum Price Data (CoinMarketCap + Binance)...")
    eth_data = fetcher.get_comprehensive_price_data('ETH')
    
    if eth_data.get('success'):
        print(f"   ✅ ETH Price: ${eth_data['current_price']:,.2f}")
        print(f"   📊 Primary Source: {eth_data['source']}")
        print(f"   💰 Market Cap: ${eth_data.get('market_cap', 0):,.0f}")
        print(f"   🏆 Market Cap Rank: #{eth_data.get('market_cap_rank', 'N/A')}")
        print(f"   📈 24h Change: {eth_data.get('price_change_24h', 0):+.2f}%")
        if eth_data.get('volume_24h'):
            print(f"   💰 24h Volume: ${eth_data['volume_24h']:,.0f}")
    else:
        print(f"   ❌ Error: {eth_data.get('error', 'Unknown error')}")
    
    print()
    
    # Test direct CoinMarketCap API
    print("3️⃣ Testing Direct CoinMarketCap API...")
    cmc_data = fetcher.get_coinmarketcap_data('BTC')
    
    if cmc_data.get('success'):
        print(f"   ✅ CoinMarketCap BTC: ${cmc_data['current_price']:,.2f}")
        print(f"   💰 Market Cap: ${cmc_data['market_cap']:,.0f}")
        print(f"   🔄 Circulating Supply: {cmc_data.get('circulating_supply', 0):,.0f} BTC")
        print(f"   📊 Max Supply: {cmc_data.get('max_supply', 'N/A')}")
    else:
        print(f"   ❌ CoinMarketCap Error: {cmc_data.get('error', 'Unknown error')}")
    
    print()
    
    # Test Binance multi-ticker functionality
    print("4️⃣ Testing Binance Multi-Ticker Data...")
    multi_data = fetcher.get_binance_multiple_tickers(['BTC', 'ETH', 'BNB', 'ADA'])
    
    if multi_data.get('success'):
        print(f"   ✅ Multi-ticker fetch successful")
        print(f"   📊 Symbols fetched: {multi_data.get('total_symbols', 0)}")
        for symbol, data in multi_data.get('data', {}).items():
            print(f"   🔸 {symbol}: ${data['price']:,.2f} ({data['symbol']})")
    else:
        print(f"   ❌ Error: {multi_data.get('error', 'Unknown error')}")
    
    print()
    
    # Test API availability
    print("5️⃣ API Availability Check...")
    print(f"   🔑 CoinMarketCap API Key: {'✅ Available' if fetcher.coinmarketcap_key else '❌ Missing'}")
    print(f"   🔑 Binance API Key: {'✅ Available' if fetcher.binance_key else '❌ Missing'}")
    print(f"   🔑 CoinDesk API Key: {'✅ Available' if fetcher.coindesk_key else '❌ Missing'}")
    print(f"   🔑 Alpha Vantage API Key: {'✅ Available' if fetcher.alpha_vantage_key else '❌ Missing'}")
    
    # Performance summary
    print()
    print("6️⃣ Performance Summary...")
    apis_working = 0
    if btc_data.get('success'): apis_working += 1
    if eth_data.get('success'): apis_working += 1
    if cmc_data.get('success'): apis_working += 1
    if multi_data.get('success'): apis_working += 1
    
    print(f"   🎯 Working APIs: {apis_working}/4")
    print(f"   🚀 Integration Status: {'Excellent' if apis_working >= 3 else 'Partial' if apis_working > 0 else 'Failed'}")
    
    return {
        'coinmarketcap': cmc_data.get('success', False),
        'binance': multi_data.get('success', False),
        'coindesk': btc_data.get('success', False) and btc_data.get('source') == 'CoinDesk',
        'alpha_vantage': eth_data.get('success', False) and eth_data.get('source') == 'Alpha Vantage',
        'api_keys_available': bool(fetcher.coinmarketcap_key and fetcher.binance_key and fetcher.coindesk_key and fetcher.alpha_vantage_key),
        'total_working': apis_working,
        'integration_quality': 'Excellent' if apis_working >= 3 else 'Partial' if apis_working > 0 else 'Failed'
    }

    def get_crypto_price_comprehensive(self, symbol: str) -> Dict[str, Any]:
        """
        Alias method untuk get_comprehensive_price_data untuk kompatibilitas MT5 Server
        
        Args:
            symbol: Crypto symbol (e.g., 'BTC', 'ETH')
            
        Returns:
            Dict dengan data harga lengkap
        """
        return self.get_comprehensive_price_data(symbol)

if __name__ == "__main__":
    test_enhanced_price_apis()

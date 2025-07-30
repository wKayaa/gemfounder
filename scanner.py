"""
Token scanner module for fetching data from various APIs
"""
import requests
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import config
from utils import rate_limit_delay, format_currency

class TokenScanner:
    """Scans for new tokens across multiple blockchains and APIs"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GemFinder/1.0'
        })
        
    def scan_dexscreener_tokens(self) -> List[Dict]:
        """Scan DexScreener for new tokens"""
        try:
            url = f"{config.DEXSCREENER_API_URL}/search/?q=&limit=100"
            response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            tokens = []
            
            if 'pairs' in data:
                for pair in data['pairs']:
                    token_data = self._parse_dexscreener_pair(pair)
                    if token_data:
                        tokens.append(token_data)
            
            logging.info(f"Fetched {len(tokens)} tokens from DexScreener")
            rate_limit_delay(1.0)  # Respect rate limits
            return tokens
            
        except Exception as e:
            logging.error(f"Error scanning DexScreener: {e}")
            return []
    
    def scan_coingecko_new_tokens(self) -> List[Dict]:
        """Scan CoinGecko for newly listed tokens"""
        try:
            url = f"{config.COINGECKO_API_URL}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 100,
                'page': 1,
                'sparkline': False,
                'price_change_percentage': '1h,24h'
            }
            
            response = self.session.get(url, params=params, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            tokens = []
            
            for coin in data:
                token_data = self._parse_coingecko_coin(coin)
                if token_data:
                    tokens.append(token_data)
            
            logging.info(f"Fetched {len(tokens)} tokens from CoinGecko")
            rate_limit_delay(1.0)
            return tokens
            
        except Exception as e:
            logging.error(f"Error scanning CoinGecko: {e}")
            return []
    
    def get_token_details_bscscan(self, token_address: str) -> Optional[Dict]:
        """Get detailed token information from BSCScan"""
        try:
            # Get token info
            url = config.BSCSCAN_API_URL
            params = {
                'module': 'token',
                'action': 'tokeninfo',
                'contractaddress': token_address,
                'apikey': 'YourApiKeyToken'  # Free tier
            }
            
            response = self.session.get(url, params=params, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == '1' and data.get('result'):
                result = data['result'][0] if isinstance(data['result'], list) else data['result']
                return {
                    'contract_address': token_address,
                    'name': result.get('tokenName', ''),
                    'symbol': result.get('symbol', ''),
                    'decimals': int(result.get('decimals', 18)),
                    'total_supply': result.get('totalSupply', '0'),
                    'verified': result.get('contractAddress') is not None
                }
            
            rate_limit_delay(0.2)  # BSCScan rate limit
            return None
            
        except Exception as e:
            logging.error(f"Error getting BSCScan token details for {token_address}: {e}")
            return None
    
    def _parse_dexscreener_pair(self, pair: Dict) -> Optional[Dict]:
        """Parse DexScreener pair data into standardized format"""
        try:
            base_token = pair.get('baseToken', {})
            quote_token = pair.get('quoteToken', {})
            
            # Skip if no market cap or price data
            market_cap = pair.get('marketCap')
            price_usd = pair.get('priceUsd')
            
            if not market_cap or not price_usd:
                return None
            
            # Convert strings to floats
            try:
                market_cap = float(market_cap)
                price_usd = float(price_usd)
            except (ValueError, TypeError):
                return None
            
            # Basic market cap filter
            if market_cap < config.MIN_MARKET_CAP or market_cap > config.MAX_MARKET_CAP:
                return None
            
            token_data = {
                'source': 'dexscreener',
                'contract_address': base_token.get('address', ''),
                'name': base_token.get('name', ''),
                'symbol': base_token.get('symbol', ''),
                'chain': pair.get('chainId', ''),
                'dex': pair.get('dexId', ''),
                'pair_address': pair.get('pairAddress', ''),
                'price_usd': price_usd,
                'market_cap': market_cap,
                'volume_24h': float(pair.get('volume', {}).get('h24', 0) or 0),
                'volume_1h': float(pair.get('volume', {}).get('h1', 0) or 0),
                'price_change_1h': float(pair.get('priceChange', {}).get('h1', 0) or 0),
                'price_change_24h': float(pair.get('priceChange', {}).get('h24', 0) or 0),
                'liquidity_usd': float(pair.get('liquidity', {}).get('usd', 0) or 0),
                'pair_created_at': pair.get('pairCreatedAt'),
                'url': pair.get('url', ''),
                'scan_timestamp': datetime.now().isoformat()
            }
            
            return token_data
            
        except Exception as e:
            logging.error(f"Error parsing DexScreener pair: {e}")
            return None
    
    def _parse_coingecko_coin(self, coin: Dict) -> Optional[Dict]:
        """Parse CoinGecko coin data into standardized format"""
        try:
            market_cap = coin.get('market_cap')
            current_price = coin.get('current_price')
            
            if not market_cap or not current_price:
                return None
            
            # Basic market cap filter
            if market_cap < config.MIN_MARKET_CAP or market_cap > config.MAX_MARKET_CAP:
                return None
            
            token_data = {
                'source': 'coingecko',
                'contract_address': '',  # CoinGecko doesn't always provide contract address
                'name': coin.get('name', ''),
                'symbol': coin.get('symbol', '').upper(),
                'coingecko_id': coin.get('id', ''),
                'price_usd': current_price,
                'market_cap': market_cap,
                'volume_24h': coin.get('total_volume', 0) or 0,
                'price_change_1h': coin.get('price_change_percentage_1h_in_currency', 0) or 0,
                'price_change_24h': coin.get('price_change_percentage_24h', 0) or 0,
                'market_cap_rank': coin.get('market_cap_rank'),
                'image': coin.get('image', ''),
                'scan_timestamp': datetime.now().isoformat()
            }
            
            return token_data
            
        except Exception as e:
            logging.error(f"Error parsing CoinGecko coin: {e}")
            return None
    
    def scan_all_sources(self) -> List[Dict]:
        """Scan all configured sources and return combined results"""
        all_tokens = []
        
        # Scan DexScreener
        dex_tokens = self.scan_dexscreener_tokens()
        all_tokens.extend(dex_tokens)
        
        # Scan CoinGecko
        gecko_tokens = self.scan_coingecko_new_tokens()
        all_tokens.extend(gecko_tokens)
        
        # Remove duplicates based on contract address or symbol
        unique_tokens = self._deduplicate_tokens(all_tokens)
        
        logging.info(f"Total unique tokens found: {len(unique_tokens)}")
        return unique_tokens
    
    def _deduplicate_tokens(self, tokens: List[Dict]) -> List[Dict]:
        """Remove duplicate tokens based on contract address or symbol"""
        seen_addresses = set()
        seen_symbols = set()
        unique_tokens = []
        
        for token in tokens:
            contract_address = token.get('contract_address', '').lower()
            symbol = token.get('symbol', '').lower()
            
            # Skip if we've seen this contract address
            if contract_address and contract_address in seen_addresses:
                continue
            
            # Skip if we've seen this symbol (less reliable but helps with CoinGecko data)
            if symbol and symbol in seen_symbols:
                continue
            
            if contract_address:
                seen_addresses.add(contract_address)
            if symbol:
                seen_symbols.add(symbol)
            
            unique_tokens.append(token)
        
        return unique_tokens
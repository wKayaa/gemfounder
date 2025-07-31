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
        """Scan DexScreener for trending tokens"""
        all_tokens = []
        
        # Get trending tokens from multiple endpoints
        endpoints_to_try = [
            f"{config.DEXSCREENER_API_URL}/tokens/trending",
            f"{config.DEXSCREENER_API_URL}/pairs/bsc/trending",
            f"{config.DEXSCREENER_API_URL}/pairs/ethereum/trending", 
            f"{config.DEXSCREENER_API_URL}/tokens/new"
        ]
        
        for endpoint in endpoints_to_try:
            try:
                response = self.session.get(endpoint, timeout=config.REQUEST_TIMEOUT)
                
                if response.status_code == 200:
                    data = response.json()
                    tokens = []
                    
                    # Handle different response structures
                    if 'pairs' in data:
                        pairs = data['pairs']
                    elif 'tokens' in data:
                        pairs = data['tokens']
                    elif isinstance(data, list):
                        pairs = data
                    else:
                        pairs = []
                    
                    for pair in pairs[:50]:  # Limit to 50 per endpoint
                        token_data = self._parse_dexscreener_pair(pair)
                        if token_data:
                            tokens.append(token_data)
                    
                    all_tokens.extend(tokens)
                    logging.info(f"Fetched {len(tokens)} tokens from {endpoint}")
                else:
                    logging.warning(f"DexScreener endpoint {endpoint} returned status {response.status_code}")
                
                rate_limit_delay(0.5)  # Respect rate limits between calls
                
            except Exception as e:
                logging.warning(f"Error scanning DexScreener endpoint {endpoint}: {e}")
                continue
        
        # If no trending endpoints work, try the basic search with popular tokens
        if not all_tokens:
            try:
                popular_search_terms = ['BSC', 'ETH', 'MATIC', 'BNB']
                for term in popular_search_terms:
                    url = f"{config.DEXSCREENER_API_URL}/search/?q={term}&limit=25"
                    response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if 'pairs' in data:
                            for pair in data['pairs'][:25]:
                                token_data = self._parse_dexscreener_pair(pair)
                                if token_data:
                                    all_tokens.append(token_data)
                    
                    rate_limit_delay(0.3)
                    
            except Exception as e:
                logging.error(f"Error in fallback DexScreener search: {e}")
        
        logging.info(f"Total fetched {len(all_tokens)} tokens from DexScreener")
        return all_tokens
    
    def scan_coingecko_new_tokens(self) -> List[Dict]:
        """Scan CoinGecko for newly listed and trending tokens"""
        all_tokens = []
        
        # Multiple CoinGecko endpoints for better coverage
        endpoints_config = [
            {
                'url': f"{config.COINGECKO_API_URL}/coins/markets",
                'params': {
                    'vs_currency': 'usd',
                    'order': 'market_cap_desc',
                    'per_page': 50,
                    'page': 1,
                    'sparkline': False,
                    'price_change_percentage': '1h,24h'
                },
                'name': 'Market Cap Desc'
            },
            {
                'url': f"{config.COINGECKO_API_URL}/coins/markets", 
                'params': {
                    'vs_currency': 'usd',
                    'order': 'volume_desc',
                    'per_page': 50,
                    'page': 1,
                    'sparkline': False,
                    'price_change_percentage': '1h,24h'
                },
                'name': 'Volume Desc'
            },
            {
                'url': f"{config.COINGECKO_API_URL}/coins/markets",
                'params': {
                    'vs_currency': 'usd', 
                    'order': 'price_change_percentage_24h_desc',
                    'per_page': 50,
                    'page': 1,
                    'sparkline': False,
                    'price_change_percentage': '1h,24h'
                },
                'name': '24h Gainers'
            }
        ]
        
        for config_item in endpoints_config:
            try:
                response = self.session.get(
                    config_item['url'], 
                    params=config_item['params'], 
                    timeout=config.REQUEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    tokens = []
                    
                    for coin in data:
                        token_data = self._parse_coingecko_coin(coin)
                        if token_data:
                            tokens.append(token_data)
                    
                    all_tokens.extend(tokens)
                    logging.info(f"Fetched {len(tokens)} tokens from CoinGecko ({config_item['name']})")
                else:
                    logging.warning(f"CoinGecko {config_item['name']} returned status {response.status_code}")
                
                rate_limit_delay(1.2)  # CoinGecko free tier rate limit
                
            except Exception as e:
                logging.warning(f"Error scanning CoinGecko {config_item['name']}: {e}")
                continue
        
        # Try trending endpoint if available
        try:
            trending_url = f"{config.COINGECKO_API_URL}/search/trending"
            response = self.session.get(trending_url, timeout=config.REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                if 'coins' in data:
                    trending_tokens = []
                    for coin in data['coins'][:20]:  # Top 20 trending
                        # Get detailed info for trending coins
                        coin_id = coin.get('item', {}).get('id', '')
                        if coin_id:
                            try:
                                detail_url = f"{config.COINGECKO_API_URL}/coins/{coin_id}"
                                detail_response = self.session.get(detail_url, timeout=config.REQUEST_TIMEOUT)
                                if detail_response.status_code == 200:
                                    detail_data = detail_response.json()
                                    token_data = self._parse_coingecko_detailed_coin(detail_data)
                                    if token_data:
                                        trending_tokens.append(token_data)
                                rate_limit_delay(0.5)
                            except Exception:
                                continue
                    
                    all_tokens.extend(trending_tokens)
                    logging.info(f"Fetched {len(trending_tokens)} trending tokens from CoinGecko")
        except Exception as e:
            logging.warning(f"Error fetching CoinGecko trending: {e}")
        
        logging.info(f"Total fetched {len(all_tokens)} tokens from CoinGecko")
        return all_tokens
    
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
    
    def _parse_coingecko_detailed_coin(self, coin: Dict) -> Optional[Dict]:
        """Parse detailed CoinGecko coin data into standardized format"""
        try:
            market_data = coin.get('market_data', {})
            current_price = market_data.get('current_price', {}).get('usd')
            market_cap = market_data.get('market_cap', {}).get('usd')
            
            if not market_cap or not current_price:
                return None
            
            # Basic market cap filter
            if market_cap < config.MIN_MARKET_CAP or market_cap > config.MAX_MARKET_CAP:
                return None
            
            token_data = {
                'source': 'coingecko_detailed',
                'contract_address': '',  # Try to get from platforms
                'name': coin.get('name', ''),
                'symbol': coin.get('symbol', '').upper(),
                'coingecko_id': coin.get('id', ''),
                'price_usd': current_price,
                'market_cap': market_cap,
                'volume_24h': market_data.get('total_volume', {}).get('usd', 0) or 0,
                'price_change_1h': market_data.get('price_change_percentage_1h_in_currency', {}).get('usd', 0) or 0,
                'price_change_24h': market_data.get('price_change_percentage_24h', 0) or 0,
                'price_change_7d': market_data.get('price_change_percentage_7d', 0) or 0,
                'market_cap_rank': coin.get('market_cap_rank'),
                'image': coin.get('image', {}).get('large', ''),
                'description': coin.get('description', {}).get('en', '')[:200] if coin.get('description', {}).get('en') else '',
                'homepage': coin.get('links', {}).get('homepage', [''])[0] if coin.get('links', {}).get('homepage') else '',
                'twitter': coin.get('links', {}).get('twitter_screen_name', ''),
                'telegram': coin.get('links', {}).get('telegram_channel_identifier', ''),
                'ath_change_percentage': market_data.get('ath_change_percentage', {}).get('usd', 0),
                'total_supply': market_data.get('total_supply', 0),
                'circulating_supply': market_data.get('circulating_supply', 0),
                'scan_timestamp': datetime.now().isoformat()
            }
            
            # Try to extract contract addresses from platforms
            platforms = coin.get('platforms', {})
            if platforms:
                for platform, address in platforms.items():
                    if address and address != '':
                        token_data['contract_address'] = address
                        token_data['platform'] = platform
                        break
            
            return token_data
            
        except Exception as e:
            logging.error(f"Error parsing detailed CoinGecko coin: {e}")
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
    
    def _parse_coingecko_detailed_coin(self, coin: Dict) -> Optional[Dict]:
        """Parse detailed CoinGecko coin data into standardized format"""
        try:
            market_data = coin.get('market_data', {})
            current_price = market_data.get('current_price', {}).get('usd')
            market_cap = market_data.get('market_cap', {}).get('usd')
            
            if not market_cap or not current_price:
                return None
            
            # Basic market cap filter
            if market_cap < config.MIN_MARKET_CAP or market_cap > config.MAX_MARKET_CAP:
                return None
            
            token_data = {
                'source': 'coingecko_detailed',
                'contract_address': '',  # Try to get from platforms
                'name': coin.get('name', ''),
                'symbol': coin.get('symbol', '').upper(),
                'coingecko_id': coin.get('id', ''),
                'price_usd': current_price,
                'market_cap': market_cap,
                'volume_24h': market_data.get('total_volume', {}).get('usd', 0) or 0,
                'price_change_1h': market_data.get('price_change_percentage_1h_in_currency', {}).get('usd', 0) or 0,
                'price_change_24h': market_data.get('price_change_percentage_24h', 0) or 0,
                'price_change_7d': market_data.get('price_change_percentage_7d', 0) or 0,
                'market_cap_rank': coin.get('market_cap_rank'),
                'image': coin.get('image', {}).get('large', ''),
                'description': coin.get('description', {}).get('en', '')[:200] if coin.get('description', {}).get('en') else '',
                'homepage': coin.get('links', {}).get('homepage', [''])[0] if coin.get('links', {}).get('homepage') else '',
                'twitter': coin.get('links', {}).get('twitter_screen_name', ''),
                'telegram': coin.get('links', {}).get('telegram_channel_identifier', ''),
                'ath_change_percentage': market_data.get('ath_change_percentage', {}).get('usd', 0),
                'total_supply': market_data.get('total_supply', 0),
                'circulating_supply': market_data.get('circulating_supply', 0),
                'scan_timestamp': datetime.now().isoformat()
            }
            
            # Try to extract contract addresses from platforms
            platforms = coin.get('platforms', {})
            if platforms:
                for platform, address in platforms.items():
                    if address and address != '':
                        token_data['contract_address'] = address
                        token_data['platform'] = platform
                        break
            
            return token_data
            
        except Exception as e:
            logging.error(f"Error parsing detailed CoinGecko coin: {e}")
            return None
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
        
        # Scan DEX-specific endpoints for new tokens
        dex_specific_tokens = self.scan_dex_specific_tokens()
        all_tokens.extend(dex_specific_tokens)
        
        # If no tokens found and mock data is enabled, generate mock data
        if not all_tokens and config.ENABLE_MOCK_DATA:
            logging.info("No tokens found from APIs, generating mock data for testing...")
            all_tokens = self._generate_mock_tokens()
        
        # Remove duplicates based on contract address or symbol
        unique_tokens = self._deduplicate_tokens(all_tokens)
        
        logging.info(f"Total unique tokens found: {len(unique_tokens)}")
        return unique_tokens
    
    def _generate_mock_tokens(self) -> List[Dict]:
        """Generate realistic mock token data for testing"""
        import random
        from datetime import datetime, timedelta
        
        mock_tokens = []
        
        # Generate diverse mock tokens with different characteristics
        token_templates = [
            # Micro gems (high risk, high reward)
            {'name': 'MoonRocket', 'symbol': 'MOON', 'market_cap_range': (15000, 80000), 'growth_range': (50, 200)},
            {'name': 'SafeGem', 'symbol': 'SGEM', 'market_cap_range': (25000, 120000), 'growth_range': (30, 150)},
            {'name': 'BabyDoge2', 'symbol': 'BDOGE2', 'market_cap_range': (40000, 200000), 'growth_range': (80, 300)},
            
            # Small gems (balanced)
            {'name': 'DeFiProtocol', 'symbol': 'DEFI', 'market_cap_range': (150000, 600000), 'growth_range': (20, 80)},
            {'name': 'MetaVerse', 'symbol': 'META', 'market_cap_range': (200000, 800000), 'growth_range': (15, 60)},
            {'name': 'GameFi', 'symbol': 'GAFI', 'market_cap_range': (300000, 900000), 'growth_range': (25, 100)},
            
            # Mid gems (lower risk)
            {'name': 'StableCoin', 'symbol': 'STBL', 'market_cap_range': (600000, 1500000), 'growth_range': (10, 40)},
            {'name': 'TechToken', 'symbol': 'TECH', 'market_cap_range': (800000, 2000000), 'growth_range': (15, 50)},
            
            # Trending tokens
            {'name': 'ViralMeme', 'symbol': 'VIRAL', 'market_cap_range': (80000, 400000), 'growth_range': (100, 500)},
            {'name': 'TrendingNow', 'symbol': 'TREND', 'market_cap_range': (120000, 600000), 'growth_range': (75, 250)}
        ]
        
        for i, template in enumerate(token_templates):
            # Random market cap within range
            market_cap = random.uniform(template['market_cap_range'][0], template['market_cap_range'][1])
            
            # Random price based on market cap (assuming reasonable supply)
            price_usd = market_cap / random.uniform(1000000, 100000000)  # Random supply
            
            # Random growth within range
            growth_24h = random.uniform(template['growth_range'][0], template['growth_range'][1])
            growth_1h = random.uniform(growth_24h * 0.1, growth_24h * 0.3)
            
            # Volume based on market cap and growth
            volume_24h = market_cap * random.uniform(0.1, 2.0) * (1 + growth_24h / 100)
            volume_1h = volume_24h * random.uniform(0.02, 0.08)
            
            token_data = {
                'source': 'mock_data',
                'contract_address': f"0x{''.join(random.choices('0123456789abcdef', k=40))}",
                'name': template['name'],
                'symbol': template['symbol'],
                'chain': random.choice(['bsc', 'ethereum', 'polygon']),
                'price_usd': price_usd,
                'market_cap': market_cap,
                'volume_24h': volume_24h,
                'volume_1h': volume_1h,
                'price_change_1h': growth_1h,
                'price_change_24h': growth_24h,
                'price_change_7d': random.uniform(-50, growth_24h * 1.5),
                'liquidity_usd': market_cap * random.uniform(0.1, 0.5),
                'pair_created_at': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                'scan_timestamp': datetime.now().isoformat(),
                'mock_token': True  # Flag to identify mock data
            }
            
            mock_tokens.append(token_data)
        
        logging.info(f"Generated {len(mock_tokens)} mock tokens for testing")
        return mock_tokens
    
    def scan_dex_specific_tokens(self) -> List[Dict]:
        """Scan DEX-specific endpoints for new token listings"""
        all_tokens = []
        
        # PancakeSwap new listings (via DexScreener)
        pancake_endpoints = [
            f"{config.DEXSCREENER_API_URL}/pairs/bsc/latest",
            f"{config.DEXSCREENER_API_URL}/pairs/bsc/trending"
        ]
        
        # Uniswap new listings (via DexScreener)
        uniswap_endpoints = [
            f"{config.DEXSCREENER_API_URL}/pairs/ethereum/latest",
            f"{config.DEXSCREENER_API_URL}/pairs/ethereum/trending"
        ]
        
        all_endpoints = pancake_endpoints + uniswap_endpoints
        
        for endpoint in all_endpoints:
            try:
                response = self.session.get(endpoint, timeout=config.REQUEST_TIMEOUT)
                
                if response.status_code == 200:
                    data = response.json()
                    tokens = []
                    
                    if 'pairs' in data:
                        for pair in data['pairs'][:30]:  # Limit per endpoint
                            token_data = self._parse_dexscreener_pair(pair)
                            if token_data:
                                tokens.append(token_data)
                    
                    all_tokens.extend(tokens)
                    logging.info(f"Fetched {len(tokens)} tokens from {endpoint}")
                
                rate_limit_delay(0.5)
                
            except Exception as e:
                logging.warning(f"Error scanning DEX endpoint {endpoint}: {e}")
                continue
        
        # Try to get some data from popular token aggregators
        try:
            # Simple method to get some trending tokens by searching popular terms
            popular_terms = ['moon', 'gem', 'safe', 'baby', 'mini', 'rocket', 'doge', 'pepe']
            for term in popular_terms[:3]:  # Limit to avoid rate limits
                try:
                    url = f"{config.DEXSCREENER_API_URL}/search/?q={term}&limit=20"
                    response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if 'pairs' in data:
                            for pair in data['pairs'][:10]:
                                token_data = self._parse_dexscreener_pair(pair)
                                if token_data:
                                    all_tokens.append(token_data)
                    
                    rate_limit_delay(0.3)
                except Exception:
                    continue
        except Exception as e:
            logging.warning(f"Error in popular terms search: {e}")
        
        logging.info(f"Total fetched {len(all_tokens)} tokens from DEX-specific sources")
        return all_tokens
    
    def scan_new_listings(self) -> List[Dict]:
        """Scan for newly listed tokens across multiple sources"""
        all_tokens = []
        
        try:
            # DexScreener new tokens endpoint
            new_endpoints = [
                f"{config.DEXSCREENER_API_URL}/tokens/new",
                f"{config.DEXSCREENER_API_URL}/pairs/bsc/new",
                f"{config.DEXSCREENER_API_URL}/pairs/ethereum/new",
                f"{config.DEXSCREENER_API_URL}/pairs/polygon/new"
            ]
            
            for endpoint in new_endpoints:
                try:
                    response = self.session.get(endpoint, timeout=config.REQUEST_TIMEOUT)
                    
                    if response.status_code == 200:
                        data = response.json()
                        tokens = []
                        
                        if 'pairs' in data:
                            for pair in data['pairs'][:20]:  # Limit per endpoint
                                token_data = self._parse_dexscreener_pair(pair)
                                if token_data and self._is_potential_gem(token_data):
                                    tokens.append(token_data)
                        
                        all_tokens.extend(tokens)
                        logging.info(f"Found {len(tokens)} new tokens from {endpoint}")
                    
                    rate_limit_delay(0.5)
                    
                except Exception as e:
                    logging.warning(f"Error scanning new listings from {endpoint}: {e}")
                    continue
            
        except Exception as e:
            logging.error(f"Error in scan_new_listings: {e}")
        
        return all_tokens
    
    def scan_microcap_gems(self) -> List[Dict]:
        """Specialized scanning for micro-cap gems with high potential"""
        all_tokens = []
        
        try:
            # Search for tokens with specific characteristics
            gem_search_terms = [
                # DeFi focused
                'defi', 'yield', 'farm', 'stake', 'protocol',
                # Gaming/NFT focused
                'game', 'nft', 'play', 'earn', 'meta',
                # Utility focused
                'dao', 'vote', 'gov', 'utility', 'token',
                # Trending meme categories (careful filtering needed)
                'ai', 'rwa', 'layer2', 'bridge'
            ]
            
            for term in gem_search_terms[:5]:  # Limit to avoid rate limits
                try:
                    # Search DexScreener for these terms
                    url = f"{config.DEXSCREENER_API_URL}/search/?q={term}&limit=15"
                    response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if 'pairs' in data:
                            for pair in data['pairs']:
                                token_data = self._parse_dexscreener_pair(pair)
                                if token_data and self._is_microcap_gem(token_data):
                                    all_tokens.append(token_data)
                    
                    rate_limit_delay(0.3)
                    
                except Exception as e:
                    logging.warning(f"Error searching for {term}: {e}")
                    continue
            
            # Also scan for tokens with high volume growth but low market cap
            try:
                volume_growth_endpoint = f"{config.DEXSCREENER_API_URL}/pairs/bsc/latest?sortBy=volumeGrowth"
                response = self.session.get(volume_growth_endpoint, timeout=config.REQUEST_TIMEOUT)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'pairs' in data:
                        for pair in data['pairs'][:20]:
                            token_data = self._parse_dexscreener_pair(pair)
                            if token_data and self._is_microcap_gem(token_data):
                                all_tokens.append(token_data)
                
            except Exception as e:
                logging.warning(f"Error scanning volume growth tokens: {e}")
            
        except Exception as e:
            logging.error(f"Error in scan_microcap_gems: {e}")
        
        logging.info(f"Found {len(all_tokens)} potential microcap gems")
        return all_tokens
    
    def _is_potential_gem(self, token: Dict) -> bool:
        """Quick check if token has gem potential"""
        try:
            market_cap = token.get('market_cap', 0)
            volume_24h = token.get('volume_24h', 0)
            price_change_24h = token.get('price_change_24h', 0)
            
            # Basic criteria for gem potential
            if 10000 <= market_cap <= 2000000:  # Between $10k and $2M
                if volume_24h > 1000:  # At least $1k volume
                    if price_change_24h > -50:  # Not crashing too hard
                        return True
            
            # Also consider trending tokens with good metrics
            if market_cap > 5000 and volume_24h > 5000:
                if abs(price_change_24h) > 15:  # Some volatility indicates interest
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _is_microcap_gem(self, token: Dict) -> bool:
        """Check if token qualifies as a microcap gem"""
        try:
            market_cap = token.get('market_cap', 0)
            volume_24h = token.get('volume_24h', 0)
            liquidity_usd = token.get('liquidity_usd', 0)
            price_change_24h = token.get('price_change_24h', 0)
            
            # Microcap criteria
            if 5000 <= market_cap <= 500000:  # Between $5k and $500k
                if volume_24h >= market_cap * 0.05:  # Volume at least 5% of market cap
                    if liquidity_usd >= 2000:  # At least $2k liquidity
                        if price_change_24h > -80:  # Not completely crashed
                            return True
            
            return False
            
        except Exception:
            return False
    
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
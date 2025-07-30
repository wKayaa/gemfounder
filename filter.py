"""
Token filtering module for applying various criteria
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import config
from utils import format_currency, format_percentage

class TokenFilter:
    """Applies filtering criteria to tokens"""
    
    def __init__(self):
        self.filter_stats = {
            'total_processed': 0,
            'passed_market_cap': 0,
            'passed_volume': 0,
            'passed_volume_growth': 0,
            'passed_all_filters': 0
        }
        self.risk_profile = None
    
    def set_risk_profile(self, risk_profile: Dict):
        """Set risk profile for this filtering session"""
        self.risk_profile = risk_profile
    
    def apply_all_filters(self, tokens: List[Dict]) -> List[Dict]:
        """Apply all filtering criteria to token list"""
        self.filter_stats['total_processed'] = len(tokens)
        
        filtered_tokens = []
        
        for token in tokens:
            if self._passes_all_filters(token):
                filtered_tokens.append(token)
                self.filter_stats['passed_all_filters'] += 1
        
        logging.info(f"Filtering results: {len(filtered_tokens)}/{len(tokens)} tokens passed all filters")
        self._log_filter_stats()
        
        return filtered_tokens
    
    def _passes_all_filters(self, token: Dict) -> bool:
        """Check if token passes all filtering criteria"""
        # Market cap filter
        if not self._check_market_cap(token):
            return False
        self.filter_stats['passed_market_cap'] += 1
        
        # Volume filter
        if not self._check_volume(token):
            return False
        self.filter_stats['passed_volume'] += 1
        
        # Volume growth filter
        if not self._check_volume_growth(token):
            return False
        self.filter_stats['passed_volume_growth'] += 1
        
        # Additional safety checks
        if not self._check_basic_safety(token):
            return False
        
        return True
    
    def _check_market_cap(self, token: Dict) -> bool:
        """Check if token meets market cap criteria"""
        try:
            market_cap = token.get('market_cap', 0)
            
            if not isinstance(market_cap, (int, float)) or market_cap <= 0:
                return False
            
            # Use risk profile settings if available
            if self.risk_profile:
                min_cap = self.risk_profile['min_market_cap']
                max_cap = self.risk_profile['max_market_cap']
            else:
                min_cap = config.MIN_MARKET_CAP
                max_cap = config.MAX_MARKET_CAP
            
            # For trending tokens, be more lenient with caps
            source = token.get('source', '')
            if 'trending' in source.lower() or 'detailed' in source.lower():
                min_cap = min_cap * 0.5  # Allow lower market cap for trending
                max_cap = max_cap * 3    # Allow higher market cap for trending
            
            # For tokens with high volume growth, be more lenient
            price_change_24h = abs(token.get('price_change_24h', 0))
            if price_change_24h > 50:  # High volatility = potential gem
                min_cap = min_cap * 0.3
                max_cap = max_cap * 5
            
            return min_cap <= market_cap <= max_cap
            
        except Exception as e:
            logging.error(f"Error checking market cap for {token.get('symbol', 'unknown')}: {e}")
            return False
    
    def _check_volume(self, token: Dict) -> bool:
        """Check if token meets volume criteria"""
        try:
            # Check 24h volume first
            volume_24h = token.get('volume_24h', 0)
            volume_1h = token.get('volume_1h', 0)
            
            # Adaptive volume threshold based on market cap
            market_cap = token.get('market_cap', 0)
            base_volume_threshold = config.MIN_VOLUME_1H
            
            # Lower volume requirements for smaller market caps
            if market_cap < 500000:  # Under 500k market cap
                base_volume_threshold = base_volume_threshold * 0.3
            elif market_cap < 1000000:  # Under 1M market cap
                base_volume_threshold = base_volume_threshold * 0.5
            
            # Check either 24h or 1h volume
            if volume_24h >= base_volume_threshold:
                return True
            elif volume_1h > 0 and volume_1h >= (base_volume_threshold * 0.1):  # 1h volume should be ~1/24 of daily
                return True
            
            # For trending tokens from good sources, be even more lenient
            source = token.get('source', '')
            if 'trending' in source.lower() or 'detailed' in source.lower():
                if volume_24h >= (base_volume_threshold * 0.2):
                    return True
            
            return False
            
        except Exception as e:
            logging.error(f"Error checking volume for {token.get('symbol', 'unknown')}: {e}")
            return False
    
    def _check_volume_growth(self, token: Dict) -> bool:
        """Check if token shows positive momentum or growth potential"""
        try:
            # Multiple indicators for growth potential
            price_change_1h = token.get('price_change_1h', 0)
            price_change_24h = token.get('price_change_24h', 0)
            price_change_7d = token.get('price_change_7d', 0)
            
            # Check for positive momentum in any timeframe
            growth_indicators = 0
            
            # 1h growth
            if price_change_1h > (config.MIN_VOLUME_GROWTH * 0.5):
                growth_indicators += 2  # Short-term momentum is valuable
            elif price_change_1h > 0:
                growth_indicators += 1
            
            # 24h growth 
            if price_change_24h > config.MIN_VOLUME_GROWTH:
                growth_indicators += 2
            elif price_change_24h > (config.MIN_VOLUME_GROWTH * 0.3):
                growth_indicators += 1
            
            # 7d growth (for trending analysis)
            if price_change_7d > (config.MIN_VOLUME_GROWTH * 2):
                growth_indicators += 1
            
            # Check for recovery patterns (negative 7d but positive 24h)
            if price_change_7d < 0 and price_change_24h > 20:
                growth_indicators += 2  # Recovery plays can be gems
            
            # Special conditions for very new or trending tokens
            source = token.get('source', '')
            if 'trending' in source.lower():
                growth_indicators += 1  # Trending tokens get bonus points
            
            # Market cap consideration - smaller caps need less growth to be interesting
            market_cap = token.get('market_cap', 0)
            if market_cap < 200000 and price_change_24h > 10:  # Small cap with decent growth
                growth_indicators += 1
            
            # Need at least 1 growth indicator to pass
            return growth_indicators >= 1
            
        except Exception as e:
            logging.error(f"Error checking volume growth for {token.get('symbol', 'unknown')}: {e}")
            return False
    
    def _check_basic_safety(self, token: Dict) -> bool:
        """Perform basic safety checks"""
        try:
            # Check if token has minimum required data
            required_fields = ['symbol', 'name', 'price_usd']
            for field in required_fields:
                if not token.get(field):
                    logging.debug(f"Token missing required field: {field}")
                    return False
            
            # Check for reasonable price (not too low to avoid dust tokens)
            price_usd = token.get('price_usd', 0)
            if price_usd <= 0 or price_usd > 1000000:  # Price too low or suspiciously high
                logging.debug(f"Token {token.get('symbol')} has suspicious price: {price_usd}")
                return False
            
            # Check symbol length (avoid spam tokens with very long symbols)
            symbol = token.get('symbol', '')
            if len(symbol) > 20 or len(symbol) < 2:
                logging.debug(f"Token symbol length suspicious: {symbol}")
                return False
            
            # Check name length
            name = token.get('name', '')
            if len(name) > 100 or len(name) < 2:
                logging.debug(f"Token name length suspicious: {name}")
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"Error in basic safety check for {token.get('symbol', 'unknown')}: {e}")
            return False
    
    def _log_filter_stats(self):
        """Log filtering statistics"""
        total = self.filter_stats['total_processed']
        if total == 0:
            return
        
        logging.info("Filter Statistics:")
        logging.info(f"  Total tokens processed: {total}")
        logging.info(f"  Passed market cap filter: {self.filter_stats['passed_market_cap']} ({self.filter_stats['passed_market_cap']/total*100:.1f}%)")
        logging.info(f"  Passed volume filter: {self.filter_stats['passed_volume']} ({self.filter_stats['passed_volume']/total*100:.1f}%)")
        logging.info(f"  Passed volume growth filter: {self.filter_stats['passed_volume_growth']} ({self.filter_stats['passed_volume_growth']/total*100:.1f}%)")
        logging.info(f"  Passed all filters: {self.filter_stats['passed_all_filters']} ({self.filter_stats['passed_all_filters']/total*100:.1f}%)")
    
    def get_filter_summary(self) -> Dict:
        """Get filtering statistics summary"""
        return self.filter_stats.copy()
    
    def reset_stats(self):
        """Reset filtering statistics"""
        self.filter_stats = {
            'total_processed': 0,
            'passed_market_cap': 0,
            'passed_volume': 0,
            'passed_volume_growth': 0,
            'passed_all_filters': 0
        }
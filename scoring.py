"""
Intelligent scoring system for evaluating token potential
"""
import logging
import math
from typing import Dict, List, Optional
import config
from utils import format_percentage

class TokenScorer:
    """Calculates intelligent scores for tokens based on multiple criteria"""
    
    def __init__(self):
        self.weights = config.SCORE_WEIGHTS
    
    def calculate_score(self, token: Dict) -> float:
        """Calculate overall score for a token (0-100)"""
        try:
            scores = {
                'market_cap': self._score_market_cap(token),
                'volume_growth': self._score_volume_growth(token),
                'liquidity_lock': self._score_liquidity_lock(token),
                'contract_security': self._score_contract_security(token),
                'whale_activity': self._score_whale_activity(token),
                'social_signals': self._score_social_signals(token)
            }
            
            # Calculate weighted score
            total_score = 0
            for category, score in scores.items():
                weight = self.weights.get(category, 0)
                total_score += score * weight
            
            # Normalize to 0-100 scale
            final_score = min(100, max(0, total_score * 100))
            
            # Add detailed scoring breakdown to token data
            token['score_breakdown'] = scores
            token['score'] = final_score
            
            logging.debug(f"Token {token.get('symbol')} scored {final_score:.1f}/100")
            return final_score
            
        except Exception as e:
            logging.error(f"Error calculating score for {token.get('symbol', 'unknown')}: {e}")
            return 0
    
    def _score_market_cap(self, token: Dict) -> float:
        """Score based on market cap position within our range (0-1)"""
        try:
            market_cap = token.get('market_cap', 0)
            
            if market_cap <= 0:
                return 0
            
            # Sweet spot is in the middle of our range
            min_mc = config.MIN_MARKET_CAP
            max_mc = config.MAX_MARKET_CAP
            optimal_mc = (min_mc + max_mc) / 2
            
            # Distance from optimal
            distance = abs(market_cap - optimal_mc)
            max_distance = max_mc - min_mc
            
            # Score inversely proportional to distance from optimal
            score = 1 - (distance / max_distance)
            return max(0, min(1, score))
            
        except Exception as e:
            logging.error(f"Error scoring market cap: {e}")
            return 0
    
    def _score_volume_growth(self, token: Dict) -> float:
        """Score based on volume and price growth (0-1)"""
        try:
            # Price change indicators
            price_change_1h = token.get('price_change_1h', 0)
            price_change_24h = token.get('price_change_24h', 0)
            price_change_7d = token.get('price_change_7d', 0)
            
            # Volume indicators
            volume_24h = token.get('volume_24h', 0)
            volume_1h = token.get('volume_1h', 0)
            
            score = 0
            
            # Score based on price momentum (more generous)
            if price_change_1h > 0:
                # Give higher scores for shorter timeframe gains
                score += min(0.5, price_change_1h / 100)  # Up to 50% for strong 1h gains
            
            if price_change_24h > 0:
                # Strong 24h gains are valuable
                score += min(0.4, price_change_24h / 150)  # Up to 40% for strong 24h gains
            
            # Bonus for momentum building (7d negative but 24h positive = reversal)
            if price_change_7d < 0 and price_change_24h > 20:
                score += 0.2  # Recovery bonus
            
            # Score based on volume relative to market cap
            market_cap = token.get('market_cap', 1)
            if volume_24h > 0 and market_cap > 0:
                volume_ratio = volume_24h / market_cap
                if volume_ratio > 0.1:  # High volume relative to market cap
                    score += min(0.3, volume_ratio * 2)
                elif volume_ratio > 0.05:
                    score += min(0.2, volume_ratio * 3)
                elif volume_ratio > 0.01:
                    score += min(0.1, volume_ratio * 5)
            
            return max(0, min(1, score))
            
        except Exception as e:
            logging.error(f"Error scoring volume growth: {e}")
            return 0
    
    def _score_liquidity_lock(self, token: Dict) -> float:
        """Score based on liquidity and lock status (0-1)"""
        try:
            liquidity_usd = token.get('liquidity_usd', 0)
            market_cap = token.get('market_cap', 1)
            
            # Basic liquidity score
            if liquidity_usd <= 0:
                # For mock data or missing liquidity data, give partial score
                if token.get('mock_token', False):
                    return 0.5  # Neutral score for testing
                return 0.3  # Some score for tokens without liquidity data
            
            # Calculate liquidity ratio to market cap
            liquidity_ratio = liquidity_usd / market_cap if market_cap > 0 else 0
            
            # Higher liquidity ratio is better (but diminishing returns)
            if liquidity_ratio > 0.3:  # Very high liquidity
                return 1.0
            elif liquidity_ratio > 0.15:  # Good liquidity
                return 0.8
            elif liquidity_ratio > 0.05:  # Decent liquidity
                return 0.6
            elif liquidity_ratio > 0.01:  # Minimal liquidity
                return 0.4
            else:
                return 0.2  # Low liquidity but not zero
            
        except Exception as e:
            logging.error(f"Error scoring liquidity: {e}")
            return 0.5  # Neutral score on error
            
        except Exception as e:
            logging.error(f"Error scoring liquidity lock: {e}")
            return 0.5  # Neutral score if we can't determine
    
    def _score_contract_security(self, token: Dict) -> float:
        """Score based on contract security indicators (0-1)"""
        try:
            score = 0
            
            # Check if contract address is available
            contract_address = token.get('contract_address', '')
            if contract_address and len(contract_address) > 20:
                score += 0.4  # Increased from 0.3
            elif contract_address:
                score += 0.2  # Partial score for shorter addresses
            
            # Check if token is verified on blockchain explorer
            if token.get('verified', False):
                score += 0.3
            else:
                # Even unverified tokens can be legitimate for new gems
                score += 0.1
            
            # Check source reliability
            source = token.get('source', '')
            if source in ['dexscreener', 'coingecko', 'coingecko_detailed']:
                score += 0.3
            elif source == 'mock_data':
                score += 0.5  # For testing purposes
            else:
                score += 0.1  # Some score for other sources
            
            # Bonus for trending tokens (more likely to be legitimate)
            if 'trending' in source.lower() or 'detailed' in source.lower():
                score += 0.2
            
            return max(0.2, min(1, score))  # Minimum 0.2 to not completely penalize new tokens
            
        except Exception as e:
            logging.error(f"Error scoring contract security: {e}")
            return 0.5  # Neutral score on error
    
    def _score_whale_activity(self, token: Dict) -> float:
        """Score based on whale activity indicators (0-1)"""
        try:
            volume_24h = token.get('volume_24h', 0)
            market_cap = token.get('market_cap', 1)
            
            # Use volume relative to market cap as whale activity indicator
            if market_cap > 0:
                volume_ratio = volume_24h / market_cap
                
                # High volume relative to market cap suggests whale interest
                if volume_ratio > 1.0:  # Volume > market cap
                    return 1.0
                elif volume_ratio > 0.5:
                    return 0.8
                elif volume_ratio > 0.2:
                    return 0.6
                elif volume_ratio > 0.1:
                    return 0.5
                else:
                    return 0.4
            
            # Fallback to absolute volume threshold
            if volume_24h > config.WHALE_THRESHOLD:
                return min(0.8, volume_24h / (config.WHALE_THRESHOLD * 5))
            
            return 0.4  # Neutral-positive score
            
        except Exception as e:
            logging.error(f"Error scoring whale activity: {e}")
            return 0.4
    
    def _score_social_signals(self, token: Dict) -> float:
        """Score based on social media signals (0-1)"""
        try:
            score = 0
            
            # Check if token has social links
            twitter = token.get('twitter', '')
            telegram = token.get('telegram', '')
            homepage = token.get('homepage', '')
            
            if twitter:
                score += 0.3
            if telegram:
                score += 0.3
            if homepage:
                score += 0.2
            
            # Market cap rank as popularity indicator
            market_cap_rank = token.get('market_cap_rank')
            if market_cap_rank:
                if market_cap_rank <= 500:
                    score += 0.4
                elif market_cap_rank <= 1000:
                    score += 0.3
                elif market_cap_rank <= 2000:
                    score += 0.2
                else:
                    score += 0.1
            
            # Source bonus (trending tokens likely have social buzz)
            source = token.get('source', '')
            if 'trending' in source.lower():
                score += 0.3
            elif 'detailed' in source.lower():
                score += 0.2
            
            # Price momentum as social interest proxy
            price_change_24h = token.get('price_change_24h', 0)
            if price_change_24h > 50:  # High momentum suggests social attention
                score += 0.3
            elif price_change_24h > 20:
                score += 0.2
            
            return max(0.3, min(1, score))  # Minimum 0.3 baseline
            
        except Exception as e:
            logging.error(f"Error scoring social signals: {e}")
            return 0.3
    
    def score_tokens(self, tokens: List[Dict]) -> List[Dict]:
        """Score multiple tokens and sort by score"""
        scored_tokens = []
        
        for token in tokens:
            score = self.calculate_score(token)
            if score >= config.SCORE_THRESHOLD:
                scored_tokens.append(token)
        
        # Sort by score (highest first)
        scored_tokens.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        logging.info(f"Scored {len(tokens)} tokens, {len(scored_tokens)} passed threshold of {config.SCORE_THRESHOLD}")
        return scored_tokens
    
    def get_score_explanation(self, token: Dict) -> str:
        """Generate human-readable explanation of the score"""
        try:
            breakdown = token.get('score_breakdown', {})
            score = token.get('score', 0)
            
            explanation = f"Overall Score: {score:.1f}/100\n\n"
            explanation += "Breakdown:\n"
            
            categories = {
                'market_cap': 'Market Cap Position',
                'volume_growth': 'Volume & Growth',
                'liquidity_lock': 'Liquidity & Lock',
                'contract_security': 'Contract Security',
                'whale_activity': 'Whale Activity',
                'social_signals': 'Social Signals'
            }
            
            for key, name in categories.items():
                component_score = breakdown.get(key, 0) * 100
                weight = self.weights.get(key, 0) * 100
                contribution = component_score * self.weights.get(key, 0)
                
                explanation += f"• {name}: {component_score:.1f}/100 (weight: {weight:.0f}%, contributes: {contribution:.1f})\n"
            
            return explanation
            
        except Exception as e:
            logging.error(f"Error generating score explanation: {e}")
            return f"Score: {token.get('score', 0):.1f}/100"
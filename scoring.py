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
            
            # Volume indicators
            volume_24h = token.get('volume_24h', 0)
            volume_1h = token.get('volume_1h', 0)
            
            score = 0
            
            # Score based on price momentum
            if price_change_1h > 0:
                # Logarithmic scaling for price changes
                score += min(0.4, math.log(1 + price_change_1h) / 10)
            
            if price_change_24h > 0:
                score += min(0.3, math.log(1 + price_change_24h) / 15)
            
            # Score based on volume
            if volume_24h > config.MIN_VOLUME_1H:
                volume_score = min(0.3, math.log(volume_24h / config.MIN_VOLUME_1H) / 10)
                score += volume_score
            
            return max(0, min(1, score))
            
        except Exception as e:
            logging.error(f"Error scoring volume growth: {e}")
            return 0
    
    def _score_liquidity_lock(self, token: Dict) -> float:
        """Score based on liquidity and lock status (0-1)"""
        try:
            liquidity_usd = token.get('liquidity_usd', 0)
            
            # Basic liquidity score
            if liquidity_usd <= 0:
                return 0
            
            # Higher liquidity is better, but with diminishing returns
            liquidity_score = min(1, math.log(1 + liquidity_usd) / 20)
            
            # TODO: In future versions, integrate with Unicrypt API to check lock status
            # For now, give partial score based on liquidity amount
            
            return liquidity_score
            
        except Exception as e:
            logging.error(f"Error scoring liquidity lock: {e}")
            return 0.5  # Neutral score if we can't determine
    
    def _score_contract_security(self, token: Dict) -> float:
        """Score based on contract security indicators (0-1)"""
        try:
            score = 0
            
            # Check if contract address is available
            contract_address = token.get('contract_address', '')
            if contract_address:
                score += 0.3
            
            # Check if token is verified on blockchain explorer
            if token.get('verified', False):
                score += 0.4
            
            # Check source reliability
            source = token.get('source', '')
            if source in ['dexscreener', 'coingecko']:
                score += 0.3
            
            # TODO: In future versions, add contract analysis:
            # - Check for honeypot indicators
            # - Analyze contract functions
            # - Check for ownership renouncement
            # - Verify audit status
            
            return max(0, min(1, score))
            
        except Exception as e:
            logging.error(f"Error scoring contract security: {e}")
            return 0.5  # Neutral score if we can't determine
    
    def _score_whale_activity(self, token: Dict) -> float:
        """Score based on whale activity indicators (0-1)"""
        try:
            # TODO: Implement whale detection by analyzing:
            # - Large recent transactions
            # - Holder distribution
            # - Known whale addresses
            
            # For now, use volume as proxy for whale interest
            volume_24h = token.get('volume_24h', 0)
            
            if volume_24h > config.WHALE_THRESHOLD:
                # Higher volume suggests more whale activity
                whale_score = min(1, math.log(volume_24h / config.WHALE_THRESHOLD) / 10)
                return whale_score
            
            return 0.3  # Neutral score
            
        except Exception as e:
            logging.error(f"Error scoring whale activity: {e}")
            return 0.3
    
    def _score_social_signals(self, token: Dict) -> float:
        """Score based on social media signals (0-1)"""
        try:
            # TODO: Implement social signal analysis:
            # - Twitter mentions and sentiment
            # - Telegram group activity
            # - Reddit mentions
            # - Discord activity
            
            # For now, use market cap rank as proxy for popularity
            market_cap_rank = token.get('market_cap_rank')
            
            if market_cap_rank:
                # Better rank = higher score (inverse relationship)
                if market_cap_rank <= 1000:
                    return 0.8
                elif market_cap_rank <= 2000:
                    return 0.6
                elif market_cap_rank <= 5000:
                    return 0.4
                else:
                    return 0.2
            
            return 0.3  # Neutral score if no rank data
            
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
"""
Advanced rug pull detection and security analysis module
"""
import logging
import requests
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import config

class RugPullDetector:
    """Advanced rug pull detection and security analysis"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GemFinder-RugDetector/1.0'
        })
        
        # Known rug pull indicators
        self.rug_indicators = {
            'honeypot_patterns': [
                'buy_tax', 'sell_tax', 'transfer_tax',
                'can_not_sell', 'cannot_sell', 'honeypot'
            ],
            'suspicious_names': [
                'safemoon', 'babydoge', 'elonmusk', 'dogelon',
                'shibainu', 'floki', 'moon', 'safe', 'baby'
            ],
            'scam_symbols': [
                'SCAM', 'RUG', 'FAKE', 'TEST', 'SPAM'
            ],
            'red_flag_domains': [
                'bit.ly', 'tinyurl.com', 't.me', 'telegram.me'
            ]
        }
        
        # Legitimate project indicators
        self.legitimacy_indicators = {
            'verified_sources': [
                'coingecko', 'coinmarketcap', 'dextools', 'dexscreener'
            ],
            'good_domains': [
                '.com', '.org', '.net', '.io', '.fi', '.xyz'
            ],
            'audit_firms': [
                'certik', 'hacken', 'slowmist', 'quantstamp', 'consensys'
            ]
        }
    
    def analyze_token_security(self, token: Dict) -> Dict:
        """Comprehensive security analysis of a token"""
        try:
            security_score = 100  # Start with perfect score
            risk_factors = []
            legitimacy_factors = []
            
            # Contract analysis
            contract_analysis = self._analyze_contract(token)
            security_score += contract_analysis['score_adjustment']
            risk_factors.extend(contract_analysis['risk_factors'])
            legitimacy_factors.extend(contract_analysis['legitimacy_factors'])
            
            # Liquidity analysis
            liquidity_analysis = self._analyze_liquidity(token)
            security_score += liquidity_analysis['score_adjustment']
            risk_factors.extend(liquidity_analysis['risk_factors'])
            legitimacy_factors.extend(liquidity_analysis['legitimacy_factors'])
            
            # Name and symbol analysis
            name_analysis = self._analyze_token_name(token)
            security_score += name_analysis['score_adjustment']
            risk_factors.extend(name_analysis['risk_factors'])
            legitimacy_factors.extend(name_analysis['legitimacy_factors'])
            
            # Trading pattern analysis
            trading_analysis = self._analyze_trading_patterns(token)
            security_score += trading_analysis['score_adjustment']
            risk_factors.extend(trading_analysis['risk_factors'])
            legitimacy_factors.extend(trading_analysis['legitimacy_factors'])
            
            # Social and web presence analysis
            social_analysis = self._analyze_social_presence(token)
            security_score += social_analysis['score_adjustment']
            risk_factors.extend(social_analysis['risk_factors'])
            legitimacy_factors.extend(social_analysis['legitimacy_factors'])
            
            # Normalize security score (0-100)
            security_score = max(0, min(100, security_score))
            
            # Determine risk level
            if security_score >= 80:
                risk_level = "LOW"
            elif security_score >= 60:
                risk_level = "MEDIUM"
            elif security_score >= 40:
                risk_level = "HIGH"
            else:
                risk_level = "CRITICAL"
            
            return {
                'security_score': security_score,
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'legitimacy_factors': legitimacy_factors,
                'is_likely_rug': security_score < 30,
                'is_safe_to_trade': security_score >= 60,
                'recommendation': self._get_recommendation(security_score, risk_factors)
            }
            
        except Exception as e:
            logging.error(f"Error analyzing token security: {e}")
            return {
                'security_score': 0,
                'risk_level': "UNKNOWN",
                'risk_factors': ["Analysis failed"],
                'legitimacy_factors': [],
                'is_likely_rug': True,
                'is_safe_to_trade': False,
                'recommendation': "AVOID - Analysis failed"
            }
    
    def _analyze_contract(self, token: Dict) -> Dict:
        """Analyze contract-related security factors"""
        score_adjustment = 0
        risk_factors = []
        legitimacy_factors = []
        
        try:
            contract_address = token.get('contract_address', '')
            chain = token.get('chain', '').lower()
            
            if not contract_address:
                risk_factors.append("No contract address available")
                score_adjustment -= 20
                return {
                    'score_adjustment': score_adjustment,
                    'risk_factors': risk_factors,
                    'legitimacy_factors': legitimacy_factors
                }
            
            # Check contract verification
            if token.get('verified', False):
                legitimacy_factors.append("Contract is verified")
                score_adjustment += 10
            else:
                risk_factors.append("Contract not verified")
                score_adjustment -= 15
            
            # Check contract age (if available)
            created_at = token.get('created_at')
            if created_at:
                try:
                    creation_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    age_days = (datetime.now() - creation_date).days
                    
                    if age_days < 1:
                        risk_factors.append("Token created less than 24 hours ago")
                        score_adjustment -= 25
                    elif age_days < 7:
                        risk_factors.append("Token less than 1 week old")
                        score_adjustment -= 10
                    elif age_days > 30:
                        legitimacy_factors.append(f"Token exists for {age_days} days")
                        score_adjustment += 5
                except:
                    pass
            
            # Check for proxy contracts (can be risky)
            if token.get('is_proxy', False):
                risk_factors.append("Uses proxy contract pattern")
                score_adjustment -= 5
            
            return {
                'score_adjustment': score_adjustment,
                'risk_factors': risk_factors,
                'legitimacy_factors': legitimacy_factors
            }
            
        except Exception as e:
            logging.error(f"Error in contract analysis: {e}")
            return {
                'score_adjustment': -20,
                'risk_factors': ["Contract analysis failed"],
                'legitimacy_factors': []
            }
    
    def _analyze_liquidity(self, token: Dict) -> Dict:
        """Analyze liquidity-related security factors"""
        score_adjustment = 0
        risk_factors = []
        legitimacy_factors = []
        
        try:
            liquidity_usd = token.get('liquidity_usd', 0)
            market_cap = token.get('market_cap', 0)
            
            if liquidity_usd <= 0:
                risk_factors.append("No liquidity information available")
                score_adjustment -= 15
                return {
                    'score_adjustment': score_adjustment,
                    'risk_factors': risk_factors,
                    'legitimacy_factors': legitimacy_factors
                }
            
            # Calculate liquidity to market cap ratio
            if market_cap > 0:
                liquidity_ratio = liquidity_usd / market_cap
                
                if liquidity_ratio < 0.05:  # Less than 5%
                    risk_factors.append(f"Very low liquidity ratio: {liquidity_ratio*100:.1f}%")
                    score_adjustment -= 20
                elif liquidity_ratio < 0.10:  # Less than 10%
                    risk_factors.append(f"Low liquidity ratio: {liquidity_ratio*100:.1f}%")
                    score_adjustment -= 10
                elif liquidity_ratio > 0.30:  # More than 30%
                    legitimacy_factors.append(f"Good liquidity ratio: {liquidity_ratio*100:.1f}%")
                    score_adjustment += 10
            
            # Absolute liquidity thresholds
            if liquidity_usd < 1000:  # Less than $1k
                risk_factors.append(f"Very low liquidity: ${liquidity_usd:,.0f}")
                score_adjustment -= 25
            elif liquidity_usd < 5000:  # Less than $5k
                risk_factors.append(f"Low liquidity: ${liquidity_usd:,.0f}")
                score_adjustment -= 10
            elif liquidity_usd > 50000:  # More than $50k
                legitimacy_factors.append(f"Good liquidity: ${liquidity_usd:,.0f}")
                score_adjustment += 5
            
            # Check for liquidity lock information
            if token.get('liquidity_locked', False):
                legitimacy_factors.append("Liquidity is locked")
                score_adjustment += 15
            elif 'lock' in str(token.get('additional_info', '')).lower():
                legitimacy_factors.append("Liquidity lock mentioned")
                score_adjustment += 10
            else:
                risk_factors.append("No liquidity lock information")
                score_adjustment -= 10
            
            return {
                'score_adjustment': score_adjustment,
                'risk_factors': risk_factors,
                'legitimacy_factors': legitimacy_factors
            }
            
        except Exception as e:
            logging.error(f"Error in liquidity analysis: {e}")
            return {
                'score_adjustment': -10,
                'risk_factors': ["Liquidity analysis failed"],
                'legitimacy_factors': []
            }
    
    def _analyze_token_name(self, token: Dict) -> Dict:
        """Analyze token name and symbol for red flags"""
        score_adjustment = 0
        risk_factors = []
        legitimacy_factors = []
        
        try:
            name = token.get('name', '').lower()
            symbol = token.get('symbol', '').lower()
            
            # Check for suspicious patterns in name
            for suspicious in self.rug_indicators['suspicious_names']:
                if suspicious in name or suspicious in symbol:
                    risk_factors.append(f"Suspicious name pattern: contains '{suspicious}'")
                    score_adjustment -= 15
            
            # Check for scam symbols
            for scam_symbol in self.rug_indicators['scam_symbols']:
                if scam_symbol.lower() in symbol:
                    risk_factors.append(f"Scam symbol detected: {scam_symbol}")
                    score_adjustment -= 30
            
            # Check for excessive use of numbers or special characters
            if re.search(r'[0-9]{3,}', name) or re.search(r'[^a-zA-Z0-9\s]{3,}', name):
                risk_factors.append("Name contains excessive numbers or symbols")
                score_adjustment -= 10
            
            # Check symbol length
            if len(symbol) > 10:
                risk_factors.append(f"Unusually long symbol: {len(symbol)} characters")
                score_adjustment -= 5
            elif len(symbol) < 2:
                risk_factors.append(f"Unusually short symbol: {len(symbol)} characters")
                score_adjustment -= 10
            
            # Check for legitimate naming patterns
            if any(word in name for word in ['protocol', 'network', 'chain', 'dao', 'defi']):
                legitimacy_factors.append("Professional naming convention")
                score_adjustment += 5
            
            return {
                'score_adjustment': score_adjustment,
                'risk_factors': risk_factors,
                'legitimacy_factors': legitimacy_factors
            }
            
        except Exception as e:
            logging.error(f"Error in name analysis: {e}")
            return {
                'score_adjustment': 0,
                'risk_factors': [],
                'legitimacy_factors': []
            }
    
    def _analyze_trading_patterns(self, token: Dict) -> Dict:
        """Analyze trading patterns for rug pull indicators"""
        score_adjustment = 0
        risk_factors = []
        legitimacy_factors = []
        
        try:
            price_change_1h = token.get('price_change_1h', 0)
            price_change_24h = token.get('price_change_24h', 0)
            volume_24h = token.get('volume_24h', 0)
            market_cap = token.get('market_cap', 0)
            
            # Check for pump and dump patterns
            if price_change_1h > 500:  # More than 500% in 1 hour
                risk_factors.append(f"Extreme price pump: +{price_change_1h:.1f}% in 1h")
                score_adjustment -= 20
            elif price_change_1h > 200:  # More than 200% in 1 hour
                risk_factors.append(f"High price volatility: +{price_change_1h:.1f}% in 1h")
                score_adjustment -= 10
            
            # Check for suspicious volume patterns
            if market_cap > 0 and volume_24h > 0:
                volume_to_mcap_ratio = volume_24h / market_cap
                
                if volume_to_mcap_ratio > 5:  # Volume more than 5x market cap
                    risk_factors.append(f"Extremely high volume ratio: {volume_to_mcap_ratio:.1f}x")
                    score_adjustment -= 15
                elif volume_to_mcap_ratio > 2:  # Volume more than 2x market cap
                    risk_factors.append(f"High volume ratio: {volume_to_mcap_ratio:.1f}x")
                    score_adjustment -= 5
                elif 0.1 <= volume_to_mcap_ratio <= 1.0:  # Healthy ratio
                    legitimacy_factors.append(f"Healthy volume ratio: {volume_to_mcap_ratio:.2f}x")
                    score_adjustment += 5
            
            # Check for consistent growth vs sudden spikes
            if 0 < price_change_24h <= 100:  # Reasonable growth
                legitimacy_factors.append(f"Reasonable 24h growth: +{price_change_24h:.1f}%")
                score_adjustment += 5
            elif price_change_24h > 1000:  # More than 1000% in 24h
                risk_factors.append(f"Extreme price spike: +{price_change_24h:.1f}% in 24h")
                score_adjustment -= 25
            
            return {
                'score_adjustment': score_adjustment,
                'risk_factors': risk_factors,
                'legitimacy_factors': legitimacy_factors
            }
            
        except Exception as e:
            logging.error(f"Error in trading pattern analysis: {e}")
            return {
                'score_adjustment': 0,
                'risk_factors': [],
                'legitimacy_factors': []
            }
    
    def _analyze_social_presence(self, token: Dict) -> Dict:
        """Analyze social media and web presence"""
        score_adjustment = 0
        risk_factors = []
        legitimacy_factors = []
        
        try:
            # Check for website
            website = token.get('website', '')
            if website:
                # Check for suspicious domains
                if any(domain in website for domain in self.rug_indicators['red_flag_domains']):
                    risk_factors.append("Uses suspicious domain for website")
                    score_adjustment -= 10
                elif any(domain in website for domain in self.legitimacy_indicators['good_domains']):
                    legitimacy_factors.append("Has professional website")
                    score_adjustment += 5
            else:
                risk_factors.append("No website provided")
                score_adjustment -= 5
            
            # Check for social media presence
            social_links = token.get('social_links', {})
            if isinstance(social_links, dict):
                social_count = len([link for link in social_links.values() if link])
                
                if social_count >= 3:
                    legitimacy_factors.append(f"Good social presence: {social_count} platforms")
                    score_adjustment += 10
                elif social_count >= 1:
                    legitimacy_factors.append(f"Some social presence: {social_count} platforms")
                    score_adjustment += 5
                else:
                    risk_factors.append("No social media presence")
                    score_adjustment -= 10
            
            # Check for audit information
            audit_info = token.get('audit_info', '')
            if audit_info:
                if any(firm in audit_info.lower() for firm in self.legitimacy_indicators['audit_firms']):
                    legitimacy_factors.append("Audited by recognized firm")
                    score_adjustment += 20
                else:
                    legitimacy_factors.append("Has audit information")
                    score_adjustment += 10
            
            return {
                'score_adjustment': score_adjustment,
                'risk_factors': risk_factors,
                'legitimacy_factors': legitimacy_factors
            }
            
        except Exception as e:
            logging.error(f"Error in social presence analysis: {e}")
            return {
                'score_adjustment': 0,
                'risk_factors': [],
                'legitimacy_factors': []
            }
    
    def _get_recommendation(self, security_score: float, risk_factors: List[str]) -> str:
        """Generate trading recommendation based on security analysis"""
        if security_score >= 80:
            return "SAFE - Low risk, suitable for investment"
        elif security_score >= 60:
            return "CAUTION - Medium risk, do your own research"
        elif security_score >= 40:
            return "HIGH RISK - Only for experienced traders"
        elif security_score >= 20:
            return "VERY HIGH RISK - Avoid unless expert"
        else:
            return "AVOID - Likely scam or rug pull"
    
    def is_token_safe(self, token: Dict, min_security_score: float = 60) -> bool:
        """Quick check if token meets minimum security requirements"""
        try:
            analysis = self.analyze_token_security(token)
            return analysis['security_score'] >= min_security_score and not analysis['is_likely_rug']
        except Exception as e:
            logging.error(f"Error checking token safety: {e}")
            return False
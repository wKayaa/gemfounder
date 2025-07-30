"""
Telegram notification system for sending token alerts
"""
import requests
import logging
from typing import Dict, List, Optional
import config
from utils import format_currency, format_percentage, sanitize_token_name, truncate_address, get_timestamp

class TelegramNotifier:
    """Handles Telegram bot notifications"""
    
    def __init__(self, bot_token: str = None, chat_id: str = None):
        self.bot_token = bot_token or config.TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or config.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        if not self.bot_token or not self.chat_id:
            logging.warning("Telegram bot token or chat ID not configured. Notifications will be logged only.")
    
    def send_token_alert(self, token: Dict) -> bool:
        """Send a formatted token alert to Telegram"""
        try:
            message = self._format_token_message(token)
            return self._send_message(message)
        except Exception as e:
            logging.error(f"Error sending token alert: {e}")
            return False
    
    def send_summary_report(self, scan_summary: Dict) -> bool:
        """Send a scan summary report"""
        try:
            message = self._format_summary_message(scan_summary)
            return self._send_message(message)
        except Exception as e:
            logging.error(f"Error sending summary report: {e}")
            return False
    
    def _format_token_message(self, token: Dict) -> str:
        """Format token data into a readable Telegram message"""
        try:
            # Sanitize text for Telegram
            name = sanitize_token_name(token.get('name', 'Unknown'))
            symbol = sanitize_token_name(token.get('symbol', 'UNK'))
            
            # Basic token info
            message = f"🚀 *GEM ALERT* 🚀\n\n"
            message += f"💎 *{name}* \\({symbol}\\)\n"
            message += f"📊 Score: *{token.get('score', 0):.1f}/100*\n\n"
            
            # Market data
            price = token.get('price_usd', 0)
            market_cap = token.get('market_cap', 0)
            volume_24h = token.get('volume_24h', 0)
            
            message += f"💰 Price: *{format_currency(price)}*\n"
            message += f"📈 Market Cap: *{format_currency(market_cap)}*\n"
            message += f"📊 Volume 24h: *{format_currency(volume_24h)}*\n"
            
            # Price changes
            price_change_1h = token.get('price_change_1h', 0)
            price_change_24h = token.get('price_change_24h', 0)
            
            if price_change_1h != 0:
                emoji = "📈" if price_change_1h > 0 else "📉"
                message += f"{emoji} 1h Change: *{format_percentage(price_change_1h)}*\n"
            
            if price_change_24h != 0:
                emoji = "📈" if price_change_24h > 0 else "📉"
                message += f"{emoji} 24h Change: *{format_percentage(price_change_24h)}*\n"
            
            # Additional info
            chain = token.get('chain', '')
            dex = token.get('dex', '')
            if chain:
                message += f"⛓️ Chain: *{chain.upper()}*\n"
            if dex:
                message += f"🔄 DEX: *{dex.upper()}*\n"
            
            # Liquidity info
            liquidity = token.get('liquidity_usd', 0)
            if liquidity > 0:
                message += f"💧 Liquidity: *{format_currency(liquidity)}*\n"
            
            # Contract address
            contract_address = token.get('contract_address', '')
            if contract_address:
                truncated = truncate_address(contract_address)
                message += f"📄 Contract: `{contract_address}`\n"
            
            # Links
            message += "\n🔗 *Quick Links:*\n"
            
            # DexScreener link
            if token.get('url'):
                message += f"[DexScreener]({token['url']})\n"
            elif contract_address and chain:
                dex_url = f"https://dexscreener.com/{chain}/{contract_address}"
                message += f"[DexScreener]({dex_url})\n"
            
            # Blockchain explorer
            if contract_address:
                if chain.lower() == 'bsc':
                    explorer_url = f"https://bscscan.com/token/{contract_address}"
                    message += f"[BSCScan]({explorer_url})\n"
                elif chain.lower() == 'ethereum':
                    explorer_url = f"https://etherscan.io/token/{contract_address}"
                    message += f"[Etherscan]({explorer_url})\n"
                elif chain.lower() == 'polygon':
                    explorer_url = f"https://polygonscan.com/token/{contract_address}"
                    message += f"[PolygonScan]({explorer_url})\n"
            
            # Score breakdown
            message += f"\n📊 *Score Breakdown:*\n"
            breakdown = token.get('score_breakdown', {})
            for category, score in breakdown.items():
                category_name = category.replace('_', ' ').title()
                message += f"• {category_name}: {score*100:.0f}%\n"
            
            # Timestamp
            message += f"\n⏰ {get_timestamp()}\n"
            
            # Warning
            message += f"\n⚠️ *DYOR \\- Not Financial Advice*"
            
            return message
            
        except Exception as e:
            logging.error(f"Error formatting token message: {e}")
            return f"Error formatting message for {token.get('symbol', 'unknown')}"
    
    def _format_summary_message(self, summary: Dict) -> str:
        """Format scan summary into a readable message"""
        try:
            message = f"📊 *Scan Summary Report*\n\n"
            
            message += f"🔍 Tokens Scanned: *{summary.get('tokens_scanned', 0)}*\n"
            message += f"✅ Passed Filters: *{summary.get('tokens_filtered', 0)}*\n"
            message += f"🚀 Notifications Sent: *{summary.get('notifications_sent', 0)}*\n"
            message += f"⏱️ Scan Duration: *{summary.get('scan_duration', 0):.1f}s*\n"
            
            # Add top scoring tokens if any
            top_tokens = summary.get('top_tokens', [])
            if top_tokens:
                message += f"\n🏆 *Top Scoring Tokens:*\n"
                for i, token in enumerate(top_tokens[:3], 1):
                    name = sanitize_token_name(token.get('symbol', 'UNK'))
                    score = token.get('score', 0)
                    message += f"{i}\\. {name}: {score:.1f}/100\n"
            
            message += f"\n⏰ {get_timestamp()}"
            
            return message
            
        except Exception as e:
            logging.error(f"Error formatting summary message: {e}")
            return "Error generating summary report"
    
    def _send_message(self, message: str) -> bool:
        """Send message to Telegram"""
        if not self.bot_token or not self.chat_id:
            logging.info(f"Telegram not configured. Message would be:\n{message}")
            return True
        
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'MarkdownV2',
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                logging.info("Telegram message sent successfully")
                return True
            else:
                logging.error(f"Telegram API error: {result.get('description', 'Unknown error')}")
                return False
                
        except Exception as e:
            logging.error(f"Error sending Telegram message: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test Telegram bot connection"""
        if not self.bot_token:
            logging.error("No Telegram bot token configured")
            return False
        
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                bot_info = result.get('result', {})
                logging.info(f"Telegram bot connected: {bot_info.get('username', 'Unknown')}")
                return True
            else:
                logging.error(f"Telegram bot test failed: {result.get('description', 'Unknown error')}")
                return False
                
        except Exception as e:
            logging.error(f"Error testing Telegram connection: {e}")
            return False
    
    def send_startup_message(self) -> bool:
        """Send bot startup notification"""
        message = f"🤖 *GemFinder Bot Started*\n\n"
        message += f"⏰ {get_timestamp()}\n"
        message += f"🔍 Scanning for gems between {format_currency(config.MIN_MARKET_CAP)} and {format_currency(config.MAX_MARKET_CAP)}\n"
        message += f"📊 Score threshold: {config.SCORE_THRESHOLD}/100\n"
        message += f"⏱️ Scan interval: {config.SCAN_INTERVAL_SECONDS}s"
        
        return self._send_message(message)
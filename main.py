"""
Main GemFinder Bot - Crypto token scanner and notifier
"""
import time
import logging
import sys
from typing import Dict, List
from datetime import datetime

# Import our modules
import config
from utils import setup_logging, get_timestamp
from scanner import TokenScanner
from filter import TokenFilter
from scoring import TokenScorer
from notifier import TelegramNotifier
from storage import TokenStorage

class GemFinderBot:
    """Main bot orchestrator"""
    
    def __init__(self):
        self.logger = setup_logging(config.LOG_FILE)
        self.scanner = TokenScanner()
        self.filter = TokenFilter()
        self.scorer = TokenScorer()
        self.notifier = TelegramNotifier()
        self.storage = TokenStorage(config.NOTIFIED_TOKENS_FILE)
        self.running = False
        
        self.logger.info("GemFinder Bot initialized")
    
    def start(self):
        """Start the bot main loop"""
        self.logger.info("Starting GemFinder Bot...")
        
        # Test Telegram connection
        if config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID:
            if self.notifier.test_connection():
                self.notifier.send_startup_message()
            else:
                self.logger.warning("Telegram connection failed, notifications will be logged only")
        
        self.running = True
        scan_count = 0
        
        try:
            while self.running:
                scan_count += 1
                self.logger.info(f"Starting scan #{scan_count}")
                
                scan_start_time = time.time()
                scan_results = self.run_scan_cycle()
                scan_duration = time.time() - scan_start_time
                
                # Log scan results
                self.logger.info(f"Scan #{scan_count} completed in {scan_duration:.1f}s")
                self.logger.info(f"Results: {scan_results}")
                
                # Store scan record
                scan_summary = {
                    'tokens_scanned': scan_results.get('tokens_scanned', 0),
                    'tokens_filtered': scan_results.get('tokens_filtered', 0),
                    'notifications_sent': scan_results.get('notifications_sent', 0),
                    'scan_duration': scan_duration
                }
                self.storage.add_scan_record(scan_summary)
                
                # Send summary every 10 scans
                if scan_count % 10 == 0:
                    self.send_summary_report(scan_summary)
                
                # Clean up old notifications periodically
                if scan_count % 50 == 0:
                    self.storage.cleanup_old_notifications()
                
                # Wait before next scan
                self.logger.info(f"Waiting {config.SCAN_INTERVAL_SECONDS}s before next scan...")
                time.sleep(config.SCAN_INTERVAL_SECONDS)
                
        except KeyboardInterrupt:
            self.logger.info("Bot stopped by user")
        except Exception as e:
            self.logger.error(f"Unexpected error in main loop: {e}")
        finally:
            self.stop()
    
    def run_scan_cycle(self) -> Dict:
        """Run a single scan cycle"""
        try:
            # Get active risk profile settings
            risk_profile = config.RISK_PROFILES.get(config.ACTIVE_RISK_PROFILE, config.RISK_PROFILES['balanced'])
            
            # Step 1: Scan for tokens
            self.logger.info("Scanning for new tokens...")
            tokens = self.scanner.scan_all_sources()
            
            if not tokens:
                self.logger.warning("No tokens found in scan")
                return {
                    'tokens_scanned': 0,
                    'tokens_filtered': 0,
                    'notifications_sent': 0
                }
            
            # Step 2: Apply filters with risk profile settings
            self.logger.info(f"Applying filters to {len(tokens)} tokens using '{config.ACTIVE_RISK_PROFILE}' risk profile...")
            self.filter.set_risk_profile(risk_profile)
            filtered_tokens = self.filter.apply_all_filters(tokens)
            
            if not filtered_tokens:
                self.logger.info("No tokens passed filtering criteria")
                return {
                    'tokens_scanned': len(tokens),
                    'tokens_filtered': 0,
                    'notifications_sent': 0
                }
            
            # Step 3: Score tokens
            self.logger.info(f"Scoring {len(filtered_tokens)} filtered tokens...")
            scored_tokens = self.scorer.score_tokens(filtered_tokens, risk_profile['score_threshold'])
            
            if not scored_tokens:
                self.logger.info(f"No tokens passed scoring threshold of {risk_profile['score_threshold']}")
                return {
                    'tokens_scanned': len(tokens),
                    'tokens_filtered': len(filtered_tokens),
                    'notifications_sent': 0
                }
            
            # Step 4: Limit notifications based on risk profile
            max_notifications = risk_profile.get('max_tokens_per_scan', 5)
            tokens_to_notify = scored_tokens[:max_notifications]
            
            # Step 5: Send notifications for new tokens
            notifications_sent = 0
            for token in tokens_to_notify:
                if self.should_notify_token(token):
                    if self.send_token_notification(token):
                        notifications_sent += 1
            
            return {
                'tokens_scanned': len(tokens),
                'tokens_filtered': len(filtered_tokens),
                'high_scoring_tokens': len(scored_tokens),
                'notifications_sent': notifications_sent,
                'risk_profile': config.ACTIVE_RISK_PROFILE,
                'score_threshold': risk_profile['score_threshold'],
                'top_tokens': scored_tokens[:5]  # Top 5 for summary
            }
            
        except Exception as e:
            self.logger.error(f"Error in scan cycle: {e}")
            return {
                'tokens_scanned': 0,
                'tokens_filtered': 0,
                'notifications_sent': 0,
                'error': str(e)
            }
    
    def should_notify_token(self, token: Dict) -> bool:
        """Check if we should send notification for this token"""
        try:
            contract_address = token.get('contract_address', '')
            
            # Skip if no contract address
            if not contract_address:
                # Use symbol as fallback for CoinGecko tokens
                symbol = token.get('symbol', '')
                if not symbol:
                    return False
                # Check by symbol instead
                return not self.storage.is_token_notified(f"symbol_{symbol.lower()}")
            
            # Check if already notified
            if self.storage.is_token_notified(contract_address):
                self.logger.debug(f"Token {token.get('symbol')} already notified, skipping")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking notification status: {e}")
            return False
    
    def send_token_notification(self, token: Dict) -> bool:
        """Send notification for a token and record it"""
        try:
            # Send Telegram notification
            if self.notifier.send_token_alert(token):
                # Record as notified
                contract_address = token.get('contract_address', '')
                if not contract_address:
                    # Use symbol as fallback
                    symbol = token.get('symbol', '')
                    if symbol:
                        contract_address = f"symbol_{symbol.lower()}"
                
                if contract_address:
                    self.storage.add_notified_token(contract_address, token)
                    self.logger.info(f"Successfully notified for token {token.get('symbol')} (score: {token.get('score', 0):.1f})")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error sending token notification: {e}")
            return False
    
    def send_summary_report(self, scan_summary: Dict):
        """Send periodic summary report"""
        try:
            # Add storage statistics
            stats = self.storage.get_statistics()
            scan_summary.update(stats)
            
            self.notifier.send_summary_report(scan_summary)
            self.logger.info("Summary report sent")
            
        except Exception as e:
            self.logger.error(f"Error sending summary report: {e}")
    
    def stop(self):
        """Stop the bot"""
        self.running = False
        self.logger.info("GemFinder Bot stopped")
    
    def run_single_scan(self):
        """Run a single scan for testing purposes"""
        self.logger.info("Running single scan...")
        results = self.run_scan_cycle()
        self.logger.info(f"Single scan results: {results}")
        return results

def main():
    """Main entry point"""
    import sys
    
    # Parse command line arguments
    args = sys.argv[1:]
    
    # Check for help
    if 'help' in args or '-h' in args or '--help' in args:
        print_usage()
        return
    
    # Check for risk profile setting
    risk_profile = None
    if '--conservative' in args:
        risk_profile = 'conservative'
        args.remove('--conservative')
    elif '--balanced' in args:
        risk_profile = 'balanced'
        args.remove('--balanced')
    elif '--aggressive' in args:
        risk_profile = 'aggressive'
        args.remove('--aggressive')
    
    # Set risk profile if specified
    if risk_profile:
        config.ACTIVE_RISK_PROFILE = risk_profile
        print(f"Using {risk_profile} risk profile")
    
    if len(args) > 0 and args[0] == "test":
        # Run single test scan
        bot = GemFinderBot()
        print(f"Running test scan with risk profile: {config.ACTIVE_RISK_PROFILE}")
        bot.run_single_scan()
    else:
        # Run continuous scanning
        bot = GemFinderBot()
        print(f"Starting GemFinder Bot with risk profile: {config.ACTIVE_RISK_PROFILE}")
        try:
            bot.start()
        except KeyboardInterrupt:
            print("\nBot stopped by user")

def print_usage():
    """Print usage information"""
    print("""
GemFinder Bot - Advanced Crypto Gem Scanner

Usage:
  python3 main.py [options] [command]

Commands:
  test          Run a single test scan
  (no command)  Run continuous scanning

Risk Profile Options:
  --conservative    Use conservative settings (safer, fewer alerts)
  --balanced        Use balanced settings (default)
  --aggressive      Use aggressive settings (higher risk, more opportunities)

Risk Profile Details:
  Conservative: $500k-$10M market cap, 60+ score threshold, max 3 alerts/scan
  Balanced:     $100k-$2M market cap, 45+ score threshold, max 5 alerts/scan  
  Aggressive:   $20k-$1M market cap, 35+ score threshold, max 10 alerts/scan

Examples:
  python3 main.py test --aggressive          # Test with aggressive profile
  python3 main.py --conservative             # Run with conservative profile
  python3 main.py test                       # Test with default profile

Configuration:
  Copy config_template.py to config_local.py and configure your API keys.
  Telegram notifications require TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID.
    """)

if __name__ == "__main__":
    main()
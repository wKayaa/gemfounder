"""
Local storage management for tracking notified tokens
"""
import json
import logging
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from utils import load_json_file, save_json_file, get_timestamp

class TokenStorage:
    """Manages local storage of notified tokens and historical data"""
    
    def __init__(self, filepath: str = "notified_tokens.json"):
        self.filepath = filepath
        self.data = self.load_data()
        
    def load_data(self) -> Dict:
        """Load token data from file"""
        default_structure = {
            "notified_tokens": {},
            "scan_history": [],
            "statistics": {
                "total_scans": 0,
                "total_notifications": 0,
                "last_scan": None
            }
        }
        return load_json_file(self.filepath, default_structure)
    
    def save_data(self) -> bool:
        """Save token data to file"""
        return save_json_file(self.filepath, self.data)
    
    def is_token_notified(self, token_address: str) -> bool:
        """Check if token has already been notified"""
        return token_address.lower() in self.data["notified_tokens"]
    
    def add_notified_token(self, token_address: str, token_data: Dict) -> bool:
        """Add token to notified list"""
        try:
            self.data["notified_tokens"][token_address.lower()] = {
                "token_data": token_data,
                "notified_at": get_timestamp(),
                "score": token_data.get("score", 0)
            }
            self.data["statistics"]["total_notifications"] += 1
            return self.save_data()
        except Exception as e:
            logging.error(f"Error adding notified token {token_address}: {e}")
            return False
    
    def get_notified_tokens(self) -> Dict:
        """Get all notified tokens"""
        return self.data["notified_tokens"]
    
    def add_scan_record(self, scan_summary: Dict) -> bool:
        """Add scan record to history"""
        try:
            scan_record = {
                "timestamp": get_timestamp(),
                "tokens_scanned": scan_summary.get("tokens_scanned", 0),
                "tokens_filtered": scan_summary.get("tokens_filtered", 0),
                "notifications_sent": scan_summary.get("notifications_sent", 0),
                "scan_duration": scan_summary.get("scan_duration", 0)
            }
            
            self.data["scan_history"].append(scan_record)
            self.data["statistics"]["total_scans"] += 1
            self.data["statistics"]["last_scan"] = get_timestamp()
            
            # Keep only last 100 scan records to prevent file bloat
            if len(self.data["scan_history"]) > 100:
                self.data["scan_history"] = self.data["scan_history"][-100:]
            
            return self.save_data()
        except Exception as e:
            logging.error(f"Error adding scan record: {e}")
            return False
    
    def cleanup_old_notifications(self, days: int = 7) -> int:
        """Remove notifications older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            old_tokens = []
            
            for address, data in self.data["notified_tokens"].items():
                notified_at = datetime.strptime(data["notified_at"], "%Y-%m-%d %H:%M:%S")
                if notified_at < cutoff_date:
                    old_tokens.append(address)
            
            for address in old_tokens:
                del self.data["notified_tokens"][address]
            
            if old_tokens:
                self.save_data()
                logging.info(f"Cleaned up {len(old_tokens)} old notifications")
            
            return len(old_tokens)
        except Exception as e:
            logging.error(f"Error cleaning up old notifications: {e}")
            return 0
    
    def get_statistics(self) -> Dict:
        """Get storage statistics"""
        return {
            "total_scans": self.data["statistics"]["total_scans"],
            "total_notifications": self.data["statistics"]["total_notifications"],
            "last_scan": self.data["statistics"]["last_scan"],
            "notified_tokens_count": len(self.data["notified_tokens"]),
            "scan_history_count": len(self.data["scan_history"])
        }
    
    def get_recent_scan_history(self, limit: int = 10) -> List[Dict]:
        """Get recent scan history"""
        return self.data["scan_history"][-limit:] if self.data["scan_history"] else []
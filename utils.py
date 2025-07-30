"""
Utility functions for the Crypto Gem Finder Bot
"""
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional

def setup_logging(log_file: str = "gemfinder.log") -> logging.Logger:
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def load_json_file(filepath: str, default: Any = None) -> Any:
    """Load data from JSON file with error handling"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return default or {}
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON file {filepath}: {e}")
        return default or {}

def save_json_file(filepath: str, data: Any) -> bool:
    """Save data to JSON file with error handling"""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        logging.error(f"Error saving JSON file {filepath}: {e}")
        return False

def format_currency(amount: float) -> str:
    """Format currency with appropriate suffixes"""
    if amount >= 1_000_000:
        return f"${amount/1_000_000:.2f}M"
    elif amount >= 1_000:
        return f"${amount/1_000:.1f}K"
    else:
        return f"${amount:.2f}"

def format_percentage(value: float) -> str:
    """Format percentage with sign"""
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f}%"

def get_timestamp() -> str:
    """Get current timestamp as string"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def rate_limit_delay(delay_seconds: float = 1.0):
    """Add delay to respect API rate limits"""
    time.sleep(delay_seconds)

def truncate_address(address: str, start: int = 6, end: int = 4) -> str:
    """Truncate blockchain address for display"""
    if len(address) <= start + end:
        return address
    return f"{address[:start]}...{address[-end:]}"

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values"""
    if old_value == 0:
        return 0
    return ((new_value - old_value) / old_value) * 100

def is_valid_address(address: str) -> bool:
    """Basic validation for blockchain addresses"""
    if not address or not isinstance(address, str):
        return False
    # Basic check for Ethereum-style addresses
    if address.startswith('0x') and len(address) == 42:
        return True
    return False

def sanitize_token_name(name: str) -> str:
    """Sanitize token name for safe display"""
    if not name:
        return "Unknown"
    # Remove potential markdown characters that could break Telegram formatting
    unsafe_chars = ['*', '_', '`', '[', ']', '(', ')', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    sanitized = name
    for char in unsafe_chars:
        sanitized = sanitized.replace(char, f'\\{char}')
    return sanitized
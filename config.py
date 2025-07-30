"""
Configuration settings for the Crypto Gem Finder Bot
"""

# API Configuration
DEXSCREENER_API_URL = "https://api.dexscreener.com/latest/dex"
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
BSCSCAN_API_URL = "https://api.bscscan.com/api"
ETHERSCAN_API_URL = "https://api.etherscan.io/api"
POLYGONSCAN_API_URL = "https://api.polygonscan.com/api"

# Scanning Configuration
SCAN_INTERVAL_SECONDS = 300  # 5 minutes
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
ENABLE_MOCK_DATA = True  # Enable mock data when APIs are unavailable

# Filtering Criteria
MIN_MARKET_CAP = 50000   # $50k (reduced from $100k to catch more gems)
MAX_MARKET_CAP = 1000000  # $1M (increased from $300k for more opportunities)
MIN_VOLUME_1H = 5000     # $5k minimum volume (reduced from $10k)
MIN_VOLUME_GROWTH = 15   # 15% growth threshold (reduced from 30%)
MIN_LIQUIDITY_LOCK = True

# Risk Profile Configuration
RISK_PROFILES = {
    'conservative': {
        'min_market_cap': 500000,      # $500k min
        'max_market_cap': 10000000,    # $10M max
        'min_volume_growth': 10,       # 10% growth
        'score_threshold': 60,         # Higher threshold
        'max_tokens_per_scan': 3       # Fewer notifications
    },
    'balanced': {
        'min_market_cap': 100000,      # $100k min
        'max_market_cap': 2000000,     # $2M max
        'min_volume_growth': 15,       # 15% growth
        'score_threshold': 45,         # Default threshold
        'max_tokens_per_scan': 5       # Moderate notifications
    },
    'aggressive': {
        'min_market_cap': 20000,       # $20k min (high risk)
        'max_market_cap': 1000000,     # $1M max
        'min_volume_growth': 5,        # 5% growth (lower barrier)
        'score_threshold': 35,         # Lower threshold
        'max_tokens_per_scan': 10      # More notifications
    }
}

# Default risk profile (can be changed by user)
ACTIVE_RISK_PROFILE = 'balanced'

# Scoring Configuration
SCORE_THRESHOLD = 45  # Reduced from 75 to find more opportunities
SCORE_WEIGHTS = {
    'market_cap': 0.15,      # 15% (reduced importance)
    'volume_growth': 0.35,   # 35% (increased - most important for gems)
    'liquidity_lock': 0.15,  # 15%
    'contract_security': 0.10, # 10% (less strict for new tokens)
    'whale_activity': 0.10,  # 10%
    'social_signals': 0.15   # 15% (increased for trending detection)
}

# Telegram Configuration
TELEGRAM_BOT_TOKEN = ""  # To be set by user
TELEGRAM_CHAT_ID = ""    # To be set by user

# Blockchain Configuration
SUPPORTED_CHAINS = {
    'bsc': {
        'name': 'Binance Smart Chain',
        'scanner_api': BSCSCAN_API_URL,
        'chain_id': 56
    },
    'ethereum': {
        'name': 'Ethereum',
        'scanner_api': ETHERSCAN_API_URL,
        'chain_id': 1
    },
    'polygon': {
        'name': 'Polygon',
        'scanner_api': POLYGONSCAN_API_URL,
        'chain_id': 137
    }
}

# Storage Configuration
NOTIFIED_TOKENS_FILE = "notified_tokens.json"
LOG_FILE = "gemfinder.log"

# Whale Detection Configuration
WHALE_THRESHOLD = 50000  # $50k+ transactions considered whale activity
WHALE_ADDRESSES = [
    # Known whale addresses can be added here
]
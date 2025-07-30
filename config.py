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

# Multiple Market Cap Tiers for Different Strategies
MARKET_CAP_TIERS = {
    'micro_gems': {'min': 10000, 'max': 100000},      # $10k-$100k: High risk, high reward
    'small_gems': {'min': 100000, 'max': 500000},     # $100k-$500k: Balanced risk/reward
    'mid_gems': {'min': 500000, 'max': 2000000},      # $500k-$2M: Lower risk, steady growth
    'trending': {'min': 50000, 'max': 5000000}        # $50k-$5M: For trending tokens
}

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
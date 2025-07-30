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

# Filtering Criteria
MIN_MARKET_CAP = 100000  # $100k
MAX_MARKET_CAP = 300000  # $300k
MIN_VOLUME_1H = 10000    # $10k minimum volume in last hour
MIN_VOLUME_GROWTH = 30   # 30% volume growth in 30 minutes
MIN_LIQUIDITY_LOCK = True

# Scoring Configuration
SCORE_THRESHOLD = 75  # Minimum score to trigger notification
SCORE_WEIGHTS = {
    'market_cap': 0.20,      # 20%
    'volume_growth': 0.25,   # 25%
    'liquidity_lock': 0.20,  # 20%
    'contract_security': 0.15, # 15%
    'whale_activity': 0.10,  # 10%
    'social_signals': 0.10   # 10%
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
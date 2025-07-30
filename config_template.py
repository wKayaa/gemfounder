# GemFinder Bot Configuration Template
# Copy this file to config_local.py and fill in your API keys

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Get from @BotFather on Telegram
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"     # Your chat ID or group chat ID

# Optional: Blockchain Explorer API Keys (for enhanced features)
BSCSCAN_API_KEY = ""        # Get from https://bscscan.com/apis
ETHERSCAN_API_KEY = ""      # Get from https://etherscan.io/apis
POLYGONSCAN_API_KEY = ""    # Get from https://polygonscan.com/apis

# Scanning Configuration (adjust as needed)
SCAN_INTERVAL_SECONDS = 300   # 5 minutes
SCORE_THRESHOLD = 75          # Minimum score to trigger notification

# Market Cap Filters (in USD)
MIN_MARKET_CAP = 100000      # $100k
MAX_MARKET_CAP = 300000      # $300k

# Volume Filters (in USD)
MIN_VOLUME_1H = 10000        # $10k minimum volume
MIN_VOLUME_GROWTH = 30       # 30% growth threshold
# 💎 GemFinder - Crypto Gem Scanner Bot

# 💎 GemFinder - Advanced Crypto Gem Scanner Bot

An intelligent Python bot that continuously scans for low market cap crypto tokens with high growth potential, featuring advanced rug pull detection and enhanced security analysis. Sends detailed Telegram notifications 24/7 when promising legitimate gems are discovered.

## 🎯 Enhanced Features

- **24/7 Continuous Operation**: Robust error handling and automatic recovery
- **Advanced Rug Pull Detection**: Multi-layered security analysis to avoid scams
- **Enhanced Token Discovery**: Multiple scanning sources including microcap gems
- **Intelligent Risk Profiles**: Conservative, Balanced, and Aggressive modes
- **Real-time Security Analysis**: Contract verification, liquidity analysis, and more
- **Smart Anti-Scam Filtering**: Suspicious name detection and trading pattern analysis
- **Adaptive Performance**: Dynamic wait times and error recovery
- **Easy Telegram Setup**: Interactive setup script for bot configuration

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/wKayaa/gemfounder.git
cd gemfounder

# Install dependencies
pip install -r requirements.txt

# Run setup
python setup.py
```

### 2. Easy Telegram Setup (Recommended)

```bash
# Run the interactive setup script
python3 telegram_setup.py
```

This will guide you through:
- Creating a Telegram bot with @BotFather
- Getting your bot token and chat ID
- Automatic configuration file creation
- Testing the setup

### 2. Manual Configuration (Alternative)

```bash
# Copy template and edit configuration
cp config_template.py config_local.py
nano config_local.py
```

Fill in your Telegram bot credentials:
- `TELEGRAM_BOT_TOKEN`: Get from [@BotFather](https://t.me/BotFather)
- `TELEGRAM_CHAT_ID`: Your user ID or group chat ID

### 3. Usage

```bash
# Test single scan
python3 main.py test

# Test with different risk profiles
python3 main.py test --aggressive    # More opportunities, higher risk
python3 main.py test --conservative  # Safer picks, fewer alerts

# Start continuous 24/7 scanning
python3 main.py

# Start with specific risk profile
python3 main.py --aggressive
```

## 🛡️ Security Features

GemFinder now includes advanced rug pull detection:

### Multi-Layer Security Analysis
- **Contract Verification**: Checks if smart contract is verified
- **Liquidity Analysis**: Evaluates liquidity ratios and lock status
- **Trading Pattern Detection**: Identifies pump & dump schemes
- **Name & Symbol Analysis**: Detects suspicious naming patterns
- **Social Presence Verification**: Checks website and social media legitimacy
- **Audit Information**: Recognizes tokens audited by reputable firms

### Risk Levels
- **SAFE** (80+ security score): Low risk, suitable for investment
- **CAUTION** (60-79): Medium risk, do your own research
- **HIGH RISK** (40-59): Only for experienced traders
- **VERY HIGH RISK** (20-39): Avoid unless expert
- **AVOID** (<20): Likely scam or rug pull

## 📊 Scoring Algorithm

The bot uses a weighted scoring system (0-100) based on:

| Criteria | Weight | Description |
|----------|---------|-------------|
| Market Cap Position | 20% | Sweet spot within $100k-$300k range |
| Volume & Growth | 25% | Trading volume and price momentum |
| Liquidity & Lock | 20% | Available liquidity and lock status |
| Contract Security | 15% | Verification and security indicators |
| Whale Activity | 10% | Large transaction detection |
| Social Signals | 10% | Community engagement metrics |

## 📁 Project Structure

```
gemfounder/
├── main.py                 # Main bot orchestrator with 24/7 operation
├── scanner.py              # Enhanced multi-blockchain token scanning
├── filter.py               # Advanced token filtering logic
├── scoring.py              # Intelligent scoring system
├── notifier.py             # Enhanced Telegram notification system
├── rug_detector.py         # Advanced rug pull detection module
├── storage.py              # Local data persistence
├── config.py               # Default configuration with risk profiles
├── utils.py                # Utility functions
├── telegram_setup.py       # Interactive Telegram bot setup script
├── requirements.txt        # Enhanced Python dependencies
├── config_template.py      # Configuration template
└── setup.py               # Setup script
```

## ⚙️ Configuration Options

### Scanning Settings
```python
SCAN_INTERVAL_SECONDS = 300    # Scan every 5 minutes
SCORE_THRESHOLD = 75           # Minimum score for notifications
```

### Market Filters
```python
MIN_MARKET_CAP = 100000        # $100k minimum
MAX_MARKET_CAP = 300000        # $300k maximum
MIN_VOLUME_1H = 10000          # $10k minimum volume
MIN_VOLUME_GROWTH = 30         # 30% growth requirement
```

### API Sources
- **DexScreener**: Real-time DEX data
- **CoinGecko**: Market data and rankings
- **BSCScan/Etherscan**: Contract verification
- **Telegram**: Push notifications

## 📱 Telegram Integration

### Setup Bot
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Create a new bot with `/newbot`
3. Get your bot token
4. Get your chat ID by messaging [@userinfobot](https://t.me/userinfobot)

### Notification Format
```
🚀 GEM ALERT 🚀

💎 SafeMoon (SAFEMOON)
📊 Score: 87.3/100

💰 Price: $0.00234
📈 Market Cap: $245K
📊 Volume 24h: $67K
📈 1h Change: +45.6%
📈 24h Change: +123.4%

⛓️ Chain: BSC
🔄 DEX: PancakeSwap
💧 Liquidity: $45K
📄 Contract: 0x8076...abc123

🛡️ Security Analysis:
🔒 Security Score: 85.2/100
⚠️ Risk Level: SAFE
💡 Recommendation: Low risk, suitable for investment

✅ Legitimacy Factors:
• Contract is verified
• Good liquidity ratio: 18.4%
• Has audit information

🔗 Quick Links:
[DexScreener](https://dexscreener.com/...)
[BSCScan](https://bscscan.com/...)

📊 Score Breakdown:
• Market Cap: 85%
• Volume Growth: 95%
• Liquidity Lock: 80%
• Contract Security: 90%
• Whale Activity: 75%
• Social Signals: 70%

⏰ 2024-01-15 14:30:25
⚠️ DYOR - Not Financial Advice
```

## 🔧 Advanced Usage

### Running as Service (Linux)
```bash
# Generate systemd service
python setup.py service

# Install and start
sudo systemctl enable gemfinder
sudo systemctl start gemfinder
sudo systemctl status gemfinder
```

### Log Monitoring
```bash
# View logs
tail -f gemfinder.log

# View systemd logs
journalctl -u gemfinder -f
```

### Custom Scoring
Modify `scoring.py` to adjust the scoring algorithm:

```python
SCORE_WEIGHTS = {
    'market_cap': 0.20,      # Adjust weights
    'volume_growth': 0.30,   # as needed
    'liquidity_lock': 0.15,
    'contract_security': 0.20,
    'whale_activity': 0.10,
    'social_signals': 0.05
}
```

## 📈 Future Enhancements

- [ ] Smart contract analysis (honeypot detection)
- [ ] Social sentiment analysis (Twitter, Reddit)
- [ ] Liquidity lock verification (Unicrypt integration)
- [ ] Multi-exchange support
- [ ] Portfolio tracking
- [ ] Paper trading simulation
- [ ] Machine learning predictions
- [ ] Web dashboard
- [ ] Mobile app

## ⚠️ Disclaimer

This bot is for educational and research purposes only. Cryptocurrency trading involves substantial risk. Always:

- Do Your Own Research (DYOR)
- Never invest more than you can afford to lose
- Verify all information independently
- This is not financial advice

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🐛 Support

- Create an issue for bugs or feature requests
- Join our [Telegram group](https://t.me/gemfinder_support) for support
- Check the [Wiki](https://github.com/wKayaa/gemfounder/wiki) for detailed guides

---

**Happy gem hunting! 💎🚀**
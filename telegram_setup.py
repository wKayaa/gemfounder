#!/usr/bin/env python3
"""
Interactive Telegram bot setup script
"""
import os
import sys
import requests
from typing import Optional

def get_telegram_bot_token() -> Optional[str]:
    """Get Telegram bot token with guidance"""
    print("\n🤖 TELEGRAM BOT TOKEN SETUP")
    print("=" * 50)
    print("To get a Telegram bot token:")
    print("1. Open Telegram and search for @BotFather")
    print("2. Send /newbot command")
    print("3. Follow the instructions to create your bot")
    print("4. Copy the token provided by BotFather")
    print("5. Paste it below")
    print()
    
    while True:
        token = input("Enter your Telegram bot token: ").strip()
        
        if not token:
            print("❌ Token cannot be empty!")
            continue
        
        # Basic token format validation
        if len(token.split(':')) != 2:
            print("❌ Invalid token format! Should be like: 123456789:ABCDEF...")
            continue
        
        # Test the token
        print("🔍 Testing bot token...")
        if test_bot_token(token):
            print("✅ Bot token is valid!")
            return token
        else:
            print("❌ Invalid bot token or bot is not accessible!")
            retry = input("Try again? (y/n): ").lower()
            if retry != 'y':
                return None

def test_bot_token(token: str) -> bool:
    """Test if bot token is valid"""
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                print(f"   Bot name: {bot_info.get('first_name', 'Unknown')}")
                print(f"   Username: @{bot_info.get('username', 'Unknown')}")
                return True
        
        return False
        
    except Exception as e:
        print(f"   Error testing token: {e}")
        return False

def get_chat_id(token: str) -> Optional[str]:
    """Get chat ID with guidance"""
    print("\n💬 CHAT ID SETUP")
    print("=" * 50)
    print("To get your chat ID:")
    print("1. Search for your bot in Telegram (use the username from above)")
    print("2. Send any message to your bot (like 'Hello')")
    print("3. Press Enter below to detect your chat ID automatically")
    print()
    print("Alternative method:")
    print("1. Search for @userinfobot in Telegram")
    print("2. Send any message to get your user ID")
    print("3. Enter the ID manually below")
    print()
    
    input("Press Enter after sending a message to your bot...")
    
    # Try to get chat ID automatically
    chat_id = get_chat_id_from_updates(token)
    
    if chat_id:
        print(f"✅ Detected chat ID: {chat_id}")
        return str(chat_id)
    else:
        print("❌ Could not detect chat ID automatically")
        print()
        manual_id = input("Enter your chat ID manually (or press Enter to skip): ").strip()
        
        if manual_id:
            if manual_id.lstrip('-').isdigit():  # Allow negative IDs for groups
                return manual_id
            else:
                print("❌ Invalid chat ID format!")
        
        return None

def get_chat_id_from_updates(token: str) -> Optional[int]:
    """Get chat ID from recent bot updates"""
    try:
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok') and data.get('result'):
                updates = data['result']
                if updates:
                    # Get the most recent chat ID
                    latest_update = updates[-1]
                    if 'message' in latest_update:
                        chat_id = latest_update['message']['chat']['id']
                        return chat_id
        
        return None
        
    except Exception as e:
        print(f"Error getting updates: {e}")
        return None

def create_config_file(token: str, chat_id: str) -> bool:
    """Create config_local.py file with the credentials"""
    config_content = f'''"""
Local configuration file for GemFinder Bot
This file contains your personal API keys and settings.
DO NOT commit this file to version control!
"""

# Telegram Configuration
TELEGRAM_BOT_TOKEN = "{token}"
TELEGRAM_CHAT_ID = "{chat_id}"

# You can override other settings here if needed
# For example:
# SCAN_INTERVAL_SECONDS = 180  # 3 minutes instead of 5
# ACTIVE_RISK_PROFILE = 'aggressive'  # or 'conservative', 'balanced'

# Risk Profile Overrides (optional)
# RISK_PROFILES = {{
#     'custom': {{
#         'min_market_cap': 50000,
#         'max_market_cap': 500000,
#         'min_volume_growth': 20,
#         'score_threshold': 50,
#         'max_tokens_per_scan': 7,
#         'min_security_score': 55
#     }}
# }}
'''
    
    try:
        with open('config_local.py', 'w') as f:
            f.write(config_content)
        
        print("✅ Created config_local.py successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating config file: {e}")
        return False

def update_main_config() -> bool:
    """Update main config.py to import from config_local.py if it exists"""
    config_import = '''
# Import local configuration if available
try:
    from config_local import *
    print("✅ Loaded local configuration")
except ImportError:
    print("⚠️  No local configuration found. Using default settings.")
    pass
'''
    
    try:
        # Read current config.py
        with open('config.py', 'r') as f:
            content = f.read()
        
        # Check if import is already there
        if 'from config_local import' in content:
            print("✅ Config already set up for local imports")
            return True
        
        # Add import at the end
        with open('config.py', 'a') as f:
            f.write(config_import)
        
        print("✅ Updated config.py to load local settings")
        return True
        
    except Exception as e:
        print(f"❌ Error updating config.py: {e}")
        return False

def test_final_setup(token: str, chat_id: str) -> bool:
    """Test the final setup by sending a test message"""
    print("\n🧪 TESTING SETUP")
    print("=" * 50)
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': '🎉 GemFinder Bot Setup Complete!\n\nYour bot is ready to find crypto gems! 💎\n\nRun: python3 main.py test',
            'parse_mode': 'Markdown'
        }
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Test message sent successfully!")
                print("   Check your Telegram to see the test message.")
                return True
        
        print("❌ Failed to send test message")
        return False
        
    except Exception as e:
        print(f"❌ Error sending test message: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 GemFinder Bot - Telegram Setup")
    print("=" * 50)
    print("This script will help you set up your Telegram bot for GemFinder.")
    print()
    
    # Get bot token
    token = get_telegram_bot_token()
    if not token:
        print("❌ Setup cancelled - no valid bot token provided")
        sys.exit(1)
    
    # Get chat ID
    chat_id = get_chat_id(token)
    if not chat_id:
        print("❌ Setup cancelled - no valid chat ID provided")
        sys.exit(1)
    
    # Create config file
    if not create_config_file(token, chat_id):
        print("❌ Setup failed - could not create config file")
        sys.exit(1)
    
    # Update main config
    if not update_main_config():
        print("❌ Setup failed - could not update main config")
        sys.exit(1)
    
    # Test setup
    if not test_final_setup(token, chat_id):
        print("⚠️  Setup completed but test message failed")
        print("   You can still try running the bot manually")
    
    print("\n🎉 SETUP COMPLETE!")
    print("=" * 50)
    print("Your GemFinder bot is now configured!")
    print()
    print("Next steps:")
    print("1. Run a test scan: python3 main.py test")
    print("2. Start the bot: python3 main.py")
    print("3. Check the README.md for more configuration options")
    print()
    print("Happy gem hunting! 💎🚀")

if __name__ == "__main__":
    main()
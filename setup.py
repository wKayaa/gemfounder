#!/usr/bin/env python3
"""
Setup script for GemFinder Bot
"""
import os
import sys

def setup_environment():
    """Setup the bot environment"""
    print("🚀 GemFinder Bot Setup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Check if config file exists
    if not os.path.exists('config_local.py'):
        print("\n📝 Creating configuration file...")
        print("Please copy config_template.py to config_local.py and fill in your API keys")
        print("\nRequired:")
        print("- Telegram Bot Token (get from @BotFather)")
        print("- Telegram Chat ID (your user ID or group ID)")
        print("\nOptional:")
        print("- Blockchain explorer API keys for enhanced features")
        return False
    
    print("✅ Configuration file found")
    
    # Try importing dependencies
    try:
        import requests
        print("✅ Dependencies installed")
    except ImportError:
        print("❌ Dependencies missing. Run: pip install -r requirements.txt")
        return False
    
    print("\n🎯 Setup complete!")
    print("\nUsage:")
    print("  python main.py          # Start continuous scanning")
    print("  python main.py test     # Run single test scan")
    
    return True

def create_systemd_service():
    """Create systemd service file for Linux systems"""
    service_content = f"""[Unit]
Description=GemFinder Crypto Bot
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'gemfinder')}
WorkingDirectory={os.getcwd()}
ExecStart=/usr/bin/python3 {os.path.join(os.getcwd(), 'main.py')}
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=gemfinder

[Install]
WantedBy=multi-user.target
"""
    
    print("\n🔧 Systemd service file content:")
    print("Save this to /etc/systemd/system/gemfinder.service")
    print("-" * 50)
    print(service_content)
    print("-" * 50)
    print("Then run:")
    print("  sudo systemctl enable gemfinder")
    print("  sudo systemctl start gemfinder")
    print("  sudo systemctl status gemfinder")

if __name__ == "__main__":
    if setup_environment():
        if len(sys.argv) > 1 and sys.argv[1] == "service":
            create_systemd_service()
    else:
        sys.exit(1)
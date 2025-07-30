#!/usr/bin/env python3
"""
Test script for GemFinder Bot components
"""
import sys
import logging
from datetime import datetime

# Import all modules to test
from utils import setup_logging, format_currency, format_percentage
from scanner import TokenScanner
from filter import TokenFilter
from scoring import TokenScorer
from notifier import TelegramNotifier
from storage import TokenStorage

def test_utils():
    """Test utility functions"""
    print("🧪 Testing Utilities...")
    
    # Test currency formatting
    assert format_currency(1234567) == "$1.23M"
    assert format_currency(12345) == "$12.3K"
    assert format_currency(123) == "$123.00"
    
    # Test percentage formatting
    assert format_percentage(12.34) == "+12.34%"
    assert format_percentage(-5.67) == "-5.67%"
    
    print("✅ Utilities test passed")

def test_storage():
    """Test storage functionality"""
    print("🧪 Testing Storage...")
    
    storage = TokenStorage("test_tokens.json")
    
    # Test adding token
    test_token = {
        "symbol": "TEST",
        "name": "Test Token",
        "score": 85
    }
    
    assert storage.add_notified_token("0x123", test_token)
    assert storage.is_token_notified("0x123")
    assert not storage.is_token_notified("0x456")
    
    print("✅ Storage test passed")

def test_scanner():
    """Test scanner functionality (limited without API keys)"""
    print("🧪 Testing Scanner...")
    
    scanner = TokenScanner()
    
    # Test DexScreener parsing (with mock data)
    mock_pair = {
        "baseToken": {"address": "0x123", "name": "Test", "symbol": "TEST"},
        "quoteToken": {"symbol": "USDT"},
        "priceUsd": "0.001",
        "marketCap": "150000",
        "volume": {"h24": "50000", "h1": "5000"},
        "priceChange": {"h1": "15", "h24": "30"},
        "liquidity": {"usd": "25000"},
        "chainId": "bsc",
        "dexId": "pancakeswap"
    }
    
    parsed = scanner._parse_dexscreener_pair(mock_pair)
    assert parsed is not None
    assert parsed["market_cap"] == 150000
    assert parsed["symbol"] == "TEST"
    
    print("✅ Scanner test passed")

def test_filter():
    """Test filtering functionality"""
    print("🧪 Testing Filter...")
    
    filter_engine = TokenFilter()
    
    # Test token that should pass
    good_token = {
        "market_cap": 200000,
        "volume_24h": 50000,
        "price_change_1h": 35,
        "symbol": "GOOD",
        "name": "Good Token",
        "price_usd": 0.001
    }
    
    # Test token that should fail (market cap too high)
    bad_token = {
        "market_cap": 500000,
        "volume_24h": 50000,
        "price_change_1h": 35,
        "symbol": "BAD",
        "name": "Bad Token",
        "price_usd": 0.001
    }
    
    filtered = filter_engine.apply_all_filters([good_token, bad_token])
    assert len(filtered) == 1
    assert filtered[0]["symbol"] == "GOOD"
    
    print("✅ Filter test passed")

def test_scorer():
    """Test scoring functionality"""
    print("🧪 Testing Scorer...")
    
    scorer = TokenScorer()
    
    test_token = {
        "market_cap": 200000,
        "volume_24h": 50000,
        "volume_1h": 5000,
        "price_change_1h": 25,
        "price_change_24h": 45,
        "liquidity_usd": 30000,
        "contract_address": "0x123",
        "verified": True,
        "source": "dexscreener"
    }
    
    score = scorer.calculate_score(test_token)
    assert 0 <= score <= 100
    assert "score_breakdown" in test_token
    
    print(f"   Test token scored: {score:.1f}/100")
    print("✅ Scorer test passed")

def test_notifier():
    """Test notification formatting (without sending)"""
    print("🧪 Testing Notifier...")
    
    # Create notifier without credentials for testing
    notifier = TelegramNotifier("", "")
    
    test_token = {
        "name": "Test Token",
        "symbol": "TEST",
        "score": 87.5,
        "price_usd": 0.00123,
        "market_cap": 245000,
        "volume_24h": 67000,
        "price_change_1h": 45.6,
        "price_change_24h": 123.4,
        "chain": "bsc",
        "dex": "pancakeswap",
        "liquidity_usd": 45000,
        "contract_address": "0x8076abc123",
        "score_breakdown": {
            "market_cap": 0.85,
            "volume_growth": 0.95,
            "liquidity_lock": 0.80,
            "contract_security": 0.90,
            "whale_activity": 0.75,
            "social_signals": 0.70
        }
    }
    
    message = notifier._format_token_message(test_token)
    assert "GEM ALERT" in message
    assert "TEST" in message
    assert "87.5/100" in message
    
    print("✅ Notifier test passed")

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting GemFinder Bot Tests")
    print("=" * 50)
    
    # Setup logging for tests
    setup_logging("test.log")
    
    try:
        test_utils()
        test_storage()
        test_scanner()
        test_filter()
        test_scorer()
        test_notifier()
        
        print("\n🎉 All tests passed!")
        print("The bot components are working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup test files
        import os
        try:
            os.remove("test_tokens.json")
            os.remove("test.log")
        except FileNotFoundError:
            pass
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
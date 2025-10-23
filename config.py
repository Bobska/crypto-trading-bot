"""
Configuration module for Crypto Trading Bot
Loads environment variables and validates required settings
Supports multiple trading profiles (conservative, balanced, aggressive)
"""
import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Parse command line arguments for profile selection
def get_profile_from_args() -> str:
    """Parse command line arguments to get profile name"""
    parser = argparse.ArgumentParser(description='Crypto Trading Bot')
    parser.add_argument('--profile', type=str, default='balanced',
                       choices=['conservative', 'balanced', 'aggressive'],
                       help='Trading profile to use (default: balanced)')
    
    # Parse only known args to avoid conflicts with other scripts
    args, _ = parser.parse_known_args()
    return args.profile

# Get active profile
ACTIVE_PROFILE = get_profile_from_args()

# Load environment variables from profile-specific .env file
profile_path = Path('profiles') / f'{ACTIVE_PROFILE}.env'

if profile_path.exists():
    load_dotenv(profile_path)
    print(f"📋 Loaded profile: {ACTIVE_PROFILE}")
else:
    # Fallback to default .env if profile doesn't exist
    load_dotenv()
    print(f"⚠️  Profile file not found: {profile_path}")
    print(f"   Using default .env file")
    ACTIVE_PROFILE = 'default'

# Safety flag - always use testnet for development
TESTNET = True

def get_env_var(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """Get environment variable with optional default and validation"""
    value = os.getenv(key, default)
    
    if required and (not value or value.strip() == ""):
        raise ValueError(f"Required environment variable '{key}' is not set or empty")
    
    return value

def get_bool_env(key: str, default: bool = False) -> bool:
    """Get boolean environment variable"""
    value = os.getenv(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')

def get_float_env(key: str, default: float = 0.0) -> float:
    """Get float environment variable with validation"""
    try:
        return float(os.getenv(key, str(default)))
    except ValueError:
        raise ValueError(f"Environment variable '{key}' must be a valid number")

def get_int_env(key: str, default: int = 0) -> int:
    """Get integer environment variable with validation"""
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        raise ValueError(f"Environment variable '{key}' must be a valid integer")

# API Configuration - Required
try:
    api_key = get_env_var("BINANCE_API_KEY", required=True)
    secret = get_env_var("BINANCE_SECRET", required=True)
    BINANCE_API_KEY: str = api_key if api_key else ""
    BINANCE_SECRET: str = secret if secret else ""
except ValueError as e:
    raise ValueError(f"Missing API credentials: {e}. Please check your .env file and ensure API keys are set.")

# Trading Settings with type conversion and defaults
symbol_val = get_env_var("SYMBOL", default="BTC/USDT")
SYMBOL: str = symbol_val if symbol_val else "BTC/USDT"
BUY_THRESHOLD = get_float_env("BUY_THRESHOLD", default=1.0)
SELL_THRESHOLD = get_float_env("SELL_THRESHOLD", default=1.0)
TRADE_AMOUNT = get_float_env("TRADE_AMOUNT", default=0.001)
CHECK_INTERVAL = get_int_env("CHECK_INTERVAL", default=30)

# AI Service Settings
ai_url = get_env_var("AI_API_URL", default="http://localhost:8000")
AI_API_URL: str = ai_url if ai_url else "http://localhost:8000"
AI_ENABLED = get_bool_env("AI_ENABLED", default=True)

# Validate numeric ranges
if BUY_THRESHOLD <= 0 or BUY_THRESHOLD > 100:
    raise ValueError("BUY_THRESHOLD must be between 0 and 100 percent")

if SELL_THRESHOLD <= 0 or SELL_THRESHOLD > 100:
    raise ValueError("SELL_THRESHOLD must be between 0 and 100 percent")

if TRADE_AMOUNT <= 0:
    raise ValueError("TRADE_AMOUNT must be positive")

if CHECK_INTERVAL < 1:
    raise ValueError("CHECK_INTERVAL must be at least 1 second")

# Print configuration status
mode = "TESTNET" if TESTNET else "LIVE TRADING"
profile_desc = get_env_var("PROFILE_DESCRIPTION", default="Custom configuration")

print(f"\n{'='*60}")
print(f"Crypto Trading Bot Configuration Loaded")
print(f"{'='*60}")
print(f"Profile: {ACTIVE_PROFILE.upper()}")
print(f"Description: {profile_desc}")
print(f"Mode: {mode}")
print(f"Symbol: {SYMBOL}")
print(f"Check Interval: {CHECK_INTERVAL}s")
print(f"Buy/Sell Thresholds: {BUY_THRESHOLD}%/{SELL_THRESHOLD}%")
print(f"Trade Amount: {TRADE_AMOUNT} BTC")
print(f"AI Enabled: {AI_ENABLED}")
print(f"{'='*60}\n")

if TESTNET:
    print("TESTNET MODE - No real money will be traded")
else:
    print("WARNING: LIVE TRADING MODE - Real money at risk!")
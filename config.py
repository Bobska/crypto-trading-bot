"""
Configuration module for Crypto Trading Bot
Loads environment variables and validates required settings
"""
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

# Safety flag - always use testnet for development
TESTNET = True

def get_env_var(key: str, default: Optional[str] = None, required: bool = False) -> str:
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
    BINANCE_API_KEY = get_env_var("BINANCE_API_KEY", required=True)
    BINANCE_SECRET = get_env_var("BINANCE_SECRET", required=True)
except ValueError as e:
    raise ValueError(f"Missing API credentials: {e}. Please check your .env file and ensure API keys are set.")

# Trading Settings with type conversion and defaults
SYMBOL = get_env_var("SYMBOL", default="BTC/USDT")
BUY_THRESHOLD = get_float_env("BUY_THRESHOLD", default=1.0)
SELL_THRESHOLD = get_float_env("SELL_THRESHOLD", default=1.0)
TRADE_AMOUNT = get_float_env("TRADE_AMOUNT", default=0.001)
CHECK_INTERVAL = get_int_env("CHECK_INTERVAL", default=30)

# AI Service Settings
AI_API_URL = get_env_var("AI_API_URL", default="http://localhost:8000")
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
print(f"Crypto Trading Bot Configuration Loaded")
print(f"Mode: {mode}")
print(f"Symbol: {SYMBOL}")
print(f"Check Interval: {CHECK_INTERVAL}s")
print(f"Buy/Sell Thresholds: {BUY_THRESHOLD}%/{SELL_THRESHOLD}%")
print(f"Trade Amount: {TRADE_AMOUNT}")
print(f"AI Enabled: {AI_ENABLED}")

if TESTNET:
    print("TESTNET MODE - No real money will be traded")
else:
    print("WARNING: LIVE TRADING MODE - Real money at risk!")
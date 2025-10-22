# Crypto Trading Bot

A Python-based cryptocurrency trading bot designed for automated grid trading strategies with Binance integration.

## Features

- **Testnet Support**: Safe development and testing environment
- **Grid Trading**: Automated buy/sell orders based on price thresholds
- **Configuration Management**: Environment-based settings with validation
- **Comprehensive Logging**: File and console logging with date-based rotation
- **AI Integration**: Optional AI service integration for enhanced trading decisions

## Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd crypto-trading-bot
```

### 2. Environment Configuration
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your testnet API keys from https://testnet.binance.vision/
```

### 3. Install Dependencies
```bash
pip install python-dotenv
```

### 4. Test Configuration
```bash
python -c "import config; print('Config loaded successfully')"
```

## Configuration

Edit `.env` file with your settings:

- **BINANCE_API_KEY**: Your Binance testnet API key
- **BINANCE_SECRET**: Your Binance testnet secret key
- **SYMBOL**: Trading pair (default: BTC/USDT)
- **BUY_THRESHOLD**: Price drop percentage to trigger buy (default: 1.0%)
- **SELL_THRESHOLD**: Price rise percentage to trigger sell (default: 1.0%)
- **TRADE_AMOUNT**: Amount to trade per order (default: 0.001 BTC)
- **CHECK_INTERVAL**: Seconds between price checks (default: 30)

## Modules

- **`config.py`**: Configuration loading and validation
- **`logger_setup.py`**: Logging configuration for file and console output

## Safety Features

- **Testnet Mode**: Hardcoded testnet flag prevents accidental live trading
- **Input Validation**: Comprehensive validation of all configuration parameters
- **Error Handling**: Clear error messages for configuration issues

## Development

This project follows strict development standards documented in `.github/DEVELOPMENT_STANDARDS.md`.

## License

[Add your license here]
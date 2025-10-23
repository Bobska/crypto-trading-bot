# 🤖 Crypto Trading Bot v1.0

An automated cryptocurrency trading bot that uses grid trading strategy with AI-powered trade analysis and recommendations.

## ✨ Features

- **Grid Trading Strategy**: Automated buy-low, sell-high execution based on percentage thresholds
- **AI Integration**: Real-time trade analysis and recommendations from AI advisor
- **Testnet Safety**: Runs exclusively on Binance Testnet - no real money at risk
- **Comprehensive Logging**: Detailed logs of all trades, decisions, and AI consultations
- **Smart Position Tracking**: Monitors current positions and calculates P&L
- **Graceful Error Handling**: Robust exception handling and recovery mechanisms
- **Real-time Status Display**: Clear visibility into bot performance and balance

## 📋 Requirements

- **Python**: 3.8 or higher
- **Python Packages**:
  - ccxt (cryptocurrency exchange library)
  - pandas (data analysis)
  - python-dotenv (environment variables)
  - requests (AI service communication)
  - tabulate (optional, for reports)
- **Binance Testnet Account**: For API keys
- **AI Service** (optional): For trade recommendations

## 🚀 Setup Instructions

### 1. Install Python Packages

```bash
pip install -r requirements.txt
```

### 2. Get Binance Testnet API Keys

1. Visit [Binance Testnet](https://testnet.binance.vision/)
2. Create a testnet account (no real funds needed)
3. Generate API Key and Secret Key
4. Save these keys securely

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Binance Testnet API Keys
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_SECRET=your_testnet_secret_key_here

# Trading Settings
SYMBOL=BTC/USDT
BUY_THRESHOLD=1.0
SELL_THRESHOLD=1.0
TRADE_AMOUNT=0.001
CHECK_INTERVAL=30

# AI Service Settings (optional)
AI_API_URL=http://localhost:8000
AI_ENABLED=true
```

### 4. Start AI Service (Optional)

If using the AI advisor feature:

```bash
# In a separate terminasl, start your AI service
cd path/to/ai-service
uvicorn api_server:app --reload --port 8000
```

Or set `AI_ENABLED=false` in `.env` to disable AI features.

## 💻 Usage

### Starting the Bot

```bash
python main.py
```

The bot will:
1. Display a startup banner
2. Connect to Binance Testnet
3. Show your starting balance
4. Display strategy settings
5. Begin monitoring and trading

### Stopping the Bot

Press `Ctrl+C` to gracefully shut down the bot. It will:
- Complete the current iteration
- Send a daily summary to AI (if enabled)
- Display final statistics
- Exit cleanly

### Monitoring the Bot

Use the monitoring utility to watch bot activity without seeing all details:

```bash
python monitor.py
```

The monitor displays:
- Last 20 lines of log activity
- Total trades today (buy/sell breakdown)
- Last price checked and current position
- Account balance and win rate
- Auto-refreshes every 60 seconds
- Exit with `Ctrl+C`

**Tip:** Run `monitor.py` in a separate terminal while the bot is running!

### Viewing Performance Dashboard

Get comprehensive analytics with visual charts:

```bash
python dashboard.py
```

The dashboard shows:
- Total P&L and win/loss statistics
- Best and worst trades with details
- Hourly trading activity bar chart
- Complete trading history analysis
- Color-coded profit/loss display
- Auto-refreshes every 5 minutes

### Exporting Trade History

Export trades to CSV for Excel analysis:

```bash
python export_trades.py
```

Generates `trades_history.csv` with:
- Buy/sell dates and times
- Entry and exit prices
- P&L in dollars and percentages
- Win/Loss status per trade
- Trade duration in minutes
- Complete performance summary

### What to Expect

The bot will:
- Check prices every 30 seconds (configurable)
- Generate BUY signals when price drops by threshold percentage
- Generate SELL signals when price rises by threshold percentage
- Consult AI advisor before executing trades (if enabled)
- Execute trades automatically
- Log all activities to `logs/trades_YYYYMMDD.log`

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Recommended |
|----------|-------------|---------|-------------|
| `BINANCE_API_KEY` | Testnet API key | Required | From testnet.binance.vision |
| `BINANCE_SECRET` | Testnet secret key | Required | From testnet.binance.vision |
| `SYMBOL` | Trading pair | `BTC/USDT` | Any available pair |
| `BUY_THRESHOLD` | Buy trigger (% drop) | `1.0` | Start with 1-2% |
| `SELL_THRESHOLD` | Sell trigger (% rise) | `1.0` | Start with 1-2% |
| `TRADE_AMOUNT` | Amount per trade | `0.001` | Small amount for testing |
| `CHECK_INTERVAL` | Seconds between checks | `30` | 30-60 recommended |
| `AI_API_URL` | AI service endpoint | `http://localhost:8000` | Your AI server |
| `AI_ENABLED` | Enable AI advisor | `true` | `false` if no AI service |

### Strategy Tips

- **Start Conservative**: Use 1-2% thresholds for initial testing
- **Test First**: Run for a few hours to understand behavior
- **Monitor Logs**: Check `logs/` directory for detailed activity
- **Adjust Gradually**: Fine-tune thresholds based on results
- **Consider Volatility**: Higher thresholds for volatile markets

## ⚠️ Safety Warnings

### 🔴 CRITICAL: TESTNET ONLY

- **This bot uses Binance TESTNET only**
- **Never use real Binance API keys**
- **No real money is involved**
- **This is for educational/testing purposes**

### Important Notes

- ⚠️ **Paper Trading**: This is simulated trading with fake money
- ⚠️ **Not Financial Advice**: This bot is for learning purposes only
- ⚠️ **No Guarantees**: Past performance doesn't indicate future results
- ⚠️ **Use at Your Own Risk**: Always verify testnet mode is active
- ⚠️ **Never Use Live Keys**: Double-check you're using testnet keys

### Before Running

✅ Verify you're using **testnet.binance.vision** API keys  
✅ Check that config output shows "Running on TESTNET"  
✅ Confirm you see "TESTNET MODE" in the logs  
✅ Start with small trade amounts  
✅ Monitor the first few trades closely  

## 📁 Project Structure

```
crypto-trading-bot/
├── main.py              # Main entry point
├── bot.py               # TradingBot class (coordination)
├── exchange.py          # BinanceTestnet class (API integration)
├── strategy.py          # GridTradingStrategy class
├── indicators.py        # Technical analysis indicators
├── ai_advisor.py        # AIAdvisor class (optional)
├── config.py            # Configuration loader
├── logger_setup.py      # Logging configuration
├── banner.py            # Startup banner display
├── monitor.py           # Real-time monitoring utility
├── dashboard.py         # Performance analytics dashboard
├── export_trades.py     # CSV trade history export
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create this)
├── .gitignore          # Git ignore rules
├── logs/               # Trading logs (auto-created)
│   └── trades_*.log    # Daily log files
└── .github/            # Development standards
    └── DEVELOPMENT_STANDARDS.md
```

## 📊 Example Output

```
╔══════════════════════════════════════════════════════════╗
║          🤖 CRYPTO TRADING BOT v1.0 🤖                  ║
║            Grid Trading with AI Advisor                 ║
║              Running on TESTNET 💰                      ║
╚══════════════════════════════════════════════════════════╝

💰 Starting Balance:
   USDT: $10,000.00
   BTC:  1.000000

📊 Strategy Settings:
   Symbol: BTC/USDT
   Buy Threshold: 1.0%
   Sell Threshold: 1.0%
   Trade Amount: 0.001 BTC

🚀 Trading Bot is now running!
Press Ctrl+C to stop
```

## 🤝 Contributing

This project follows strict development standards. Please review:
- `.github/DEVELOPMENT_STANDARDS.md` for coding guidelines
- Conventional commit messages required
- All changes must be tested on testnet

## 📝 License

This project is for educational purposes only. Use at your own risk.

## 🆘 Troubleshooting

### Bot won't start
- Check your API keys are correct
- Verify `.env` file exists and is properly formatted
- Ensure all packages are installed: `pip install -r requirements.txt`

### No trades executing
- Check if price is moving enough to trigger thresholds
- Try lowering BUY_THRESHOLD and SELL_THRESHOLD to 0.5%
- Review logs in `logs/` directory for details

### AI service errors
- Make sure AI service is running on correct port
- Set `AI_ENABLED=false` to run without AI
- Check AI_API_URL matches your service endpoint

### Connection errors
- Confirm internet connection is stable
- Verify Binance Testnet is accessible
- Check firewall isn't blocking connections

## 📚 Additional Resources

- [Binance Testnet](https://testnet.binance.vision/) - Get API keys
- [CCXT Documentation](https://docs.ccxt.com/) - Exchange library docs
- [Grid Trading Guide](https://www.binance.com/en/blog/strategy/what-is-grid-trading-and-how-to-use-it-421499824684903688) - Strategy explanation

---

**Remember: This is a TESTNET trading bot. Never use real API keys or real money!**
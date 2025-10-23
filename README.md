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

### Bot buys when it should sell (Position Mismatch)

**Symptoms:**
- Bot holds BTC but tries to buy more
- Bot holds USDT but tries to sell
- Target price display is wrong

**Solutions:**

1. **Check bot_state.json exists and has correct position:**
   ```powershell
   Get-Content bot_state.json
   ```
   Should show:
   ```json
   {
     "position": "BTC",     # or "USDT"
     "last_buy_price": 107000.0,
     "last_sell_price": 108071.39
   }
   ```

2. **Verify balance detection logs:**
   Check `logs/` for messages like:
   ```
   🔍 Balance check: Detected BTC holdings (1.011000), overriding position to BTC
   State loaded - Position: BTC, Last Buy: $107,000.00
   Starting with position: BTC
   ```

3. **Check actual balance:**
   ```powershell
   python -c "from exchange import BinanceTestnet; import config; e = BinanceTestnet(config.BINANCE_API_KEY, config.BINANCE_SECRET); print(e.get_balance())"
   ```

4. **Reset state if corrupted:**
   ```powershell
   Remove-Item bot_state.json -Force
   python main.py  # Will create fresh state based on balance
   ```

5. **Verify position matches actual BTC balance:**
   - If BTC balance > 0.0001: Position should be "BTC"
   - If BTC balance ≤ 0.0001: Position should be "USDT"

### State file not saving

**Symptoms:**
- Bot forgets position after restart
- No bot_state.json file created
- Same trades repeat after restart

**Solutions:**

1. **Check write permissions:**
   ```powershell
   # Verify you can create files in the directory
   "test" | Out-File -FilePath test.txt
   Remove-Item test.txt
   ```

2. **Check logs for "State saved" message:**
   ```
   2025-10-23 15:06:18 - TradingBot - INFO - State saved
   ```
   Should appear after:
   - Bot initialization
   - Every successful trade
   - Bot shutdown

3. **Verify save_state() is called:**
   - Check `bot.py` has `self.save_state()` in:
     - End of `__init__()` method
     - After successful buy in `execute_trade()`
     - After successful sell in `execute_trade()`
     - In `stop()` method before shutdown

4. **Check for error messages:**
   Look for: `Failed to save state: <error message>`

### Position detection wrong

**Symptoms:**
- Bot detects wrong position on startup
- "No BTC detected" but you have BTC
- "Detected BTC holdings" but you have none

**Solutions:**

1. **Verify 0.0001 threshold is reasonable:**
   - 0.0001 BTC ≈ $10 (at $100k BTC)
   - Balances below this are considered "dust" and treated as zero
   - Adjust threshold in `bot.py` if trading smaller amounts

2. **Check balance detection logs:**
   Look for warnings in logs:
   ```
   🔍 Balance check: Detected BTC holdings (1.011000), overriding position to BTC
   ```
   or
   ```
   🔍 Balance check: No BTC detected (0.000050), overriding position to USDT
   ```

3. **Test balance detection:**
   ```powershell
   python -c "from exchange import BinanceTestnet; import config; e = BinanceTestnet(config.BINANCE_API_KEY, config.BINANCE_SECRET); b = e.get_balance(); print(f'BTC: {b[\"BTC\"]:.8f}, USDT: {b[\"USDT\"]:.2f}')"
   ```

4. **Manual state override:**
   If automatic detection fails, manually set state:
   ```powershell
   '{"position": "BTC", "last_buy_price": 107000.0, "last_sell_price": 0.0}' | Set-Content -Path bot_state.json
   ```

### Target prices not showing

**Symptoms:**
- Status display missing target price line
- Shows "Waiting for first buy opportunity" when position is BTC

**Solutions:**

1. **Check last_buy_price or last_sell_price:**
   ```powershell
   Get-Content bot_state.json
   ```
   - If position is BTC, need `last_buy_price` (not null)
   - If position is USDT after sell, need `last_sell_price` (not null)

2. **Set reference price manually:**
   ```powershell
   # If holding BTC, set a buy price reference
   '{"position": "BTC", "last_buy_price": 107000.0, "last_sell_price": 0.0}' | Set-Content -Path bot_state.json
   ```

3. **Restart bot to recalculate targets**

### AI service errors
- Make sure AI service is running on correct port
- Set `AI_ENABLED=false` to run without AI
- Check AI_API_URL matches your service endpoint

### Connection errors
- Confirm internet connection is stable
- Verify Binance Testnet is accessible
- Check firewall isn't blocking connections

## ✅ State Persistence Summary

After implementing state persistence features:
- ✅ **Bot remembers position between restarts** - No data loss
- ✅ **Bot auto-detects position from balance** - Self-healing on startup
- ✅ **Bot shows target prices for next trade** - Clear visibility
- ✅ **State persists in bot_state.json file** - Automatic backups
- ✅ **No more buying when it should sell!** - Position tracking works

## 📚 Additional Resources

- [Binance Testnet](https://testnet.binance.vision/) - Get API keys
- [CCXT Documentation](https://docs.ccxt.com/) - Exchange library docs
- [Grid Trading Guide](https://www.binance.com/en/blog/strategy/what-is-grid-trading-and-how-to-use-it-421499824684903688) - Strategy explanation

---

**Remember: This is a TESTNET trading bot. Never use real API keys or real money!**
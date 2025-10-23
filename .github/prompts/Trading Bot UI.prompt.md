---
mode: agent
---
🔧 STEP 1: Add API Endpoints to Bot
First, we need the bot to expose data via API.

Copilot Prompt for bot_api.py:
Create bot_api.py that adds FastAPI endpoints to control the trading bot:

Import requirements:
- from fastapi import FastAPI, HTTPException
- from fastapi.middleware.cors import CORSMiddleware
- import bot, config, exchange, strategy
- from datetime import datetime
- import json

Create FastAPI app:
- app = FastAPI(title="Trading Bot API")
- Enable CORS for all origins (for local HTML access)

Global variable:
- trading_bot = None  # Will store bot instance

Endpoint: GET /api/status
- Returns current bot status as JSON:
  * bot_running: boolean
  * symbol: string
  * current_price: float (get from exchange)
  * position: string ('USDT' or 'BTC')
  * balance: dict (USDT and BTC amounts)
  * last_updated: timestamp
- If bot not running, return minimal status
- Handle errors gracefully

Endpoint: GET /api/stats
- Returns trading statistics:
  * total_trades: int
  * wins: int
  * losses: int
  * win_rate: float
  * last_buy_price: float or null
  * last_sell_price: float or null
- Gets data from strategy.get_stats()

Endpoint: GET /api/trades/recent
- Returns last 10 trades from logs
- Parse log files for BUY/SELL entries
- Return array of trade objects:
  * timestamp, action, price, result
- Sort by most recent first

Endpoint: POST /api/bot/start
- Starts the trading bot in background thread
- Returns: {"status": "started", "message": "Bot started successfully"}
- If already running: return 400 error

Endpoint: POST /api/bot/stop
- Stops the trading bot gracefully
- Returns: {"status": "stopped", "message": "Bot stopped successfully"}

Add at bottom:
- if __name__ == "__main__":
- import uvicorn
- uvicorn.run(app, host="0.0.0.0", port=8002)
- Comment: Run alongside main bot on different port
Test the API:
bash# Terminal 1: Run your bot normally
python main.py

# Terminal 2: Run API server
python bot_api.py

# Terminal 3: Test endpoint
curl http://localhost:8002/api/status

🔧 STEP 2: Create Simple HTML Dashboard

Copilot Prompt for ui/dashboard.html:
Create a single-file HTML dashboard for crypto trading bot:

HTML structure:
- <!DOCTYPE html> with UTF-8 charset
- Title: "Crypto Trading Bot Dashboard"
- Include inline CSS (dark theme, modern design)
- Include inline JavaScript (no external dependencies)

CSS styling (in <style> tag):
- Dark theme: background #1a1a2e, text #eee
- Modern card-based layout
- Grid layout for status cards
- Table styling for trades
- Responsive design (works on mobile)
- Status indicators: 🟢 green for running, 🔴 red for stopped
- Color-coded P&L: green for profit, red for loss

JavaScript functionality (in <script> tag):
- API_URL = 'http://localhost:8002/api'
- Function fetchStatus(): gets /api/status
- Function fetchStats(): gets /api/stats
- Function fetchRecentTrades(): gets /api/trades/recent
- Function updateDashboard(): updates all UI elements
- Function formatPrice(price): adds commas and $ sign
- Function formatPercent(pct): adds % and + sign
- Auto-refresh every 5 seconds: setInterval(updateDashboard, 5000)
- Run updateDashboard() on page load

HTML layout:
- Header: "🤖 Crypto Trading Bot Dashboard"
- Status Section:
  * Bot Status (running/stopped with emoji)
  * Symbol (BTC/USDT)
  * Current Price (formatted)
  * Position (USDT or BTC)
  * Last Updated (timestamp)
- Balance Cards (3 columns):
  * USDT Balance
  * BTC Balance
  * Combined Value
- Statistics Cards (3 columns):
  * Total Trades
  * Win Rate (percentage)
  * Today's P&L
- Recent Trades Table:
  * Columns: Time, Action, Price, Result
  * Last 10 trades
  * Color-coded wins/losses
- Footer: "Auto-refreshes every 5 seconds"

Error handling:
- Show error message if API unreachable
- Display "Connecting..." during first load
- Handle missing data gracefully

✅ VERSION 1.0 CHECKPOINT
Test it works:

✅ Bot running: python main.py (Terminal 1)
✅ API running: python bot_api.py (Terminal 2)
✅ Open ui/dashboard.html in Chrome/Firefox
✅ See live data refreshing every 5 seconds
✅ Make a trade, see it appear in dashboard

What you have now:

View-only dashboard
Live updates (5-second refresh)
Zero setup required
Works immediately

Limitations:

Can't control bot (start/stop)
Can't change settings
No history beyond 10 trades
Manual refresh required (not instant)

Time to complete: 2-3 hours
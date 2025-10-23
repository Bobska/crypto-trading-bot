# Trading Bot Dashboard

A real-time web dashboard for monitoring and controlling the crypto trading bot.

## Features

- **Live Status Monitoring**: Current price, position, balances
- **Trading Statistics**: Win rate, total trades, P&L
- **Recent Trades**: Last 10 trades with results
- **Auto-Refresh**: Updates every 5 seconds
- **Dark Theme**: Modern, responsive design
- **Zero Setup**: Single HTML file, no build process

## Quick Start

### 1. Install Dependencies

```bash
pip install fastapi uvicorn
```

### 2. Start the API Server

```bash
python bot_api.py
```

The API will start on http://localhost:8002

### 3. Open Dashboard

Simply open `ui/dashboard.html` in your browser:

- **Chrome/Edge**: `File > Open` or drag the file into browser
- **Direct path**: `file:///C:/dev-projects/crypto-trading-bot/ui/dashboard.html`

The dashboard will automatically connect to the API and start displaying live data.

## API Endpoints

### GET /api/status
Returns current bot status:
```json
{
  "bot_running": false,
  "symbol": "BTC/USDT",
  "current_price": 109737.65,
  "position": "USDT",
  "balance": {
    "USDT": 9359.07,
    "BTC": 1.006
  },
  "last_updated": "2025-10-23T21:33:50",
  "profile": "balanced"
}
```

### GET /api/stats
Returns trading statistics:
```json
{
  "total_trades": 13,
  "wins": 6,
  "losses": 7,
  "win_rate": 46.2,
  "last_buy_price": 108325.00,
  "last_sell_price": 109626.41
}
```

### GET /api/trades/recent
Returns last 10 trades:
```json
[
  {
    "timestamp": "2025-10-23 20:15:45",
    "action": "SELL",
    "price": 102440.00,
    "result": "+$2,440.00 (+2.44%)"
  }
]
```

### POST /api/bot/start
Starts the trading bot in background:
```json
{
  "status": "started",
  "message": "Bot started successfully"
}
```

### POST /api/bot/stop
Stops the trading bot:
```json
{
  "status": "stopped",
  "message": "Bot stopped successfully"
}
```

## Usage Scenarios

### Scenario 1: Monitor Running Bot

```bash
# Terminal 1: Run your bot
python main.py

# Terminal 2: Start API server
python bot_api.py

# Browser: Open dashboard
# file:///path/to/ui/dashboard.html
```

The dashboard will show real-time data from the running bot.

### Scenario 2: Control Bot via API

```bash
# Start API server only
python bot_api.py

# Start bot via API
curl -X POST http://localhost:8002/api/bot/start

# Monitor in dashboard
# Open ui/dashboard.html

# Stop bot via API
curl -X POST http://localhost:8002/api/bot/stop
```

## Dashboard Components

### Status Section
- Bot running status with live indicator
- Active profile badge
- Current symbol and price
- Current position (USDT or BTC)
- Last update timestamp

### Balance Cards
- USDT balance
- BTC balance
- Total value in USD

### Statistics Cards
- Total completed trades
- Win rate percentage
- Wins vs losses breakdown
- Last buy and sell prices

### Recent Trades Table
- Last 10 trades
- Timestamp, action, price
- Profit/loss for completed pairs
- Color-coded results

## Troubleshooting

### Dashboard shows "Connecting..."

**Problem**: Dashboard can't reach API server

**Solutions**:
1. Verify API is running: `curl http://localhost:8002/api/status`
2. Check port 8002 is not in use: `netstat -ano | findstr :8002`
3. Check browser console for CORS errors (F12)

### API returns 500 errors

**Problem**: API can't connect to exchange or load config

**Solutions**:
1. Verify .env file exists with API keys
2. Check profile file exists in profiles/
3. Test exchange connection: `python -c "import config; from exchange import BinanceTestnet; e = BinanceTestnet(config.BINANCE_API_KEY, config.BINANCE_SECRET); print(e.get_balance())"`

### No trades showing

**Problem**: No log files or trades recorded yet

**Solutions**:
1. Run the bot to generate trades: `python main.py`
2. Check logs directory exists: `ls logs/`
3. Verify log pattern matches: Look for "BUY RECORDED" or "SELL RECORDED" in logs

### Bot won't start via API

**Problem**: Bot already running or config error

**Solutions**:
1. Stop any running bot instances
2. Check if bot is already running: Check /api/status
3. Review API logs for error messages
4. Verify config is valid: `python -c "import config; print(config.SYMBOL)"`

## API Documentation

FastAPI provides automatic interactive docs:

- **Swagger UI**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc

Use these to:
- Test endpoints interactively
- View request/response schemas
- Try starting/stopping the bot

## Development

### Running on Different Port

Edit `bot_api.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8003)  # Change port
```

Update dashboard URL in `ui/dashboard.html`:
```javascript
const API_URL = 'http://localhost:8003/api';  // Update port
```

### Adding New Endpoints

Add to `bot_api.py`:
```python
@app.get("/api/custom")
async def custom_endpoint():
    return {"data": "value"}
```

Update dashboard to call it:
```javascript
async function fetchCustom() {
    const response = await fetch(`${API_URL}/custom`);
    return await response.json();
}
```

### Customizing Dashboard

Edit `ui/dashboard.html`:
- CSS: Modify `<style>` section
- JavaScript: Update `<script>` section
- HTML: Change layout in `<body>`

No build process needed - just refresh browser.

## Architecture

```
┌─────────────┐
│   Browser   │
│  dashboard  │
└──────┬──────┘
       │ HTTP
       │ (5s polling)
       │
┌──────▼──────┐
│  bot_api.py │
│  FastAPI    │
│  Port 8002  │
└──────┬──────┘
       │
       ├─────► Exchange API (live data)
       ├─────► Strategy stats (bot state)
       └─────► Log files (trade history)
```

## Limitations (v1.0)

- **View-Only**: Can start/stop bot but can't change settings
- **Polling**: 5-second refresh, not real-time WebSocket
- **No History**: Only last 10 trades, no historical charts
- **Local Only**: Must run on same machine as bot

## Future Enhancements

Potential improvements for v2.0:
- WebSocket for real-time updates
- Settings control panel
- Historical charts and analytics
- Multi-bot dashboard (manage multiple symbols)
- Mobile app version
- Authentication/security

## Security Notes

⚠️ **Important**: This API has no authentication!

- Only use on trusted local networks
- Don't expose port 8002 to internet
- API keys are loaded server-side (not sent to browser)
- For production, add authentication middleware

## Support

Issues with the dashboard?

1. Check API logs for errors
2. Open browser console (F12) for JavaScript errors
3. Verify all dependencies installed: `pip list | grep -E "fastapi|uvicorn"`
4. Test API directly: `curl http://localhost:8002/api/status`

## Version

- Dashboard: v1.0
- API: v1.0
- Last Updated: 2025-10-23

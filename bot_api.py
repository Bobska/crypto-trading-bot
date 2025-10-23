"""
Trading Bot API Server
Exposes FastAPI endpoints to control and monitor the trading bot
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pathlib import Path
import threading
import re
import json
from typing import Optional, Dict, List

# Create FastAPI app
app = FastAPI(title="Trading Bot API", version="1.0.0")

# Enable CORS for local HTML access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global bot instance
trading_bot: Optional[object] = None
bot_thread: Optional[threading.Thread] = None
bot_running = False

@app.get("/api/status")
async def get_status():
    """Get current bot status"""
    try:
        import config
        from exchange import BinanceTestnet
        
        # Create exchange instance to get live data
        exchange = BinanceTestnet(config.BINANCE_API_KEY, config.BINANCE_SECRET)
        
        current_price = None
        balance = None
        
        try:
            current_price = exchange.get_current_price(config.SYMBOL)
            balance = exchange.get_balance()
        except Exception as e:
            print(f"Error getting exchange data: {e}")
        
        status = {
            "bot_running": bot_running,
            "symbol": config.SYMBOL,
            "current_price": current_price,
            "position": trading_bot.position if trading_bot else "USDT",
            "balance": balance or {"USDT": 0.0, "BTC": 0.0},
            "last_updated": datetime.now().isoformat(),
            "profile": config.ACTIVE_PROFILE
        }
        
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")

@app.get("/api/stats")
async def get_stats():
    """Get trading statistics"""
    try:
        if trading_bot and hasattr(trading_bot, 'strategy'):
            stats = trading_bot.strategy.get_stats()
            
            # Add last buy/sell prices
            stats['last_buy_price'] = trading_bot.strategy.last_buy_price
            stats['last_sell_price'] = trading_bot.strategy.last_sell_price
            
            return stats
        else:
            return {
                "total_trades": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0,
                "last_buy_price": None,
                "last_sell_price": None
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@app.get("/api/trades/recent")
async def get_recent_trades():
    """Get last 10 trades from logs"""
    try:
        trades = []
        logs_dir = Path('logs')
        
        if not logs_dir.exists():
            return []
        
        # Get most recent log files (last 2 days)
        log_files = sorted(logs_dir.glob('trades_*.log'), reverse=True)[:2]
        
        # Pattern to match: 2025-10-23 08:14:00 - GridTradingStrategy - INFO - 📝 BUY RECORDED: $65,000.00
        buy_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?(BUY|SELL) RECORDED: \$([0-9,]+\.\d{2})'
        
        for log_file in log_files:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for match in re.finditer(buy_pattern, content):
                timestamp_str = match.group(1)
                action = match.group(2)
                price_str = match.group(3).replace(',', '')
                
                trades.append({
                    'timestamp': timestamp_str,
                    'action': action,
                    'price': float(price_str),
                    'result': None  # Will be calculated by comparing consecutive trades
                })
        
        # Sort by timestamp descending
        trades.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Calculate results (profit/loss between buy and sell pairs)
        for i in range(len(trades) - 1):
            if trades[i]['action'] == 'SELL' and trades[i+1]['action'] == 'BUY':
                profit = trades[i]['price'] - trades[i+1]['price']
                profit_pct = (profit / trades[i+1]['price']) * 100
                trades[i]['result'] = f"+${profit:.2f} (+{profit_pct:.2f}%)" if profit > 0 else f"-${abs(profit):.2f} ({profit_pct:.2f}%)"
        
        # Return last 10 trades
        return trades[:10]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting trades: {str(e)}")

@app.post("/api/bot/start")
async def start_bot():
    """Start the trading bot in background thread"""
    global trading_bot, bot_thread, bot_running
    
    if bot_running:
        raise HTTPException(status_code=400, detail="Bot is already running")
    
    try:
        import config
        from exchange import BinanceTestnet
        from strategy import GridTradingStrategy
        from ai_advisor import AIAdvisor
        from bot import TradingBot
        
        # Create bot components
        exchange = BinanceTestnet(config.BINANCE_API_KEY, config.BINANCE_SECRET)
        
        strategy = GridTradingStrategy(
            buy_threshold=config.BUY_THRESHOLD,
            sell_threshold=config.SELL_THRESHOLD,
            trade_amount=config.TRADE_AMOUNT
        )
        
        ai_advisor = AIAdvisor(api_url=config.AI_API_URL) if config.AI_ENABLED else AIAdvisor(api_url="")
        
        trading_bot = TradingBot(
            exchange=exchange,
            strategy=strategy,
            ai_advisor=ai_advisor,
            symbol=config.SYMBOL,
            check_interval=config.CHECK_INTERVAL
        )
        
        # Start bot in background thread
        def run_bot():
            global bot_running
            bot_running = True
            try:
                trading_bot.run()
            except Exception as e:
                print(f"Bot error: {e}")
            finally:
                bot_running = False
        
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        
        return {"status": "started", "message": "Bot started successfully"}
    except Exception as e:
        bot_running = False
        raise HTTPException(status_code=500, detail=f"Error starting bot: {str(e)}")

@app.post("/api/bot/stop")
async def stop_bot():
    """Stop the trading bot gracefully"""
    global trading_bot, bot_running
    
    if not bot_running:
        raise HTTPException(status_code=400, detail="Bot is not running")
    
    try:
        if trading_bot:
            trading_bot.stop()
            bot_running = False
        
        return {"status": "stopped", "message": "Bot stopped successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping bot: {str(e)}")

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Trading Bot API",
        "version": "1.0.0",
        "endpoints": {
            "status": "/api/status",
            "stats": "/api/stats",
            "recent_trades": "/api/trades/recent",
            "start_bot": "POST /api/bot/start",
            "stop_bot": "POST /api/bot/stop"
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 Trading Bot API Server Starting")
    print("="*60)
    print("Server: http://localhost:8002")
    print("Docs: http://localhost:8002/docs")
    print("="*60 + "\n")
    
    # Run on port 8002 to avoid conflict with bot's main port
    uvicorn.run(app, host="0.0.0.0", port=8002)

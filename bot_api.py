"""
Trading Bot API
FastAPI app exposing endpoints to monitor and control the trading bot
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pathlib import Path
import threading
import json
import re
from typing import Optional, Dict, Any, List

import config
from exchange import BinanceTestnet
from strategy import GridTradingStrategy
from ai_advisor import AIAdvisor
from bot import TradingBot

app = FastAPI(title="Trading Bot API", version="1.0.0")

# Enable CORS (allow all origins for local dashboard access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global bot/thread instances
trading_bot: Optional[TradingBot] = None
bot_thread: Optional[threading.Thread] = None

# Helpers

def _load_state_file() -> Dict[str, Any]:
    state_path = Path("bot_state.json")
    if state_path.exists():
        try:
            return json.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _get_exchange() -> BinanceTestnet:
    return BinanceTestnet(config.BINANCE_API_KEY, config.BINANCE_SECRET)


def _get_strategy() -> GridTradingStrategy:
    return GridTradingStrategy(
        buy_threshold=config.BUY_THRESHOLD,
        sell_threshold=config.SELL_THRESHOLD,
        trade_amount=config.TRADE_AMOUNT,
        stop_loss_percentage=config.get_float_env("STOP_LOSS_PERCENTAGE", 3.0),
        use_trailing_stop=config.get_bool_env("USE_TRAILING_STOP", False),
        trailing_stop_percentage=config.get_float_env("TRAILING_STOP_PERCENTAGE", 1.5),
    )


def _get_ai() -> AIAdvisor:
    if config.AI_ENABLED:
        return AIAdvisor(api_url=config.AI_API_URL)
    return AIAdvisor(api_url="")


def _parse_recent_trades(limit: int = 10) -> List[Dict[str, Any]]:
    logs_dir = Path("logs")
    if not logs_dir.exists():
        return []

    log_files = sorted(logs_dir.glob("trades_*.log"), reverse=True)
    entries: List[Dict[str, Any]] = []

    buy_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*BUY RECORDED: \$([0-9,]+\.\d{2})")
    sell_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*SELL RECORDED: \$([0-9,]+\.\d{2})")

    # Read latest files first until we have enough entries
    for lf in log_files:
        try:
            text = lf.read_text(encoding="utf-8")
        except Exception:
            continue

        for m in buy_pattern.finditer(text):
            ts, price = m.group(1), float(m.group(2).replace(",", ""))
            entries.append({"timestamp": ts, "action": "BUY", "price": price, "result": None})
        for m in sell_pattern.finditer(text):
            ts, price = m.group(1), float(m.group(2).replace(",", ""))
            entries.append({"timestamp": ts, "action": "SELL", "price": price, "result": None})

        if len(entries) >= limit * 2:  # extra buffer
            break

    # Sort by timestamp desc and trim
    entries.sort(key=lambda e: e["timestamp"], reverse=True)
    entries = entries[:limit]

    # Attempt to compute result for SELL rows by pairing with previous BUY
    # Walk entries in reverse chronological order to find prior buy
    last_buy_price: Optional[float] = None
    for e in sorted(entries, key=lambda x: x["timestamp"]):
        if e["action"] == "BUY":
            last_buy_price = e["price"]
        elif e["action"] == "SELL" and last_buy_price:
            pnl_pct = (e["price"] - last_buy_price) / last_buy_price * 100
            e["result"] = "WIN" if pnl_pct > 0 else "LOSS" if pnl_pct < 0 else "BREAK-EVEN"
            last_buy_price = None

    return sorted(entries, key=lambda e: e["timestamp"], reverse=True)


@app.get("/api/status")
def get_status():
    """Return current bot status"""
    try:
        exch = _get_exchange()
        price = None
        balance = None
        position = None

        # Try to get symbol and position from running bot, else from state
        symbol = config.SYMBOL
        running = False

        if trading_bot and trading_bot.running:
            running = True
            symbol = trading_bot.symbol
            position = trading_bot.position
            price = exch.get_current_price(symbol)
            balance = exch.get_balance()
        else:
            # Fallback to minimal status using state and exchange
            state = _load_state_file()
            position = state.get("position")
            price = exch.get_current_price(symbol)
            balance = exch.get_balance()

        return {
            "bot_running": running,
            "profile": getattr(config, "ACTIVE_PROFILE", "default"),
            "symbol": symbol,
            "current_price": price,
            "position": position,
            "balance": balance,
            "last_updated": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
def get_stats():
    """Return trading statistics from strategy"""
    try:
        if trading_bot and trading_bot.strategy:
            return trading_bot.strategy.get_stats()
        # Not running: return zeros
        return {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0,
            "last_buy_price": None,
            "last_sell_price": None,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trades/recent")
def recent_trades():
    try:
        return _parse_recent_trades(limit=10)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/bot/start")
def start_bot():
    global trading_bot, bot_thread
    if trading_bot and trading_bot.running:
        raise HTTPException(status_code=400, detail="Bot is already running")

    try:
        exch = _get_exchange()
        strat = _get_strategy()
        ai = _get_ai()

        trading_bot = TradingBot(
            exchange=exch,
            strategy=strat,
            ai_advisor=ai,
            symbol=config.SYMBOL,
            check_interval=config.CHECK_INTERVAL,
            require_ai_confirmation=config.get_bool_env("AI_CONFIRMATION_REQUIRED", False),
        )

        def _run():
            try:
                trading_bot.run()
            except Exception:
                pass

        bot_thread = threading.Thread(target=_run, name="TradingBotThread", daemon=True)
        bot_thread.start()

        return {"status": "started", "message": "Bot started successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/bot/stop")
def stop_bot():
    global trading_bot, bot_thread
    if not trading_bot or not trading_bot.running:
        return {"status": "stopped", "message": "Bot is not running"}

    try:
        trading_bot.stop()
        if bot_thread and bot_thread.is_alive():
            bot_thread.join(timeout=2.0)
        return {"status": "stopped", "message": "Bot stopped successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    # Run alongside main bot on different port
    uvicorn.run(app, host="0.0.0.0", port=8002)
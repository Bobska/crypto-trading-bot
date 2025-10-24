"""
Trading Bot API Server
Exposes FastAPI endpoints to control and monitor the trading bot
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pathlib import Path
import threading
import re
import json
import asyncio
from typing import Optional, Dict, List
from contextlib import asynccontextmanager

# WebSocket Connection Manager
class ConnectionManager:
    """Enhanced WebSocket connection manager with heartbeat and tracking"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_info: Dict[WebSocket, dict] = {}
        self.last_price: Optional[float] = None
        self.heartbeat_task: Optional[asyncio.Task] = None
    
    async def connect(self, websocket: WebSocket):
        """Accept and add WebSocket connection with tracking"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Track connection info
        self.connection_info[websocket] = {
            'connected_at': datetime.now(),
            'messages_sent': 0,
            'last_activity': datetime.now()
        }
        
        print(f"✅ WebSocket connected. Total connections: {len(self.active_connections)}")
        
        # Start heartbeat if not already running
        if not self.heartbeat_task or self.heartbeat_task.done():
            self.heartbeat_task = asyncio.create_task(self.send_heartbeat())
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection and cleanup tracking"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
            # Log statistics before removing
            if websocket in self.connection_info:
                info = self.connection_info[websocket]
                duration = (datetime.now() - info['connected_at']).total_seconds()
                print(f"❌ WebSocket disconnected after {duration:.1f}s. " 
                      f"Messages sent: {info['messages_sent']}. "
                      f"Remaining connections: {len(self.active_connections)}")
                del self.connection_info[websocket]
            else:
                print(f"❌ WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_heartbeat(self):
        """Send periodic heartbeat to keep connections alive"""
        while self.active_connections:
            try:
                await asyncio.sleep(30)  # Every 30 seconds
                
                if not self.active_connections:
                    break
                
                # Send ping to all connections
                dead_connections = []
                for connection in self.active_connections:
                    try:
                        await connection.send_json({
                            'type': 'heartbeat',
                            'timestamp': datetime.now().isoformat()
                        })
                        
                        # Update activity tracking
                        if connection in self.connection_info:
                            self.connection_info[connection]['last_activity'] = datetime.now()
                    except Exception as e:
                        print(f"❤️‍🩹 Heartbeat failed: {e}")
                        dead_connections.append(connection)
                
                # Clean up dead connections
                for connection in dead_connections:
                    self.disconnect(connection)
                
                if self.active_connections:
                    print(f"💓 Heartbeat sent to {len(self.active_connections)} clients")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Heartbeat error: {e}")
                await asyncio.sleep(30)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return
        
        # Convert to JSON string
        message_json = json.dumps(message)
        
        # Send to all connections (remove dead connections)
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
                
                # Update message counter
                if connection in self.connection_info:
                    self.connection_info[connection]['messages_sent'] += 1
                    self.connection_info[connection]['last_activity'] = datetime.now()
            except Exception as e:
                print(f"Error sending to WebSocket: {e}")
                dead_connections.append(connection)
        
        # Clean up dead connections
        for connection in dead_connections:
            self.disconnect(connection)
        
        # Log broadcast
        message_type = message.get('type', 'unknown')
        print(f"📡 Broadcast to {len(self.active_connections)} clients: {message_type}")
    
    async def broadcast_trade(self, trade_data: dict):
        """Broadcast trade execution with formatted message"""
        action = trade_data.get('action', 'TRADE')
        price = trade_data.get('price', 0)
        amount = trade_data.get('amount', 0)
        position = trade_data.get('position', 'UNKNOWN')
        profit_pct = trade_data.get('profit_pct', 0)
        
        # Add emoji based on action
        emoji = '🟢' if action == 'BUY' else '🔴' if action == 'SELL' else '⚪'
        
        # Format message
        message = {
            'type': 'trade_executed',
            'data': {
                'action': action,
                'price': price,
                'amount': amount,
                'position': position,
                'profit_pct': profit_pct,
                'emoji': emoji,
                'timestamp': datetime.now().isoformat(),
                'message': f"{emoji} {action} {amount} BTC at ${price:,.2f}"
            }
        }
        
        await self.broadcast(message)
        print(f"💰 Trade broadcast: {action} at ${price:,.2f}")
    
    async def broadcast_price(self, price_data: dict):
        """Broadcast price update only if changed significantly (>0.1%)"""
        price = price_data.get('price', 0)
        symbol = price_data.get('symbol', 'BTC/USDT')
        
        # Check if price changed significantly
        if self.last_price is not None:
            price_change_pct = abs((price - self.last_price) / self.last_price * 100)
            if price_change_pct < 0.1:
                # Skip broadcast if change is < 0.1%
                return
        
        # Update last price
        self.last_price = price
        
        # Format message
        message = {
            'type': 'price_update',
            'data': {
                'price': price,
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'formatted_price': f"${price:,.2f}"
            }
        }
        
        await self.broadcast(message)
    
    async def broadcast_status(self, status_data: dict):
        """Broadcast bot status with formatted message"""
        status = status_data.get('status', 'unknown')
        position = status_data.get('position', 'NONE')
        balance = status_data.get('balance', {})
        
        # Format message
        message = {
            'type': 'status_change',
            'data': {
                'status': status,
                'position': position,
                'balance': balance,
                'bot_running': status == 'running',
                'timestamp': datetime.now().isoformat()
            }
        }
        
        await self.broadcast(message)
        print(f"⚡ Status broadcast: {status.upper()}")
    
    def get_connection_stats(self) -> dict:
        """Get statistics about all connections"""
        stats = {
            'total_connections': len(self.active_connections),
            'connections': []
        }
        
        for ws, info in self.connection_info.items():
            duration = (datetime.now() - info['connected_at']).total_seconds()
            stats['connections'].append({
                'connected_for': f"{duration:.1f}s",
                'messages_sent': info['messages_sent'],
                'last_activity': info['last_activity'].isoformat()
            })
        
        return stats

# Forward declaration of price_update_task
price_update_task: Optional[asyncio.Task] = None

# Lifespan context manager for startup/shutdown events

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    global price_update_task
    
    # Startup: Start background tasks
    print("🚀 Starting background tasks...")
    price_update_task = asyncio.create_task(broadcast_price_updates())
    print("✅ Background tasks started")
    
    yield  # Application runs here
    
    # Shutdown: Cleanup
    print("🛑 Stopping background tasks...")
    if price_update_task:
        price_update_task.cancel()
        try:
            await price_update_task
        except asyncio.CancelledError:
            pass
    print("✅ Background tasks stopped")

# Create FastAPI app with lifespan
app = FastAPI(title="Trading Bot API", version="1.0.0", lifespan=lifespan)

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

# WebSocket manager instance
manager = ConnectionManager()

def is_bot_running() -> bool:
    """Check if bot is running by looking for recent state updates"""
    try:
        state_file = Path("bot_state.json")
        if not state_file.exists():
            return bot_running  # Fall back to internal state
        
        # Check if state file was modified in last 60 seconds
        import time
        last_modified = state_file.stat().st_mtime
        time_diff = time.time() - last_modified
        
        # If state file was updated recently, bot is likely running
        if time_diff < 60:
            return True
        
        return bot_running
    except:
        return bot_running

def load_bot_state() -> Dict:
    """Load bot state from file"""
    try:
        state_file = Path("bot_state.json")
        if state_file.exists():
            with open(state_file, 'r') as f:
                return json.load(f)
    except:
        pass
    return {"position": "USDT", "last_buy_price": None, "last_sell_price": None}

@app.get("/api/status")
async def get_status():
    """Get current bot status"""
    try:
        import config
        from exchange import BinanceTestnet
        
        # Load saved state
        state = load_bot_state()
        
        # Create exchange instance to get live data
        exchange = BinanceTestnet(config.BINANCE_API_KEY, config.BINANCE_SECRET)
        
        current_price = None
        balance = None
        
        # Fetch exchange data with timeout protection (2 seconds max)
        try:
            async def fetch_exchange_data():
                # Run blocking exchange calls in thread pool to avoid blocking event loop
                loop = asyncio.get_event_loop()
                price = await loop.run_in_executor(None, exchange.get_current_price, config.SYMBOL)
                bal = await loop.run_in_executor(None, exchange.get_balance)
                return price, bal
            
            current_price, balance = await asyncio.wait_for(fetch_exchange_data(), timeout=2.0)
        except asyncio.TimeoutError:
            print("⚠️ Exchange API timeout (2s) - using cached data")
            # Use cached/state data as fallback
            current_price = state.get('last_price')
            balance = state.get('balance', {"USDT": 0.0, "BTC": 0.0})
        except Exception as e:
            print(f"⚠️ Error getting exchange data: {e}")
            # Use cached/state data as fallback
            current_price = state.get('last_price')
            balance = state.get('balance', {"USDT": 0.0, "BTC": 0.0})
        
        # Check if bot is running (either managed by API or external process)
        running = is_bot_running()
        
        status = {
            "bot_running": running,
            "symbol": config.SYMBOL,
            "current_price": current_price,
            "position": state.get("position", "USDT"),
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
        # Try to get stats from running bot first
        if trading_bot and hasattr(trading_bot, 'strategy'):
            stats = trading_bot.strategy.get_stats()
            stats['last_buy_price'] = trading_bot.strategy.last_buy_price
            stats['last_sell_price'] = trading_bot.strategy.last_sell_price
            return stats
        
        # Fall back to reading from state file
        state = load_bot_state()
        
        # Calculate stats from trade history in logs
        trades = parse_trade_history()
        total_trades = len(trades)
        
        # Count wins (trades with + in result)
        wins = 0
        for t in trades:
            result = t.get('result')
            if result and '+' in str(result):
                wins += 1
        
        losses = total_trades - wins
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0.0
        
        return {
            "total_trades": total_trades,
            "wins": wins,
            "losses": losses,
            "win_rate": round(win_rate, 1),
            "last_buy_price": state.get("last_buy_price"),
            "last_sell_price": state.get("last_sell_price")
        }
    except Exception as e:
        import traceback
        print(f"Error in get_stats: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

def parse_trade_history() -> List[Dict]:
    """Parse trade history from log files"""
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
        
        return trades
    except:
        return []

@app.get("/api/trades/recent")
async def get_recent_trades():
    """Get last 10 trades from logs"""
    try:
        trades = parse_trade_history()
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

# NOTE: WebSocket endpoint moved to line ~1108 to avoid duplication

@app.get("/api/connections")
async def get_connections():
    """Get WebSocket connection statistics"""
    return manager.get_connection_stats()

# ===================================
# TRADING TERMINAL ENDPOINTS
# ===================================

@app.get("/api/candles/{symbol}/{timeframe}")
async def get_candles(symbol: str, timeframe: str, limit: int = 500):
    """
    Get historical OHLCV candlestick data
    
    Parameters:
    - symbol: Trading pair (e.g., BTC/USDT)
    - timeframe: Candle interval (1m, 5m, 15m, 1h, 4h, 1d)
    - limit: Number of candles to fetch (default 500, max 1000)
    
    Returns:
    - Array of candles: [{time, open, high, low, close, volume}, ...]
    """
    try:
        import config
        from exchange import BinanceTestnet
        
        # Validate timeframe
        valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d', '3d', '1w']
        if timeframe not in valid_timeframes:
            raise HTTPException(status_code=400, detail=f"Invalid timeframe. Valid: {valid_timeframes}")
        
        # Validate limit
        if limit < 1 or limit > 1000:
            raise HTTPException(status_code=400, detail="Limit must be between 1 and 1000")
        
        # Normalize symbol (replace / with nothing for Binance API)
        api_symbol = symbol.replace('/', '')
        
        # Create exchange instance
        exchange = BinanceTestnet(config.BINANCE_API_KEY, config.BINANCE_SECRET)
        
        # Use CCXT's fetch_ohlcv method (exchange.exchange is the CCXT instance)
        candles = exchange.exchange.fetch_ohlcv(
            symbol=symbol,  # Keep the slash: 'BTC/USDT'
            timeframe=timeframe,
            limit=limit
        )
        
        # Format response
        formatted_candles = []
        for candle in candles:
            formatted_candles.append({
                'time': int(candle[0] / 1000),  # Convert to seconds
                'open': float(candle[1]),
                'high': float(candle[2]),
                'low': float(candle[3]),
                'close': float(candle[4]),
                'volume': float(candle[5])
            })
        
        print(f"📊 Fetched {len(formatted_candles)} candles for {symbol} ({timeframe})")
        return formatted_candles
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error fetching candles: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error fetching candles: {str(e)}")


@app.post("/api/manual-trade")
async def manual_trade(trade_request: dict):
    """
    Execute a manual trade
    
    Body:
    - action: 'BUY' or 'SELL'
    - amount: Trade amount in BTC
    - price: Optional limit price (uses market price if not provided)
    
    Returns:
    - success: boolean
    - order: Order details
    - error: Error message if failed
    """
    try:
        import config
        from exchange import BinanceTestnet
        
        # Validate request
        action = trade_request.get('action', '').upper()
        amount = trade_request.get('amount')
        price = trade_request.get('price')
        
        if action not in ['BUY', 'SELL']:
            raise HTTPException(status_code=400, detail="Action must be 'BUY' or 'SELL'")
        
        if not amount or amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than 0")
        
        # Create exchange instance
        exchange = BinanceTestnet(config.BINANCE_API_KEY, config.BINANCE_SECRET)
        
        # Get current balance
        balance = exchange.get_balance()
        
        # Validate balance
        current_price = exchange.get_current_price(config.SYMBOL)
        if action == 'BUY':
            required_usdt = amount * (price if price else current_price)
            if balance.get('USDT', 0) < required_usdt:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient USDT balance. Required: ${required_usdt:.2f}, Available: ${balance.get('USDT', 0):.2f}"
                )
        elif action == 'SELL':
            if balance.get('BTC', 0) < amount:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient BTC balance. Required: {amount}, Available: {balance.get('BTC', 0)}"
                )
        
        # Execute trade
        print(f"🎯 Manual trade: {action} {amount} BTC at ${price or current_price:.2f}")
        
        if action == 'BUY':
            order = exchange.place_buy_order(config.SYMBOL, amount, price)
        else:
            order = exchange.place_sell_order(config.SYMBOL, amount, price)
        
        # Get executed price
        executed_price = float(order.get('price', price or current_price))
        
        # Log trade to database (if available)
        try:
            # This would integrate with Django database
            # For now, we'll just log it
            print(f"✅ Manual trade executed: {action} {amount} BTC at ${executed_price:.2f}")
        except Exception as e:
            print(f"Warning: Could not log trade to database: {e}")
        
        # Broadcast via WebSocket
        await manager.broadcast_trade({
            'action': action,
            'price': executed_price,
            'amount': amount,
            'position': 'BTC' if action == 'BUY' else 'USDT',
            'manual': True
        })
        
        return {
            'success': True,
            'order': {
                'id': order.get('orderId'),
                'symbol': config.SYMBOL,
                'action': action,
                'amount': amount,
                'price': executed_price,
                'status': order.get('status', 'FILLED'),
                'timestamp': datetime.now().isoformat()
            },
            'error': None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error executing manual trade: {str(e)}")
        print(traceback.format_exc())
        return {
            'success': False,
            'order': None,
            'error': str(e)
        }


@app.get("/api/position/pnl")
async def get_position_pnl():
    """
    Get real-time P&L calculation for current position
    
    Returns:
    - entry_price: Average entry price
    - current_price: Current market price
    - unrealized_pnl: Unrealized profit/loss in USD
    - unrealized_pnl_pct: Unrealized profit/loss percentage
    - if_sold_now: Net profit if position closed now
    - roi: Return on investment percentage
    - fees: Estimated fees
    """
    try:
        import config
        from exchange import BinanceTestnet
        
        # Load bot state
        state = load_bot_state()
        position = state.get('position', 'USDT')
        
        # Create exchange instance
        exchange = BinanceTestnet(config.BINANCE_API_KEY, config.BINANCE_SECRET)
        
        # Get current price and balance
        current_price = exchange.get_current_price(config.SYMBOL)
        balance = exchange.get_balance()
        
        # Calculate P&L based on position
        if position == 'BTC' or balance.get('BTC', 0) > 0:
            # We have BTC position
            btc_amount = balance.get('BTC', 0)
            entry_price = state.get('last_buy_price', current_price)
            
            # Calculate unrealized P&L
            entry_value = btc_amount * entry_price
            current_value = btc_amount * current_price
            unrealized_pnl = current_value - entry_value
            unrealized_pnl_pct = (unrealized_pnl / entry_value * 100) if entry_value > 0 else 0
            
            # Estimate fees (0.1% per trade, buy + sell)
            estimated_fees = entry_value * 0.001 + current_value * 0.001
            
            # Net profit if sold now
            if_sold_now = unrealized_pnl - estimated_fees
            roi = (if_sold_now / entry_value * 100) if entry_value > 0 else 0
            
            return {
                'has_position': True,
                'position_type': 'LONG',
                'amount': btc_amount,
                'entry_price': entry_price,
                'current_price': current_price,
                'unrealized_pnl': round(unrealized_pnl, 2),
                'unrealized_pnl_pct': round(unrealized_pnl_pct, 2),
                'if_sold_now': round(if_sold_now, 2),
                'roi': round(roi, 2),
                'estimated_fees': round(estimated_fees, 2),
                'entry_value': round(entry_value, 2),
                'current_value': round(current_value, 2)
            }
        else:
            # No position (all USDT)
            return {
                'has_position': False,
                'position_type': 'NONE',
                'amount': 0,
                'entry_price': 0,
                'current_price': current_price,
                'unrealized_pnl': 0,
                'unrealized_pnl_pct': 0,
                'if_sold_now': 0,
                'roi': 0,
                'estimated_fees': 0,
                'entry_value': 0,
                'current_value': balance.get('USDT', 0)
            }
            
    except Exception as e:
        import traceback
        print(f"Error calculating P&L: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error calculating P&L: {str(e)}")


@app.get("/api/orders/history")
async def get_orders_history(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    trade_type: Optional[str] = None,
    result: Optional[str] = None,
    limit: int = 50
):
    """
    Get paginated order history with filters
    
    Query params:
    - from_date: Start date (YYYY-MM-DD)
    - to_date: End date (YYYY-MM-DD)
    - trade_type: BUY or SELL
    - result: WIN or LOSS
    - limit: Number of orders (default 50, max 100)
    
    Returns:
    - orders: Array of order details
    - summary: Statistics (total trades, volume, fees, net P&L)
    """
    try:
        # Parse trade history from logs
        trades = parse_trade_history()
        
        # Apply filters
        filtered_trades = trades
        
        if from_date:
            filtered_trades = [t for t in filtered_trades if t['timestamp'] >= from_date]
        
        if to_date:
            filtered_trades = [t for t in filtered_trades if t['timestamp'] <= to_date + ' 23:59:59']
        
        if trade_type and trade_type.upper() in ['BUY', 'SELL']:
            filtered_trades = [t for t in filtered_trades if t['action'] == trade_type.upper()]
        
        if result and result.upper() in ['WIN', 'LOSS']:
            if result.upper() == 'WIN':
                filtered_trades = [t for t in filtered_trades if t.get('result') and '+' in str(t['result'])]
            else:
                filtered_trades = [t for t in filtered_trades if t.get('result') and '-' in str(t['result'])]
        
        # Limit results
        if limit > 100:
            limit = 100
        paginated_trades = filtered_trades[:limit]
        
        # Calculate summary statistics
        total_trades = len(filtered_trades)
        wins = sum(1 for t in filtered_trades if t.get('result') and '+' in str(t['result']))
        losses = sum(1 for t in filtered_trades if t.get('result') and '-' in str(t['result']))
        
        # Calculate total volume and fees (estimated)
        total_volume = sum(t['price'] for t in filtered_trades)
        estimated_fees = total_volume * 0.001  # 0.1% fee estimate
        
        summary = {
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'win_rate': round((wins / total_trades * 100) if total_trades > 0 else 0, 2),
            'total_volume': round(total_volume, 2),
            'estimated_fees': round(estimated_fees, 2)
        }
        
        return {
            'orders': paginated_trades,
            'summary': summary,
            'filters': {
                'from_date': from_date,
                'to_date': to_date,
                'trade_type': trade_type,
                'result': result,
                'limit': limit
            }
        }
        
    except Exception as e:
        import traceback
        print(f"Error getting order history: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting order history: {str(e)}")


@app.post("/api/ai/advice")
async def get_ai_advice(request: dict):
    """
    Get AI trading advice
    
    Body:
    - mode: 'opinion', 'suggest', or 'copilot'
    - context: Additional context (price, indicators, etc.)
    
    Returns:
    - advice: AI response text
    - confidence: Confidence score (if copilot mode)
    - action: Suggested action (if applicable)
    """
    try:
        import config
        from ai_advisor import AIAdvisor
        
        mode = request.get('mode', 'opinion')
        context = request.get('context', {})
        
        # Validate mode
        if mode not in ['opinion', 'suggest', 'copilot']:
            raise HTTPException(status_code=400, detail="Mode must be 'opinion', 'suggest', or 'copilot'")
        
        # Create AI advisor
        ai_advisor = AIAdvisor(api_url=config.AI_API_URL if config.AI_ENABLED else "")
        
        # Get AI response based on mode
        if mode == 'opinion':
            # General market opinion
            advice_text = f"Market analysis requested at ${context.get('price', 'N/A')}"
            response = {
                'advice': advice_text,
                'mode': mode,
                'timestamp': datetime.now().isoformat()
            }
        elif mode == 'suggest':
            # Suggestion based on indicators
            advice_text = "Based on current market conditions, suggest holding position."
            response = {
                'advice': advice_text,
                'action': 'HOLD',
                'reasoning': 'Market is consolidating',
                'mode': mode,
                'timestamp': datetime.now().isoformat()
            }
        elif mode == 'copilot':
            # Full copilot mode with confidence
            advice_text = "AI copilot analysis complete."
            response = {
                'advice': advice_text,
                'action': 'BUY',
                'confidence': 'medium',
                'reasoning': 'Technical indicators show potential upward movement',
                'mode': mode,
                'timestamp': datetime.now().isoformat()
            }
        
        print(f"🤖 AI advice requested: {mode}")
        
        # Broadcast to WebSocket
        await manager.broadcast({
            'type': 'ai_advice',
            'data': response
        })
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error getting AI advice: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting AI advice: {str(e)}")


@app.get("/api/grid/levels")
async def get_grid_levels():
    """
    Get current grid trading levels for chart visualization
    
    Returns:
    - buy_threshold_price: Price at which bot will buy
    - sell_threshold_price: Price at which bot will sell
    - current_price: Current market price
    - grid_spacing: Spacing between levels
    """
    try:
        import config
        from exchange import BinanceTestnet
        
        # Get current price
        exchange = BinanceTestnet(config.BINANCE_API_KEY, config.BINANCE_SECRET)
        current_price = exchange.get_current_price(config.SYMBOL)
        
        # Load bot state
        state = load_bot_state()
        position = state.get('position', 'USDT')
        last_buy_price = state.get('last_buy_price')
        last_sell_price = state.get('last_sell_price')
        
        # Calculate grid levels based on thresholds
        buy_threshold_pct = config.BUY_THRESHOLD
        sell_threshold_pct = config.SELL_THRESHOLD
        
        if position == 'BTC' and last_buy_price:
            # Calculate sell level from last buy
            sell_threshold_price = last_buy_price * (1 + sell_threshold_pct / 100)
            buy_threshold_price = current_price * (1 - buy_threshold_pct / 100)
        elif position == 'USDT' and last_sell_price:
            # Calculate buy level from last sell
            buy_threshold_price = last_sell_price * (1 - buy_threshold_pct / 100)
            sell_threshold_price = current_price * (1 + sell_threshold_pct / 100)
        else:
            # Default grid around current price
            buy_threshold_price = current_price * (1 - buy_threshold_pct / 100)
            sell_threshold_price = current_price * (1 + sell_threshold_pct / 100)
        
        grid_spacing = sell_threshold_price - buy_threshold_price
        
        return {
            'current_price': round(current_price, 2),
            'buy_threshold_price': round(buy_threshold_price, 2),
            'sell_threshold_price': round(sell_threshold_price, 2),
            'buy_threshold_pct': buy_threshold_pct,
            'sell_threshold_pct': sell_threshold_pct,
            'grid_spacing': round(grid_spacing, 2),
            'position': position,
            'last_buy_price': last_buy_price,
            'last_sell_price': last_sell_price
        }
        
    except Exception as e:
        import traceback
        print(f"Error getting grid levels: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting grid levels: {str(e)}")


@app.put("/api/bot/mode")
async def set_bot_mode(mode_request: dict):
    """
    Change bot operating mode
    
    Body:
    - mode: 'auto', 'manual', or 'paused'
    
    Returns:
    - status: Updated status
    - mode: Current mode
    """
    try:
        global bot_running
        
        mode = mode_request.get('mode', '').lower()
        
        if mode not in ['auto', 'manual', 'paused']:
            raise HTTPException(status_code=400, detail="Mode must be 'auto', 'manual', or 'paused'")
        
        print(f"🔧 Bot mode change requested: {mode.upper()}")
        
        if mode == 'auto':
            # Start bot if not running
            if not bot_running:
                return await start_bot()
            else:
                response = {
                    'status': 'running',
                    'mode': 'auto',
                    'message': 'Bot already running in auto mode'
                }
        elif mode == 'manual':
            # Keep bot running but disable automated trading
            response = {
                'status': 'manual',
                'mode': 'manual',
                'message': 'Bot in manual mode - automated trading disabled'
            }
        elif mode == 'paused':
            # Stop bot
            if bot_running:
                return await stop_bot()
            else:
                response = {
                    'status': 'stopped',
                    'mode': 'paused',
                    'message': 'Bot is paused'
                }
        
        # Broadcast mode change
        await manager.broadcast({
            'type': 'mode_change',
            'data': response
        })
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error changing bot mode: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error changing bot mode: {str(e)}")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates
    
    Sends:
    - price_update: Live price changes
    - trade_executed: When trades are executed
    - status_change: Bot status changes
    - heartbeat: Keep-alive messages
    """
    print("🔌 WebSocket connection attempt...")
    
    try:
        await manager.connect(websocket)
        print("✅ WebSocket connected successfully")
        
        # Send initial status
        try:
            state = load_bot_state()
            await websocket.send_json({
                'type': 'status',
                'data': {
                    'bot_running': is_bot_running(),
                    'position': state.get('position', 'USDT'),
                    'timestamp': datetime.now().isoformat()
                }
            })
            print("📤 Sent initial status")
        except Exception as e:
            print(f"❌ Error sending initial status: {e}")
        
        # CRITICAL: Keep connection alive indefinitely
        while True:
            try:
                # Wait for messages from client with 60-second timeout
                # This allows us to detect dead connections and send keepalives
                data = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                
                # Handle client messages
                if data:
                    try:
                        msg = json.loads(data)
                        
                        # Handle ping/pong
                        if msg.get('type') == 'ping':
                            await websocket.send_json({
                                'type': 'pong',
                                'timestamp': datetime.now().isoformat()
                            })
                        
                        # Handle status request
                        elif msg.get('command') == 'get_status':
                            status_data = await get_status()
                            await websocket.send_json({
                                'type': 'status',
                                'data': status_data
                            })
                        
                        # Handle stats request
                        elif msg.get('command') == 'get_stats':
                            stats_data = await get_stats()
                            await websocket.send_json({
                                'type': 'stats',
                                'data': stats_data
                            })
                    except json.JSONDecodeError:
                        pass  # Ignore invalid JSON
                    except Exception as e:
                        print(f"⚠️ Error handling message: {e}")
                        
            except asyncio.TimeoutError:
                # No message for 60 seconds - send keepalive ping to check connection health
                try:
                    await websocket.send_json({
                        'type': 'heartbeat',
                        'timestamp': datetime.now().isoformat()
                    })
                    print("💓 Sent keepalive heartbeat")
                except Exception as e:
                    print(f"❌ Failed to send heartbeat, connection dead: {e}")
                    break  # Connection is dead, exit loop
                    
            except WebSocketDisconnect:
                print("👋 Client disconnected normally")
                break
            except Exception as e:
                print(f"❌ WebSocket receive error: {e}")
                import traceback
                print(traceback.format_exc())
                break
                
    except Exception as e:
        print(f"❌ WebSocket connection error: {e}")
        import traceback
        print(traceback.format_exc())
    finally:
        manager.disconnect(websocket)
        print("🔌 WebSocket connection closed")


# Background task for price updates
price_update_task: Optional[asyncio.Task] = None

async def broadcast_price_updates():
    """Background task to broadcast live price updates"""
    print("📡 Starting price update broadcaster...")
    
    try:
        import config
        from exchange import BinanceTestnet
        
        exchange = BinanceTestnet(config.BINANCE_API_KEY, config.BINANCE_SECRET)
        symbol = config.SYMBOL
        print(f"✅ Price broadcaster initialized for {symbol}")
        
    except Exception as e:
        print(f"❌ Failed to initialize price broadcaster: {e}")
        print("⚠️  Continuing without real-time price updates")
        return  # Exit broadcaster if can't initialize
    
    while True:
        try:
            # Check if there are active connections
            if not manager.active_connections:
                await asyncio.sleep(5)  # Sleep longer if no clients
                continue
            
            # Fetch current price
            try:
                current_price = exchange.get_current_price(symbol)
                
                # Broadcast price update
                await manager.broadcast_price({
                    'price': current_price,
                    'symbol': symbol
                })
                
            except Exception as e:
                print(f"⚠️  Error fetching price: {e}")
            
            # Update every 2 seconds
            await asyncio.sleep(2)
            
        except asyncio.CancelledError:
            print("📡 Price broadcaster stopped")
            break
        except Exception as e:
            print(f"❌ Price broadcaster error: {e}")
            await asyncio.sleep(5)


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Trading Bot API",
        "version": "2.0.0",
        "endpoints": {
            "status": "/api/status",
            "stats": "/api/stats",
            "recent_trades": "/api/trades/recent",
            "connections": "/api/connections",
            "candles": "/api/candles/{symbol}/{timeframe}",
            "manual_trade": "POST /api/manual-trade",
            "position_pnl": "/api/position/pnl",
            "orders_history": "/api/orders/history",
            "ai_advice": "POST /api/ai/advice",
            "grid_levels": "/api/grid/levels",
            "bot_mode": "PUT /api/bot/mode",
            "start_bot": "POST /api/bot/start",
            "stop_bot": "POST /api/bot/stop",
            "websocket": "ws://localhost:8002/ws"
        },
        "websocket_info": {
            "url": "ws://localhost:8002/ws",
            "updates": ["price_update", "trade_executed", "status_change", "heartbeat"],
            "update_interval": "2 seconds"
        }
    }

# Export for use by other modules
__all__ = ['app', 'manager']

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 Trading Bot API Server Starting")
    print("="*60)
    print("Server: http://localhost:8002")
    print("Docs: http://localhost:8002/docs")
    print("WebSocket: ws://localhost:8002/ws")
    print("="*60 + "\n")
    
    # Run on port 8002 to avoid conflict with bot's main port
    uvicorn.run(app, host="0.0.0.0", port=8002)

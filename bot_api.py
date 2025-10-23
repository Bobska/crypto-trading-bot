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
        
        try:
            current_price = exchange.get_current_price(config.SYMBOL)
            balance = exchange.get_balance()
        except Exception as e:
            print(f"Error getting exchange data: {e}")
        
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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    
    try:
        # Send initial status on connect
        status_data = await get_status()
        await websocket.send_text(json.dumps({
            "type": "status",
            "data": status_data
        }))
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Receive messages from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle client commands
                if message.get("command") == "get_status":
                    status_data = await get_status()
                    await websocket.send_text(json.dumps({
                        "type": "status",
                        "data": status_data
                    }))
                elif message.get("command") == "get_stats":
                    stats_data = await get_stats()
                    await websocket.send_text(json.dumps({
                        "type": "stats",
                        "data": stats_data
                    }))
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"WebSocket error: {e}")
                await asyncio.sleep(1)
    
    finally:
        manager.disconnect(websocket)

@app.get("/api/connections")
async def get_connections():
    """Get WebSocket connection statistics"""
    return manager.get_connection_stats()

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
            "connections": "/api/connections",
            "start_bot": "POST /api/bot/start",
            "stop_bot": "POST /api/bot/stop",
            "websocket": "ws://localhost:8002/ws"
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

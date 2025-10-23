"""
Multi-Bot Trading System
Runs multiple trading bots simultaneously for different trading pairs

Usage:
    python multi_bot.py

Features:
    - Runs separate bots for BTC/USDT, ETH/USDT, and BNB/USDT
    - Each bot operates in its own thread with independent strategy
    - Shared exchange and AI advisor instances across all bots
    - Separate log files: logs/trades_BTC.log, logs/trades_ETH.log, logs/trades_BNB.log
    - Combined status display showing all positions
    - Graceful shutdown with Ctrl+C stops all bots

Architecture:
    - MultiBotManager: Coordinates multiple bot instances
    - Each bot has: Own TradingBot instance, Own GridTradingStrategy, Own state file
    - Shared resources: BinanceTestnet exchange, AIAdvisor
"""
import config
import signal
import sys
import threading
import time
from datetime import datetime
from exchange import BinanceTestnet
from strategy import GridTradingStrategy
from ai_advisor import AIAdvisor
from bot import TradingBot
from logger_setup import setup_logger
from banner import print_banner

class MultiBotManager:
    """
    Manages multiple trading bots running in parallel threads
    
    Each bot operates on a different trading pair with its own strategy
    and state, but shares the same exchange and AI advisor instances.
    """
    
    def __init__(self, symbols: list, exchange, ai_advisor):
        """
        Initialize Multi-Bot Manager
        
        Args:
            symbols: List of trading pair symbols (e.g., ['BTC/USDT', 'ETH/USDT'])
            exchange: Shared exchange instance
            ai_advisor: Shared AI advisor instance
        """
        self.symbols = symbols
        self.exchange = exchange
        self.ai_advisor = ai_advisor
        self.bots = {}
        self.threads = {}
        self.running = False
        
        # Setup logger
        self.logger = setup_logger('MultiBotManager')
        
        # Register signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info(f"Multi-Bot Manager initialized for {len(symbols)} symbols")
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C and termination signals"""
        print("\n\n🛑 Shutdown signal received...")
        self.logger.info(f"Received signal {signum}, initiating shutdown")
        self.stop_all()
        sys.exit(0)
    
    def create_bots(self):
        """Create separate bot instance for each symbol"""
        self.logger.info("Creating bot instances...")
        
        for symbol in self.symbols:
            # Extract base currency for logging (e.g., 'BTC' from 'BTC/USDT')
            base_currency = symbol.split('/')[0]
            
            # Create separate strategy for this symbol
            strategy = GridTradingStrategy(
                buy_threshold=config.BUY_THRESHOLD,
                sell_threshold=config.SELL_THRESHOLD,
                trade_amount=config.TRADE_AMOUNT
            )
            
            # Create bot with custom logger name for separate log files
            bot = TradingBot(
                exchange=self.exchange,
                strategy=strategy,
                ai_advisor=self.ai_advisor,
                symbol=symbol,
                check_interval=config.CHECK_INTERVAL
            )
            
            # Override bot's logger to use symbol-specific log file
            bot.logger = setup_logger(f'Bot_{base_currency}', log_suffix=base_currency)
            
            self.bots[symbol] = bot
            self.logger.info(f"✓ Created bot for {symbol}")
        
        self.logger.info(f"All {len(self.bots)} bots created successfully")
    
    def start_all(self):
        """Start all bots in separate threads"""
        self.running = True
        self.logger.info("Starting all bots...")
        
        for symbol, bot in self.bots.items():
            # Create thread for this bot
            thread = threading.Thread(
                target=self._run_bot,
                args=(symbol, bot),
                name=f"Thread-{symbol}",
                daemon=True
            )
            
            self.threads[symbol] = thread
            thread.start()
            
            self.logger.info(f"✓ Started bot for {symbol} in thread {thread.name}")
            
            # Small delay between starting bots to avoid API rate limits
            time.sleep(0.5)
        
        self.logger.info(f"All {len(self.threads)} bot threads started")
    
    def _run_bot(self, symbol: str, bot: TradingBot):
        """Run a single bot (called in separate thread)"""
        try:
            self.logger.info(f"[{symbol}] Bot thread starting...")
            bot.run()
        except Exception as e:
            self.logger.error(f"[{symbol}] Bot thread error: {str(e)}")
    
    def stop_all(self):
        """Stop all bots gracefully"""
        self.running = False
        self.logger.info("Stopping all bots...")
        
        # Stop each bot
        for symbol, bot in self.bots.items():
            self.logger.info(f"Stopping bot for {symbol}...")
            bot.stop()
        
        # Wait for all threads to finish
        for symbol, thread in self.threads.items():
            if thread.is_alive():
                self.logger.info(f"Waiting for {symbol} thread to finish...")
                thread.join(timeout=5.0)
        
        self.logger.info("All bots stopped")
    
    def print_combined_status(self):
        """Print status of all bots in a consolidated view"""
        print("\n" + "=" * 80)
        print(f"MULTI-BOT STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Get overall balance
        balance = self.exchange.get_balance()
        
        if balance:
            print("\n💰 Total Balance:")
            print(f"   USDT: ${balance.get('USDT', 0.0):,.2f}")
            
            for symbol in self.symbols:
                base_currency = symbol.split('/')[0]
                amount = balance.get(base_currency, 0.0)
                print(f"   {base_currency}:  {amount:.6f}")
        
        print("\n📊 Individual Bot Status:")
        print("-" * 80)
        
        for symbol, bot in self.bots.items():
            base_currency = symbol.split('/')[0]
            current_price = self.exchange.get_current_price(symbol)
            
            if current_price:
                print(f"\n{symbol}:")
                print(f"   Position: {bot.position}")
                print(f"   Price: ${current_price:,.2f}")
                
                if bot.position == base_currency:
                    # Holding crypto - show entry and targets
                    if bot.strategy.last_buy_price:
                        profit_pct = ((current_price - bot.strategy.last_buy_price) / 
                                     bot.strategy.last_buy_price) * 100
                        print(f"   Entry: ${bot.strategy.last_buy_price:,.2f}")
                        print(f"   P&L: {profit_pct:+.2f}%")
                        
                        sell_target = bot.strategy.last_buy_price * (1 + bot.strategy.sell_threshold / 100)
                        print(f"   Sell Target: ${sell_target:,.2f} ({bot.strategy.sell_threshold}%)")
                else:
                    # Holding USDT - show buy target
                    if bot.strategy.last_sell_price:
                        buy_target = bot.strategy.last_sell_price * (1 - bot.strategy.buy_threshold / 100)
                        print(f"   Buy Target: ${buy_target:,.2f} ({bot.strategy.buy_threshold}%)")
                
                # Show stats
                stats = bot.strategy.get_stats()
                print(f"   Trades: {stats['total_trades']} | Win Rate: {stats['win_rate']:.1f}%")
        
        print("\n" + "=" * 80)
    
    def monitor(self):
        """Monitor all bots and print combined status periodically"""
        self.logger.info("Starting monitoring loop...")
        
        try:
            while self.running:
                # Print combined status every 60 seconds
                time.sleep(60)
                
                if self.running:
                    self.print_combined_status()
                    
        except KeyboardInterrupt:
            pass


def main():
    """
    Initialize and run multiple trading bots
    
    Creates separate bot instances for each trading pair,
    runs them in parallel threads, and monitors their status.
    """
    try:
        # Display startup banner
        print_banner()
        
        # Setup logger
        logger = setup_logger('Main')
        logger.info("Initializing Multi-Bot Trading System...")
        
        # Define trading pairs
        symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
        
        print("\n🤖 Multi-Bot Trading System")
        print(f"   Trading Pairs: {', '.join(symbols)}")
        print()
        
        # Create exchange instance (shared by all bots)
        logger.info("Connecting to Binance Testnet...")
        exchange = BinanceTestnet(config.BINANCE_API_KEY, config.BINANCE_SECRET)
        
        # Verify connection
        balance = exchange.get_balance()
        
        if balance is None:
            logger.error("Failed to connect to exchange")
            print("❌ Connection failed: Unable to retrieve account balance")
            print("   Please check your API keys and network connection")
            return
        
        # Display starting balance
        print("💰 Starting Balance:")
        print(f"   USDT: ${balance.get('USDT', 0.0):,.2f}")
        for symbol in symbols:
            base_currency = symbol.split('/')[0]
            amount = balance.get(base_currency, 0.0)
            print(f"   {base_currency}:  {amount:.6f}")
        print()
        
        # Initialize AI advisor (shared by all bots)
        if config.AI_ENABLED:
            logger.info("Initializing AI Advisor...")
            ai_advisor = AIAdvisor(api_url=config.AI_API_URL)
        else:
            logger.info("AI Advisor is disabled")
            print("⚠️  AI Advisor: DISABLED")
            print()
            ai_advisor = AIAdvisor(api_url="")
        
        # Display strategy settings
        print("📊 Strategy Settings (Applied to all bots):")
        print(f"   Buy Threshold: {config.BUY_THRESHOLD}%")
        print(f"   Sell Threshold: {config.SELL_THRESHOLD}%")
        print(f"   Trade Amount: {config.TRADE_AMOUNT} BTC")
        print(f"   Check Interval: {config.CHECK_INTERVAL} seconds")
        print()
        
        # Create multi-bot manager
        logger.info("Creating Multi-Bot Manager...")
        manager = MultiBotManager(symbols, exchange, ai_advisor)
        
        # Create all bots
        manager.create_bots()
        
        print("\n" + "=" * 80)
        print("🚀 Starting all bots...")
        print("=" * 80)
        print("Press Ctrl+C to stop all bots")
        print("=" * 80)
        print()
        
        # Start all bots
        manager.start_all()
        
        # Give bots time to initialize
        time.sleep(2)
        
        # Print initial combined status
        manager.print_combined_status()
        
        # Monitor bots (blocks until Ctrl+C)
        manager.monitor()
        
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user (Ctrl+C)")
        print("\n👋 Goodbye!")
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        print(f"\n❌ Fatal error: {str(e)}")
        raise


if __name__ == "__main__":
    main()

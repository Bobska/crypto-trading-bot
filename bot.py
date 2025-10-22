"""
Trading Bot Module
Main trading bot that coordinates exchange, strategy, and AI advisor
"""
import time
import traceback
from logger_setup import setup_logger

class TradingBot:
    """
    Cryptocurrency Trading Bot
    
    Coordinates between exchange connection, trading strategy, and AI advisor
    to execute automated trading decisions. Monitors price movements and 
    executes trades based on strategy signals with optional AI consultation.
    
    The bot runs continuously, checking prices at regular intervals and
    maintaining position state (USDT or BTC).
    """
    
    def __init__(self, exchange, strategy, ai_advisor, symbol: str, check_interval: int):
        """
        Initialize Trading Bot
        
        Args:
            exchange: Exchange instance for API communication
            strategy: Trading strategy instance for signal generation
            ai_advisor: AI advisor instance for trade recommendations
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            check_interval: Seconds between price checks
        """
        self.exchange = exchange
        self.strategy = strategy
        self.ai_advisor = ai_advisor
        self.symbol = symbol
        self.check_interval = check_interval
        
        # Initialize bot state
        self.position = 'USDT'  # Starting with cash (not holding BTC)
        self.running = False
        
        # Setup logging
        self.logger = setup_logger('TradingBot')
        
        # Log initialization
        self.logger.info(f"Trading Bot initialized for {symbol}")
        self.logger.info(f"Check interval: {check_interval} seconds")
        self.logger.info(f"Starting position: {self.position}")
    
    def print_status(self, current_price: float) -> None:
        """
        Print current bot status with price, position, balance, and stats
        
        Args:
            current_price: Current price of the trading pair
        """
        # Get current stats and balance
        stats = self.strategy.get_stats()
        balance = self.exchange.get_balance()
        
        # Format price with commas
        formatted_price = f"${current_price:,.2f}"
        
        # Print status box
        print()
        print("=" * 60)
        print("🤖 TRADING BOT STATUS")
        print("=" * 60)
        print(f"Symbol: {self.symbol}")
        print(f"Current Price: {formatted_price}")
        print(f"Position: {self.position}")
        print(f"Balance: ${balance.get('USDT', 0.0):.2f} USDT | {balance.get('BTC', 0.0):.6f} BTC")
        print(f"Stats: {stats['total_trades']} trades | {stats['wins']} wins | {stats['losses']} losses | {stats['win_rate']:.1f}% win rate")
        print("=" * 60)
        print()
    
    def execute_trade(self, signal: str, price: float) -> bool:
        """
        Execute a trade based on signal
        
        Args:
            signal: Trade signal ('BUY' or 'SELL')
            price: Current price for the trade
            
        Returns:
            True if trade executed successfully, False otherwise
        """
        if signal == 'BUY':
            # Log buy execution attempt
            self.logger.info(f"🟢 Executing BUY order at ${price:,.2f}")
            
            # Place market buy order
            order = self.exchange.place_market_buy(self.symbol, self.strategy.trade_amount)
            
            if order:
                # Record successful buy
                self.strategy.record_buy(price)
                self.position = 'BTC'
                self.logger.info(f"✅ BUY order successful - Position changed to BTC")
                return True
            else:
                # Log failure
                self.logger.error(f"❌ BUY order failed")
                return False
        
        elif signal == 'SELL':
            # Log sell execution attempt
            self.logger.info(f"🔴 Executing SELL order at ${price:,.2f}")
            
            # Place market sell order
            order = self.exchange.place_market_sell(self.symbol, self.strategy.trade_amount)
            
            if order:
                # Record successful sell
                self.strategy.record_sell(price)
                self.position = 'USDT'
                self.logger.info(f"✅ SELL order successful - Position changed to USDT")
                return True
            else:
                # Log failure
                self.logger.error(f"❌ SELL order failed")
                return False
        
        else:
            # Invalid signal
            return False
    
    def run(self) -> None:
        """
        Start the trading bot main loop
        
        Continuously monitors price and executes trades based on strategy signals.
        Runs until interrupted by user (Ctrl+C).
        """
        # Set running flag
        self.running = True
        
        # Log startup
        self.logger.info(f"🚀 Trading Bot starting...")
        
        # Print user-friendly startup messages
        print()
        print("=" * 60)
        print("🚀 Trading Bot is now running!")
        print("=" * 60)
        print(f"Symbol: {self.symbol}")
        print(f"Check Interval: {self.check_interval} seconds")
        print()
        print("Press Ctrl+C to stop")
        print("=" * 60)
        print()
        
        try:
            # Initialize iteration counter
            iteration = 0
            
            # Main trading loop
            while self.running:
                iteration += 1
                
                # 1. Get current price
                current_price = self.exchange.get_current_price(self.symbol)
                
                if current_price is None:
                    self.logger.warning("⚠️ Failed to get current price, skipping iteration")
                    time.sleep(self.check_interval)
                    continue
                
                # 2. Get trading signal
                signal = self.strategy.analyze(current_price, self.position)
                
                # 3. Print status every 10 iterations OR when signal != 'HOLD'
                if iteration % 10 == 0 or signal != 'HOLD':
                    self.print_status(current_price)
                
                # 4. Execute trade if signal is not HOLD
                if signal != 'HOLD':
                    # Get current stats
                    stats = self.strategy.get_stats()
                    
                    # Get AI recommendation
                    ai_advice = self.ai_advisor.analyze_trade_opportunity(signal, current_price, stats)
                    
                    # Execute the trade
                    self.execute_trade(signal, current_price)
                
                # 5. Sleep for check interval
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            # Handle user interruption
            self.logger.info("⏸️ Bot stopped by user")
            print("\n👋 Trading Bot stopped by user")
            self.stop()
            
        except Exception as e:
            # Handle unexpected errors
            self.logger.error(f"❌ Unexpected error: {str(e)}")
            self.logger.error(traceback.format_exc())
            print(f"\n❌ Error occurred: {str(e)}")
            self.stop()
    
    def stop(self) -> None:
        """
        Stop the trading bot gracefully
        """
        self.running = False
        self.logger.info("Trading Bot stopped")
        print("Bot has been stopped")

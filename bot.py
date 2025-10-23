"""
Trading Bot Module
Main trading bot that coordinates exchange, strategy, and AI advisor
"""
import time
import traceback
from datetime import datetime, timedelta
from typing import List, Tuple
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
        
        # Price alert tracking (for volatility detection)
        self.price_history: List[Tuple[datetime, float]] = []
        self.price_alert_threshold = 2.0  # 2% price change alert
        self.price_tracking_window = 300  # 5 minutes in seconds
        
        # Setup logging
        self.logger = setup_logger('TradingBot')
        
        # Log initialization
        self.logger.info(f"Trading Bot initialized for {symbol}")
        self.logger.info(f"Check interval: {check_interval} seconds")
        self.logger.info(f"Starting position: {self.position}")
        self.logger.info(f"Price alert threshold: {self.price_alert_threshold}%")
    
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
    
    def check_price_alerts(self, current_price: float) -> None:
        """
        Check for rapid price movements and alert on high volatility
        
        Tracks price history over the last 5 minutes and alerts if price
        moves more than 2% in either direction. Helps identify volatile
        market conditions that may require trading pause.
        
        Args:
            current_price: Current market price
        """
        current_time = datetime.now()
        
        # Add current price to history
        self.price_history.append((current_time, current_price))
        
        # Remove prices older than tracking window (5 minutes)
        cutoff_time = current_time - timedelta(seconds=self.price_tracking_window)
        self.price_history = [
            (timestamp, price) 
            for timestamp, price in self.price_history 
            if timestamp > cutoff_time
        ]
        
        # Need at least 2 data points to compare
        if len(self.price_history) < 2:
            return
        
        # Get oldest price in the window
        oldest_time, oldest_price = self.price_history[0]
        
        # Calculate price change percentage
        price_change = current_price - oldest_price
        price_change_percent = (price_change / oldest_price) * 100
        
        # Check if change exceeds threshold
        if abs(price_change_percent) >= self.price_alert_threshold:
            # Calculate time window
            time_diff = (current_time - oldest_time).total_seconds() / 60  # in minutes
            
            # Determine direction
            direction = "UP" if price_change > 0 else "DOWN"
            
            # Log warning with details
            self.logger.warning(f"⚠️ PRICE ALERT: {direction} {abs(price_change_percent):.2f}% in {time_diff:.1f} minutes")
            self.logger.warning(f"⚠️ Price moved from ${oldest_price:,.2f} to ${current_price:,.2f}")
            self.logger.warning(f"⚠️ High volatility detected - consider pausing trading")
            
            # Print console alert (visible to user)
            print()
            print("⚠️" + "=" * 58 + "⚠️")
            print(f"   VOLATILITY ALERT: Price {direction} {abs(price_change_percent):.2f}%")
            print(f"   From: ${oldest_price:,.2f} → To: ${current_price:,.2f}")
            print(f"   Time Window: {time_diff:.1f} minutes")
            print(f"   Recommendation: Monitor closely or pause trading")
            print("⚠️" + "=" * 58 + "⚠️")
            print()
            
            # Optionally notify AI about volatility
            if self.ai_advisor and self.ai_advisor.enabled:
                volatility_message = f"""High volatility detected:
- Price moved {direction} {abs(price_change_percent):.2f}% in {time_diff:.1f} minutes
- From ${oldest_price:,.2f} to ${current_price:,.2f}
- Current position: {self.position}

Should I pause trading during this volatile period?"""
                
                try:
                    ai_response = self.ai_advisor._send_message(volatility_message)
                    if ai_response:
                        self.logger.info(f"🤖 AI Volatility Advice: {ai_response[:200]}...")
                except Exception as e:
                    self.logger.debug(f"Could not get AI volatility advice: {e}")
    
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
                
                # 2. Check for price alerts (high volatility detection)
                self.check_price_alerts(current_price)
                
                # 3. Check stop-loss (emergency sell if triggered)
                if self.strategy.check_stop_loss(current_price, self.position):
                    self.logger.warning("⚠️ STOP LOSS: Executing emergency sell")
                    self.print_status(current_price)
                    self.execute_trade('SELL', current_price)
                    time.sleep(self.check_interval)
                    continue
                
                # 4. Get trading signal
                signal = self.strategy.analyze(current_price, self.position)
                
                # 5. Print status every 10 iterations OR when signal != 'HOLD'
                if iteration % 10 == 0 or signal != 'HOLD':
                    self.print_status(current_price)
                
                # 6. Execute trade if signal is not HOLD
                if signal != 'HOLD':
                    # Get current stats
                    stats = self.strategy.get_stats()
                    
                    # Get AI recommendation
                    ai_advice = self.ai_advisor.analyze_trade_opportunity(signal, current_price, stats)
                    
                    # Execute the trade
                    self.execute_trade(signal, current_price)
                
                # 7. Sleep for check interval
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
        Stop the trading bot gracefully and send daily summary to AI
        """
        self.running = False
        
        # Get final statistics and balance
        final_stats = self.strategy.get_stats()
        final_balance = self.exchange.get_balance()
        
        # Send daily summary to AI advisor
        self.ai_advisor.send_daily_summary(final_stats, final_balance)
        
        # Log shutdown
        self.logger.info("Trading Bot stopped")
        print("Bot has been stopped")

"""
Trading Bot Module
Main trading bot that coordinates exchange, strategy, and AI advisor
"""
import json
import time
import traceback
import asyncio
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
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
    
    def __init__(self, exchange, strategy, ai_advisor, symbol: str, check_interval: int, require_ai_confirmation: bool = False):
        """
        Initialize Trading Bot
        
        Args:
            exchange: Exchange instance for API communication
            strategy: Trading strategy instance for signal generation
            ai_advisor: AI advisor instance for trade recommendations
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            check_interval: Seconds between price checks
            require_ai_confirmation: If True, requires AI approval before executing trades
        """
        self.exchange = exchange
        self.strategy = strategy
        self.ai_advisor = ai_advisor
        self.symbol = symbol
        self.check_interval = check_interval
        self.require_ai_confirmation = require_ai_confirmation
        
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
        self.logger.info(f"AI Confirmation Required: {self.require_ai_confirmation}")
        
        # Load saved state if it exists
        self.load_state()
        
        # Verify position matches actual balance
        balance = self.exchange.get_balance()
        
        if balance is not None:
            # Check if actual holdings match saved position
            btc_balance = balance.get('BTC', 0.0)
            
            if btc_balance > 0.0001 and self.position == 'USDT':
                # Have BTC but state says USDT - override to BTC
                self.position = 'BTC'
                self.logger.warning(f"🔍 Balance check: Detected BTC holdings ({btc_balance:.6f}), overriding position to BTC")
                
            elif btc_balance <= 0.0001 and self.position == 'BTC':
                # No BTC but state says BTC - override to USDT
                self.position = 'USDT'
                self.logger.warning(f"🔍 Balance check: No BTC detected ({btc_balance:.6f}), overriding position to USDT")
            
            # If holding BTC but no buy price, estimate from current price
            if self.position == 'BTC' and (self.strategy.last_buy_price is None or self.strategy.last_buy_price == 0.0):
                current_price = self.exchange.get_current_price(self.symbol)
                if current_price:
                    self.strategy.last_buy_price = current_price
                    self.logger.warning(f"⚠️ No buy price found, estimating from current price: ${current_price:,.2f}")
                    self.logger.warning(f"⚠️ Profit tracking will be based on this estimated entry price")
            
            # Save corrected state
            self.save_state()
        
        # Log final confirmed position
        self.logger.info(f"Starting with position: {self.position}")
    
    def _broadcast_update(self, message_type: str, data: dict) -> None:
        """
        Send update to all WebSocket clients via bot_api
        
        Args:
            message_type: Type of update (e.g., 'trade_executed', 'price_update', 'status_change')
            data: Update data dictionary
        """
        try:
            import sys
            if 'bot_api' in sys.modules:
                from bot_api import manager
                # Run async broadcast in sync context
                asyncio.run(manager.broadcast({
                    "type": message_type,
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                }))
        except Exception as e:
            self.logger.debug(f"WebSocket broadcast failed (API may not be running): {e}")
    
    def save_state(self) -> None:
        """
        Save bot state to JSON file for persistence across restarts
        
        Saves current position and strategy prices to allow resuming
        trading from the same state after bot restart.
        """
        try:
            state = {
                'position': self.position,
                'last_buy_price': self.strategy.last_buy_price,
                'last_sell_price': self.strategy.last_sell_price
            }
            
            with open('bot_state.json', 'w') as f:
                json.dump(state, f, indent=2)
            
            self.logger.info("State saved")
            
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
    
    def load_state(self) -> None:
        """
        Load bot state from JSON file if it exists
        
        Restores position and strategy prices from previous session.
        If no saved state exists, starts fresh with default values.
        Estimates buy price from current market price if holding BTC without reference.
        """
        try:
            with open('bot_state.json', 'r') as f:
                state = json.load(f)
            
            # Restore state
            self.position = state.get('position', 'USDT')
            self.strategy.last_buy_price = state.get('last_buy_price') or 0.0
            self.strategy.last_sell_price = state.get('last_sell_price') or 0.0
            
            # If holding BTC but no buy price recorded, estimate from current price
            if self.position == 'BTC' and (self.strategy.last_buy_price is None or self.strategy.last_buy_price == 0.0):
                current_price = self.exchange.get_current_price(self.symbol)
                if current_price:
                    self.strategy.last_buy_price = current_price
                    self.logger.warning(f"⚠️ No buy price found, estimating from current price: ${current_price:,.2f}")
                    self.logger.warning(f"⚠️ Profit tracking will be based on this estimated entry price")
                    # Save the estimated price
                    self.save_state()
            
            # Log loaded state (after estimation)
            buy_price_str = f"${self.strategy.last_buy_price:,.2f}" if self.strategy.last_buy_price else "None"
            sell_price_str = f"${self.strategy.last_sell_price:,.2f}" if self.strategy.last_sell_price else "None"
            self.logger.info(f"State loaded - Position: {self.position}, Last Buy: {buy_price_str}, Last Sell: {sell_price_str}")
            
        except FileNotFoundError:
            self.logger.info("No saved state found, starting fresh")
        except Exception as e:
            self.logger.error(f"Failed to load state: {e}")
            self.logger.info("Starting with default state")
    
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
        
        # Show target prices based on current position
        if self.position == 'BTC' and self.strategy.last_buy_price is not None:
            # Holding BTC - show target sell price
            target_sell_price = self.strategy.last_buy_price * (1 + self.strategy.sell_threshold / 100)
            print(f"   Target Sell Price: ${target_sell_price:,.2f} (waiting for {self.strategy.sell_threshold}% gain)")
        elif self.position == 'USDT' and self.strategy.last_sell_price is not None:
            # Holding USDT after a sell - show target buy price
            target_buy_price = self.strategy.last_sell_price * (1 - self.strategy.buy_threshold / 100)
            print(f"   Target Buy Price: ${target_buy_price:,.2f} (waiting for {self.strategy.buy_threshold}% drop)")
        elif self.position == 'USDT' and self.strategy.last_sell_price is None:
            # First time - waiting for initial entry
            print(f"   Waiting for first buy opportunity at current market price")
        
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
                
                # Broadcast trade update
                self._broadcast_update("trade_executed", {
                    "action": "BUY",
                    "price": price,
                    "amount": self.strategy.trade_amount,
                    "position": self.position
                })
                
                # Save state after successful trade
                self.save_state()
                
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
                
                # Calculate profit percentage
                profit_pct = 0.0
                if self.strategy.last_buy_price and self.strategy.last_buy_price > 0:
                    profit_pct = ((price - self.strategy.last_buy_price) / self.strategy.last_buy_price) * 100
                
                # Broadcast trade update
                self._broadcast_update("trade_executed", {
                    "action": "SELL",
                    "price": price,
                    "amount": self.strategy.trade_amount,
                    "position": self.position,
                    "profit_pct": round(profit_pct, 2)
                })
                
                # Adjust position size based on performance
                balance = self.exchange.get_balance()
                stats = self.strategy.get_stats()
                if balance and stats:
                    self.strategy.adjust_position_size(balance, stats['win_rate'])
                
                # Save state after successful trade
                self.save_state()
                
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
    
    def _parse_ai_confirmation(self, ai_response: str) -> bool:
        """
        Parse AI response to determine if trade should proceed
        
        Looks for positive keywords indicating approval or negative
        keywords indicating the trade should be avoided.
        
        Args:
            ai_response: AI advisor's response text
            
        Returns:
            True if AI approves the trade, False if AI suggests avoiding it
        """
        if not ai_response:
            return False
        
        # Convert to lowercase for case-insensitive matching
        response_lower = ai_response.lower()
        
        # Positive keywords (AI approves trade)
        positive_keywords = [
            'yes', 'proceed', 'go ahead', 'good', 'take', 'execute',
            'approve', 'favorable', 'recommend', 'looks good', 'agree',
            'positive', 'buy it', 'sell it', 'do it', 'take it'
        ]
        
        # Negative keywords (AI blocks trade)
        negative_keywords = [
            'no', 'wait', 'avoid', 'don\'t', 'do not', 'hold off',
            'pause', 'skip', 'risky', 'caution', 'reconsider',
            'unfavorable', 'against', 'decline', 'reject'
        ]
        
        # Count matches
        positive_count = sum(1 for keyword in positive_keywords if keyword in response_lower)
        negative_count = sum(1 for keyword in negative_keywords if keyword in response_lower)
        
        # Log parsing results
        self.logger.debug(f"AI response parsing: {positive_count} positive, {negative_count} negative keywords")
        
        # Decision logic: positive wins if more positive than negative
        # Default to False (block) if unclear or equal
        if positive_count > negative_count and positive_count > 0:
            return True
        else:
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
        
        # Broadcast status change
        self._broadcast_update("status_change", {
            "status": "running",
            "symbol": self.symbol
        })
        
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
                
                # Broadcast price update every 10 iterations (reduce broadcast frequency)
                if iteration % 10 == 0:
                    self._broadcast_update("price_update", {
                        "price": current_price,
                        "symbol": self.symbol,
                        "position": self.position
                    })
                
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
                    
                    # Check if AI confirmation is required
                    if self.require_ai_confirmation:
                        if ai_advice is None:
                            # No AI response, skip trade
                            self.logger.warning(f"🛑 AI CONFIRMATION: No AI response received, skipping {signal} trade")
                            time.sleep(self.check_interval)
                            continue
                        
                        # Parse AI response for confirmation
                        ai_approved = self._parse_ai_confirmation(ai_advice)
                        
                        if ai_approved:
                            self.logger.info(f"✅ AI CONFIRMATION: AI approved {signal} trade at ${current_price:,.2f}")
                            # Execute the trade
                            self.execute_trade(signal, current_price)
                        else:
                            self.logger.warning(f"🛑 AI BLOCKED TRADE: AI advised against {signal} at ${current_price:,.2f}")
                            self.logger.info(f"🛑 AI Reasoning: {ai_advice[:150]}...")
                            print(f"\n⚠️  Trade blocked by AI advisor")
                            print(f"   Signal: {signal} at ${current_price:,.2f}")
                            print(f"   AI said: {ai_advice[:100]}...")
                    else:
                        # No AI confirmation required, execute directly
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
        
        # Broadcast status change
        self._broadcast_update("status_change", {
            "status": "stopped"
        })
        
        # Save state before shutdown
        self.save_state()
        
        # Get final statistics and balance
        final_stats = self.strategy.get_stats()
        final_balance = self.exchange.get_balance()
        
        # Send daily summary to AI advisor
        self.ai_advisor.send_daily_summary(final_stats, final_balance)
        
        # Log shutdown
        self.logger.info("Trading Bot stopped")
        print("Bot has been stopped")

"""
Grid Trading Strategy Implementation
Automated buy/sell strategy based on price movement thresholds
"""
from logger_setup import setup_logger
from typing import Optional

class GridTradingStrategy:
    """
    Grid Trading Strategy
    
    A systematic trading approach that places buy and sell orders at predetermined
    price intervals (grid levels). The strategy profits from market volatility by:
    
    - Buying when price drops by the buy_threshold percentage
    - Selling when price rises by the sell_threshold percentage
    - Maintaining a grid of orders to capture price movements in both directions
    
    Key Benefits:
    - Works well in sideways/ranging markets
    - Automatically takes profits on price swings
    - Reduces emotional trading decisions
    - Consistent execution based on predetermined rules
    
    Risk Considerations:
    - Can accumulate losses in strong trending markets
    - Requires sufficient capital for multiple grid levels
    - May miss opportunities in fast-moving markets
    """
    
    def __init__(self, buy_threshold: float, sell_threshold: float, trade_amount: float):
        """
        Initialize Grid Trading Strategy
        
        Args:
            buy_threshold: Percentage drop to trigger buy orders (e.g., 1.0 for 1%)
            sell_threshold: Percentage rise to trigger sell orders (e.g., 1.0 for 1%)
            trade_amount: Amount to trade per order (base currency)
        """
        self.logger = setup_logger('GridTradingStrategy')
        
        # Trading thresholds (as percentages)
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.trade_amount = trade_amount
        
        # Price tracking for grid logic
        self.last_buy_price: Optional[float] = None
        self.last_sell_price: Optional[float] = None
        
        # Strategy statistics
        self.total_trades = 0
        self.wins = 0
        self.losses = 0
        
        # Log initialization
        self.logger.info("Grid Trading Strategy initialized")
        self.logger.info(f"Buy threshold: {self.buy_threshold}%")
        self.logger.info(f"Sell threshold: {self.sell_threshold}%")
        self.logger.info(f"Trade amount: {self.trade_amount}")
        self.logger.info("Strategy ready for execution")
    
    def get_strategy_stats(self) -> dict:
        """
        Get current strategy statistics
        
        Returns:
            Dictionary containing strategy performance metrics
        """
        win_rate = (self.wins / self.total_trades * 100) if self.total_trades > 0 else 0
        
        stats = {
            'total_trades': self.total_trades,
            'wins': self.wins,
            'losses': self.losses,
            'win_rate': win_rate,
            'last_buy_price': self.last_buy_price,
            'last_sell_price': self.last_sell_price,
            'buy_threshold': self.buy_threshold,
            'sell_threshold': self.sell_threshold,
            'trade_amount': self.trade_amount
        }
        
        return stats
    
    def reset_strategy(self):
        """
        Reset strategy state and statistics
        Useful for starting fresh or switching markets
        """
        self.last_buy_price = None
        self.last_sell_price = None
        self.total_trades = 0
        self.wins = 0
        self.losses = 0
        
        self.logger.info("Strategy state reset - all statistics cleared")
    
    def update_thresholds(self, buy_threshold: float, sell_threshold: float):
        """
        Update trading thresholds dynamically
        
        Args:
            buy_threshold: New buy threshold percentage
            sell_threshold: New sell threshold percentage
        """
        old_buy = self.buy_threshold
        old_sell = self.sell_threshold
        
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        
        self.logger.info(f"Thresholds updated - Buy: {old_buy}% -> {buy_threshold}%, Sell: {old_sell}% -> {sell_threshold}%")
    
    def analyze(self, current_price: float, position: str) -> str:
        """
        Analyze current market conditions and return trading signal
        
        Args:
            current_price: Current market price of the trading pair
            position: Current position ('USDT' for cash, 'BTC' for holding crypto)
            
        Returns:
            Trading signal: 'BUY', 'SELL', or 'HOLD'
        """
        self.logger.debug(f"Analyzing price: ${current_price:,.2f}, Position: {position}")
        
        if position == 'USDT':
            # Holding cash (USDT) - looking for buy opportunities
            
            if self.last_sell_price is None:
                # First trade opportunity - no previous sell price to compare
                self.logger.info(f"First trade opportunity detected at ${current_price:,.2f}")
                self.logger.info("🟢 BUY SIGNAL: Initial entry into market")
                return 'BUY'
            
            # Calculate price drop from last sell
            price_drop = ((self.last_sell_price - current_price) / self.last_sell_price) * 100
            
            self.logger.debug(f"Price drop calculation: (${self.last_sell_price:,.2f} - ${current_price:,.2f}) / ${self.last_sell_price:,.2f} * 100 = {price_drop:.2f}%")
            
            if price_drop >= self.buy_threshold:
                # Price has dropped enough to trigger buy signal
                price_change = self.last_sell_price - current_price
                self.logger.info(f"🟢 BUY SIGNAL: Price dropped {price_drop:.2f}% (-${price_change:,.2f}) from ${self.last_sell_price:,.2f} to ${current_price:,.2f}")
                self.logger.info(f"Drop threshold met: {price_drop:.2f}% >= {self.buy_threshold}%")
                return 'BUY'
            else:
                # Price hasn't dropped enough yet
                self.logger.debug(f"HOLD: Price drop {price_drop:.2f}% below buy threshold of {self.buy_threshold}%")
                self.logger.debug(f"Need ${self.last_sell_price * (1 - self.buy_threshold/100):,.2f} or lower to trigger buy")
                return 'HOLD'
        
        elif position == 'BTC':
            # Holding BTC - looking for sell opportunities
            
            if self.last_buy_price is None:
                # No previous buy price to compare - shouldn't happen in normal operation
                self.logger.warning(f"No last_buy_price recorded while holding BTC at ${current_price:,.2f}")
                self.logger.warning("Cannot determine sell signal without buy reference price")
                return 'HOLD'
            
            # Calculate price rise from last buy
            price_rise = ((current_price - self.last_buy_price) / self.last_buy_price) * 100
            
            self.logger.debug(f"Price rise calculation: (${current_price:,.2f} - ${self.last_buy_price:,.2f}) / ${self.last_buy_price:,.2f} * 100 = {price_rise:.2f}%")
            
            if price_rise >= self.sell_threshold:
                # Price has risen enough to trigger sell signal
                price_change = current_price - self.last_buy_price
                self.logger.info(f"🔴 SELL SIGNAL: Price rose {price_rise:.2f}% (+${price_change:,.2f}) from ${self.last_buy_price:,.2f} to ${current_price:,.2f}")
                self.logger.info(f"Rise threshold met: {price_rise:.2f}% >= {self.sell_threshold}%")
                return 'SELL'
            else:
                # Price hasn't risen enough yet
                self.logger.debug(f"HOLD: Price rise {price_rise:.2f}% below sell threshold of {self.sell_threshold}%")
                self.logger.debug(f"Need ${self.last_buy_price * (1 + self.sell_threshold/100):,.2f} or higher to trigger sell")
                return 'HOLD'
        
        else:
            # Unknown position - return HOLD as default
            self.logger.warning(f"Unknown position '{position}' - valid positions are 'USDT' or 'BTC'")
            return 'HOLD'
    
    def record_buy(self, price: float) -> None:
        """
        Record a buy trade execution
        
        Args:
            price: The executed buy price
        """
        self.last_buy_price = price
        self.total_trades += 1
        
        self.logger.info(f"📝 BUY RECORDED: ${price:,.2f} (Trade #{self.total_trades})")
    
    def record_sell(self, price: float) -> None:
        """
        Record a sell trade execution and calculate P&L
        
        Args:
            price: The executed sell price
        """
        self.last_sell_price = price
        self.total_trades += 1
        
        if self.last_buy_price is not None:
            # Calculate profit/loss percentage
            profit_loss_pct = ((price - self.last_buy_price) / self.last_buy_price) * 100
            profit_loss_amount = price - self.last_buy_price
            
            if profit_loss_pct > 0:
                # Profitable trade
                self.wins += 1
                self.logger.info(f"📝 SELL RECORDED: ${price:,.2f} (Trade #{self.total_trades})")
                self.logger.info(f"✅ PROFIT: +{profit_loss_pct:.2f}% (+${profit_loss_amount:,.2f}) - Buy: ${self.last_buy_price:,.2f} -> Sell: ${price:,.2f}")
            else:
                # Loss or break-even trade
                self.losses += 1
                self.logger.info(f"📝 SELL RECORDED: ${price:,.2f} (Trade #{self.total_trades})")
                self.logger.info(f"❌ LOSS: {profit_loss_pct:.2f}% (${profit_loss_amount:,.2f}) - Buy: ${self.last_buy_price:,.2f} -> Sell: ${price:,.2f}")
        else:
            # No buy price recorded (shouldn't happen in normal operation)
            self.logger.info(f"📝 SELL RECORDED: ${price:,.2f} (Trade #{self.total_trades})")
            self.logger.warning("No corresponding buy price found - cannot calculate P&L")
    
    def get_stats(self) -> dict:
        """
        Get strategy performance statistics
        
        Returns:
            Dictionary with trading performance metrics
        """
        win_rate = (self.wins / self.total_trades * 100) if self.total_trades > 0 else 0
        
        return {
            'total_trades': self.total_trades,
            'wins': self.wins,
            'losses': self.losses,
            'win_rate': win_rate
        }
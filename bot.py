"""
Trading Bot Module
Main trading bot that coordinates exchange, strategy, and AI advisor
"""
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

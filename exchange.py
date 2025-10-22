"""
Binance Testnet Exchange Integration
Handles connection and configuration for Binance testnet trading
"""
import ccxt
from typing import Optional, Dict, Any
from logger_setup import setup_logger

class BinanceTestnet:
    """
    Binance Testnet exchange wrapper using ccxt
    Provides safe testnet trading environment with proper error handling
    """
    
    def __init__(self, api_key: str, secret: str):
        """
        Initialize Binance testnet connection
        
        Args:
            api_key: Binance testnet API key
            secret: Binance testnet secret key
        """
        self.logger = setup_logger('BinanceTestnet')
        self.exchange: Optional[ccxt.binance] = None
        
        try:
            # Initialize ccxt Binance exchange instance for testnet
            self.exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': secret,
                'sandbox': True,  # Enable testnet/sandbox mode
                'rateLimit': True,  # Enable built-in rate limiting
                'enableRateLimit': True,  # Additional rate limit protection
                'urls': {
                    'api': {
                        'public': 'https://testnet.binance.vision/api/v3',
                        'private': 'https://testnet.binance.vision/api/v3',
                        'fapiPublic': 'https://testnet.binancefuture.com/fapi/v1',
                        'fapiPrivate': 'https://testnet.binancefuture.com/fapi/v1',
                    }
                },
                'options': {
                    'defaultType': 'spot',  # Use spot trading
                }
            })
            
            # Test the connection
            self._test_connection()
            
            self.logger.info("Successfully connected to Binance Testnet")
            self.logger.info(f"Exchange ID: {self.exchange.id}")
            self.logger.info(f"Rate limit enabled: {self.exchange.rateLimit}")
            self.logger.info(f"Sandbox mode enabled: True")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Binance testnet connection: {str(e)}")
            self.exchange = None
            raise ConnectionError(f"Could not connect to Binance testnet: {str(e)}")
    
    def _test_connection(self):
        """
        Test the exchange connection by fetching server time
        Raises exception if connection fails
        """
        if not self.exchange:
            raise RuntimeError("Exchange not initialized")
            
        try:
            # Simple test to verify connection works
            server_time = self.exchange.fetch_time()
            self.logger.info(f"Connection test successful - Server time: {server_time}")
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            raise
    
    def is_connected(self) -> bool:
        """
        Check if exchange connection is established
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self.exchange is not None
    
    def get_exchange_info(self) -> Dict[str, Any]:
        """
        Get basic exchange information
        
        Returns:
            dict: Exchange information including markets, limits, etc.
        """
        if not self.is_connected():
            raise RuntimeError("Exchange not connected")
        
        if not self.exchange:
            raise RuntimeError("Exchange not initialized")
        
        try:
            # For testnet, we'll get basic info without loading all markets
            # since testnet has limited API endpoint support
            info = {
                'id': self.exchange.id,
                'name': getattr(self.exchange, 'name', 'Binance Testnet'),
                'sandbox': True,  # We know this is testnet
                'rateLimit': self.exchange.rateLimit,
                'has_fetch_ticker': self.exchange.has.get('fetchTicker', False),
                'has_create_order': self.exchange.has.get('createOrder', False),
                'has_fetch_balance': self.exchange.has.get('fetchBalance', False),
                'has_fetch_order_book': self.exchange.has.get('fetchOrderBook', False),
            }
            
            self.logger.info("Exchange info retrieved for testnet environment")
            return info
            
        except Exception as e:
            self.logger.error(f"Failed to get exchange info: {str(e)}")
            raise
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current market price for a trading symbol
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            
        Returns:
            Current price as float, or None if failed
        """
        if not self.is_connected():
            self.logger.error("Cannot get price - exchange not connected")
            return None
        
        if not self.exchange:
            self.logger.error("Cannot get price - exchange not initialized")
            return None
        
        try:
            # For testnet compatibility, we'll try different approaches
            # First try the standard ticker method
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                current_price = float(ticker['last'])
            except Exception as ticker_error:
                self.logger.warning(f"Standard ticker failed for {symbol}, trying order book method: {str(ticker_error)}")
                # Fallback to order book method which works better with testnet
                order_book = self.exchange.fetch_order_book(symbol)
                # Use the midpoint between best bid and ask
                if order_book['bids'] and order_book['asks']:
                    best_bid = float(order_book['bids'][0][0])
                    best_ask = float(order_book['asks'][0][0])
                    current_price = (best_bid + best_ask) / 2
                else:
                    raise Exception("No bid/ask data available")
            
            # Log with formatted output
            formatted_price = f"${current_price:,.2f}"
            self.logger.info(f"Current price for {symbol}: {formatted_price}")
            
            return current_price
            
        except Exception as e:
            self.logger.error(f"Failed to get current price for {symbol}: {str(e)}")
            return None
    
    def get_balance(self) -> Optional[Dict[str, float]]:
        """
        Get account balance for USDT and BTC
        
        Returns:
            Dictionary with 'USDT' and 'BTC' balance, or None if failed
        """
        if not self.is_connected():
            self.logger.error("Cannot get balance - exchange not connected")
            return None
        
        if not self.exchange:
            self.logger.error("Cannot get balance - exchange not initialized")
            return None
        
        try:
            # Fetch account balance
            balance_data = self.exchange.fetch_balance()
            
            # Extract free balance for USDT and BTC, default to 0 if not found
            usdt_balance = balance_data.get('USDT', {}).get('free', 0) or 0
            btc_balance = balance_data.get('BTC', {}).get('free', 0) or 0
            
            # Convert to float to ensure consistent type
            usdt_balance = float(usdt_balance)
            btc_balance = float(btc_balance)
            
            # Create result dictionary
            balances = {
                'USDT': usdt_balance,
                'BTC': btc_balance
            }
            
            # Log with formatted numbers
            self.logger.info(f"Account Balance - USDT: {usdt_balance:,.2f}, BTC: {btc_balance:.8f}")
            
            return balances
            
        except Exception as e:
            self.logger.error(f"Failed to get account balance: {str(e)}")
            return None
    
    def place_market_buy(self, symbol: str, amount: float) -> Optional[Dict[str, Any]]:
        """
        Place a market buy order
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            amount: Amount of base currency to buy
            
        Returns:
            Order object on success, None on failure
        """
        if not self.is_connected():
            self.logger.error("Cannot place buy order - exchange not connected")
            return None
        
        if not self.exchange:
            self.logger.error("Cannot place buy order - exchange not initialized")
            return None
        
        try:
            # Create market buy order
            order = self.exchange.create_market_buy_order(symbol, amount)
            
            # Log successful buy order
            self.logger.info(f"✅ BUY ORDER PLACED: {amount} {symbol.split('/')[0]} at market price")
            self.logger.info(f"Order ID: {order.get('id', 'N/A')}")
            
            return order
            
        except Exception as e:
            self.logger.error(f"❌ FAILED TO PLACE BUY ORDER: {symbol} amount {amount} - {str(e)}")
            return None
    
    def place_market_sell(self, symbol: str, amount: float) -> Optional[Dict[str, Any]]:
        """
        Place a market sell order
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USDT')
            amount: Amount of base currency to sell
            
        Returns:
            Order object on success, None on failure
        """
        if not self.is_connected():
            self.logger.error("Cannot place sell order - exchange not connected")
            return None
        
        if not self.exchange:
            self.logger.error("Cannot place sell order - exchange not initialized")
            return None
        
        try:
            # Create market sell order
            order = self.exchange.create_market_sell_order(symbol, amount)
            
            # Log successful sell order
            self.logger.info(f"✅ SELL ORDER PLACED: {amount} {symbol.split('/')[0]} at market price")
            self.logger.info(f"Order ID: {order.get('id', 'N/A')}")
            
            return order
            
        except Exception as e:
            self.logger.error(f"❌ FAILED TO PLACE SELL ORDER: {symbol} amount {amount} - {str(e)}")
            return None
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
            # Initialize ccxt Binance exchange instance
            self.exchange = ccxt.binance()
            self.exchange.apiKey = api_key
            self.exchange.secret = secret
            self.exchange.sandbox = True  # Enable testnet/sandbox mode
            self.exchange.rateLimit = True  # Enable built-in rate limiting
            self.exchange.enableRateLimit = True  # Additional rate limit protection
            
            # Set testnet URLs - correct format for Binance testnet
            self.exchange.urls['api'] = {
                'public': 'https://testnet.binance.vision/api/v3',
                'private': 'https://testnet.binance.vision/api/v3',
            }
            
            # Configure for spot trading
            self.exchange.options['defaultType'] = 'spot'
            
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
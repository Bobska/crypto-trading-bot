"""
Main entry point for the Crypto Trading Bot
Initializes all components and starts the trading bot
"""
import config
from exchange import BinanceTestnet
from strategy import GridTradingStrategy
from ai_advisor import AIAdvisor
from bot import TradingBot
from logger_setup import setup_logger
from banner import print_banner

def main():
    """
    Initialize and run the trading bot
    
    Sets up all components, verifies exchange connection,
    and starts the main trading loop.
    """
    try:
        # Display startup banner
        print_banner()
        
        # Setup logger
        logger = setup_logger('Main')
        logger.info("Initializing Crypto Trading Bot...")
        
        # Create exchange instance
        logger.info("Connecting to Binance Testnet...")
        exchange = BinanceTestnet(config.BINANCE_API_KEY, config.BINANCE_SECRET)
        
        # Verify connection by getting balance
        balance = exchange.get_balance()
        
        if balance is None:
            logger.error("Failed to connect to exchange - could not retrieve balance")
            print("❌ Connection failed: Unable to retrieve account balance")
            print("   Please check your API keys and network connection")
            return
        
        # Display starting balance
        print("\n💰 Starting Balance:")
        print(f"   USDT: ${balance.get('USDT', 0.0):,.2f}")
        print(f"   BTC:  {balance.get('BTC', 0.0):.6f}")
        print()
        
        # TODO: Create strategy and AI advisor instances
        # TODO: Create trading bot instance
        # TODO: Start bot
        
        logger.info("Initialization complete")
        
    except Exception as e:
        logger = setup_logger('Main')
        logger.error(f"Fatal error during initialization: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        print(f"\n❌ Fatal error: {str(e)}")
        print("   Check logs for details")

if __name__ == "__main__":
    main()

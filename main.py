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
        
        # Initialize trading strategy
        logger.info("Initializing trading strategy...")
        strategy = GridTradingStrategy(
            buy_threshold=config.BUY_THRESHOLD,
            sell_threshold=config.SELL_THRESHOLD,
            trade_amount=config.TRADE_AMOUNT
        )
        
        # Display strategy settings
        print("📊 Strategy Settings:")
        print(f"   Symbol: {config.SYMBOL}")
        print(f"   Buy Threshold: {config.BUY_THRESHOLD}%")
        print(f"   Sell Threshold: {config.SELL_THRESHOLD}%")
        print(f"   Trade Amount: {config.TRADE_AMOUNT} BTC")
        print()
        
        # Initialize AI advisor
        if config.AI_ENABLED:
            logger.info("Initializing AI Advisor...")
            ai_advisor = AIAdvisor(api_url=config.AI_API_URL)
        else:
            logger.info("AI Advisor is disabled")
            print("⚠️  AI Advisor: DISABLED")
            print()
            ai_advisor = AIAdvisor(api_url="")
        
        # Create trading bot
        logger.info("Creating trading bot instance...")
        trading_bot = TradingBot(
            exchange=exchange,
            strategy=strategy,
            ai_advisor=ai_advisor,
            symbol=config.SYMBOL,
            check_interval=config.CHECK_INTERVAL
        )
        
        logger.info("Initialization complete")
        logger.info("Starting trading bot...")
        
        # Start the bot
        trading_bot.run()
        
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user (Ctrl+C)")
        print("\n👋 Goodbye!")
        
    except Exception as e:
        logger = setup_logger('Main')
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        print(f"\n❌ Fatal error: {str(e)}")
        print("   Check logs for details")

if __name__ == "__main__":
    main()

"""
Test script for BinanceTestnet exchange operations
Tests read-only operations: price fetching and balance checking
"""
import config
from exchange import BinanceTestnet

def main():
    """Test exchange connection and read operations"""
    try:
        print("Initializing Binance Testnet connection...")
        
        # Create exchange instance
        exchange = BinanceTestnet(config.BINANCE_API_KEY, config.BINANCE_SECRET)
        
        if not exchange.is_connected():
            print("❌ Failed to connect to Binance Testnet")
            return
        
        print("✅ Connected to Binance Testnet")
        
        # Test price fetching
        print("\nFetching current price...")
        btc_price = exchange.get_current_price('BTC/USDT')
        
        if btc_price:
            print(f"BTC/USDT current price: ${btc_price:,.2f}")
        else:
            print("❌ Failed to fetch BTC/USDT price")
        
        # Test balance fetching
        print("\nFetching account balance...")
        balance = exchange.get_balance()
        
        if balance:
            usdt_balance = balance['USDT']
            btc_balance = balance['BTC']
            print(f"Balance - USDT: ${usdt_balance:,.2f}, BTC: {btc_balance:.6f}")
        else:
            print("❌ Failed to fetch account balance")
        
        print("\n📊 Exchange test completed successfully!")
        
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        print("Please check your API keys and internet connection")

if __name__ == "__main__":
    main()
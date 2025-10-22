"""
Test script for GridTradingStrategy
Simulates a complete grid trading cycle with price movements
"""
from strategy import GridTradingStrategy

def main():
    """Simulate grid trading with price sequence"""
    print("=== Grid Trading Strategy Simulation ===")
    
    # Create strategy with 1% thresholds
    strategy = GridTradingStrategy(
        buy_threshold=1.0,
        sell_threshold=1.0,
        trade_amount=0.001
    )
    
    # Price sequence for simulation
    prices = [43000, 42500, 43000, 43500, 43000]
    
    # Start with USDT position (holding cash)
    position = 'USDT'
    
    print(f"\nStarting position: {position}")
    print("Price sequence:", prices)
    print("\n" + "="*60)
    
    # Simulate trading through price sequence
    for i, price in enumerate(prices):
        print(f"\nStep {i+1}: Price = ${price:,.2f}")
        
        # Analyze current price
        signal = strategy.analyze(price, position)
        
        print(f"Signal: {signal}, Position: {position}")
        
        # Execute trades based on signal
        if signal == 'BUY' and position == 'USDT':
            strategy.record_buy(price)
            position = 'BTC'
            print(f"✅ EXECUTED BUY - New position: {position}")
            
        elif signal == 'SELL' and position == 'BTC':
            strategy.record_sell(price)
            position = 'USDT'
            print(f"✅ EXECUTED SELL - New position: {position}")
            
        elif signal == 'HOLD':
            print(f"📊 HOLDING - Current position: {position}")
        
        print("-" * 40)
    
    # Print final statistics
    print("\n" + "="*60)
    print("FINAL TRADING STATISTICS")
    print("="*60)
    
    stats = strategy.get_stats()
    
    print(f"Total Trades: {stats['total_trades']}")
    print(f"Wins: {stats['wins']}")
    print(f"Losses: {stats['losses']}")
    print(f"Win Rate: {stats['win_rate']:.1f}%")
    print(f"Final Position: {position}")
    
    # Show detailed strategy stats
    detailed_stats = strategy.get_strategy_stats()
    print(f"\nLast Buy Price: ${detailed_stats['last_buy_price']:,.2f}" if detailed_stats['last_buy_price'] else "No buy price recorded")
    print(f"Last Sell Price: ${detailed_stats['last_sell_price']:,.2f}" if detailed_stats['last_sell_price'] else "No sell price recorded")
    
    print("\n🎯 Grid Trading Simulation Complete!")

if __name__ == "__main__":
    main()
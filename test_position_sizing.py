"""
Test Dynamic Position Sizing
Simulates consecutive wins and losses to verify position sizing adjustments
"""
from strategy import GridTradingStrategy

def test_position_sizing():
    """Test dynamic position sizing with consecutive wins/losses"""
    
    print("=" * 70)
    print("TESTING DYNAMIC POSITION SIZING")
    print("=" * 70)
    
    # Create strategy with 0.001 BTC base trade amount
    strategy = GridTradingStrategy(
        buy_threshold=1.0,
        sell_threshold=1.0,
        trade_amount=0.001
    )
    
    print(f"\n📊 Initial Settings:")
    print(f"   Base Trade Amount: {strategy.base_trade_amount:.6f} BTC")
    print(f"   Current Trade Amount: {strategy.trade_amount:.6f} BTC")
    print(f"   Min Position Size: {strategy.min_position_size:.6f} BTC")
    print(f"   Max Position Size: {strategy.max_position_size:.6f} BTC")
    
    # Mock balance
    mock_balance = {'USDT': 10000.0, 'BTC': 0.0}
    
    # Test consecutive wins
    print("\n" + "=" * 70)
    print("TEST 1: CONSECUTIVE WINS")
    print("=" * 70)
    
    buy_price = 100000.0
    for i in range(5):
        sell_price = buy_price * 1.02  # 2% profit
        strategy.last_buy_price = buy_price
        strategy.record_sell(sell_price)
        
        stats = strategy.get_stats()
        print(f"\nTrade {i+1}:")
        print(f"  Consecutive Wins: {strategy.consecutive_wins}")
        print(f"  Trade Amount: {strategy.trade_amount:.6f} BTC")
        
        if i >= 2:  # After 3rd win
            strategy.adjust_position_size(mock_balance, stats['win_rate'])
    
    print(f"\n✅ After 5 wins - Final trade amount: {strategy.trade_amount:.6f} BTC")
    
    # Reset for loss test
    strategy.consecutive_wins = 0
    strategy.consecutive_losses = 0
    
    # Test consecutive losses
    print("\n" + "=" * 70)
    print("TEST 2: CONSECUTIVE LOSSES")
    print("=" * 70)
    
    for i in range(5):
        sell_price = buy_price * 0.98  # 2% loss
        strategy.last_buy_price = buy_price
        strategy.record_sell(sell_price)
        
        stats = strategy.get_stats()
        print(f"\nTrade {i+1}:")
        print(f"  Consecutive Losses: {strategy.consecutive_losses}")
        print(f"  Trade Amount: {strategy.trade_amount:.6f} BTC")
        
        if i >= 2:  # After 3rd loss
            strategy.adjust_position_size(mock_balance, stats['win_rate'])
    
    print(f"\n❌ After 5 losses - Final trade amount: {strategy.trade_amount:.6f} BTC")
    
    # Test limits
    print("\n" + "=" * 70)
    print("TEST 3: POSITION SIZE LIMITS")
    print("=" * 70)
    
    # Reset and force to max
    strategy.trade_amount = strategy.max_position_size * 0.9
    strategy.consecutive_wins = 5
    print(f"\nBefore: {strategy.trade_amount:.6f} BTC")
    strategy.adjust_position_size(mock_balance, 80.0)
    print(f"After increase: {strategy.trade_amount:.6f} BTC")
    print(f"Max limit: {strategy.max_position_size:.6f} BTC")
    
    # Force to min
    strategy.trade_amount = strategy.min_position_size * 1.1
    strategy.consecutive_wins = 0
    strategy.consecutive_losses = 5
    print(f"\nBefore: {strategy.trade_amount:.6f} BTC")
    strategy.adjust_position_size(mock_balance, 20.0)
    print(f"After decrease: {strategy.trade_amount:.6f} BTC")
    print(f"Min limit: {strategy.min_position_size:.6f} BTC")
    
    # Final stats
    print("\n" + "=" * 70)
    print("FINAL STATISTICS")
    print("=" * 70)
    final_stats = strategy.get_stats()
    print(f"Total Trades: {final_stats['total_trades']}")
    print(f"Wins: {final_stats['wins']}")
    print(f"Losses: {final_stats['losses']}")
    print(f"Win Rate: {final_stats['win_rate']:.1f}%")
    print("=" * 70)

if __name__ == "__main__":
    test_position_sizing()

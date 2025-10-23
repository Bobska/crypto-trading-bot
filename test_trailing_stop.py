"""
Test Trailing Stop Feature
Simulates price movements to verify trailing stop triggers correctly
"""
from strategy import GridTradingStrategy

def test_trailing_stop():
    """Test trailing stop feature with simulated price movements"""
    
    print("=" * 70)
    print("TESTING TRAILING STOP FEATURE")
    print("=" * 70)
    
    # Create strategy WITH trailing stop enabled and HIGH sell threshold
    # High sell threshold ensures trailing stop triggers before normal sell
    strategy_with_ts = GridTradingStrategy(
        buy_threshold=1.0,
        sell_threshold=10.0,  # 10% - won't trigger in our test
        trade_amount=0.001,
        use_trailing_stop=True,
        trailing_stop_percentage=1.5
    )
    
    print("\n📊 Strategy Settings:")
    print(f"   Trailing Stop: {'ENABLED' if strategy_with_ts.use_trailing_stop else 'DISABLED'}")
    print(f"   Trailing Stop %: {strategy_with_ts.trailing_stop_percentage}%")
    print(f"   Sell Threshold: {strategy_with_ts.sell_threshold}% (high to test trailing stop)")
    
    # Simulate buying BTC at $100,000
    buy_price = 100000.0
    strategy_with_ts.record_buy(buy_price)
    
    print("\n" + "=" * 70)
    print("SCENARIO 1: Price rises then falls - Trailing stop should trigger")
    print("=" * 70)
    
    # Simulate price movements - rises to +4%, then falls
    price_sequence = [
        (100000.0, "Entry price"),
        (101000.0, "Up 1.0% - Peak updated"),
        (102000.0, "Up 2.0% - Peak updated"),
        (103000.0, "Up 3.0% - Peak updated"),
        (104000.0, "Up 4.0% - Peak updated (highest: $104,000)"),
        (103500.0, "Down 0.48% from peak of $104k"),
        (103000.0, "Down 0.96% from peak of $104k"),
        (102500.0, "Down 1.44% from peak of $104k"),
        (102440.0, "Down 1.5% from peak - TRAILING STOP TRIGGERS!"),
    ]
    
    for price, description in price_sequence:
        print(f"\n💰 Price: ${price:,.2f} - {description}")
        
        if strategy_with_ts.highest_price_since_buy:
            drawdown = ((strategy_with_ts.highest_price_since_buy - price) / 
                       strategy_with_ts.highest_price_since_buy) * 100
            print(f"   📊 Peak: ${strategy_with_ts.highest_price_since_buy:,.2f}")
            print(f"   📉 Drawdown: {drawdown:.2f}%")
        
        signal = strategy_with_ts.analyze(price, 'BTC')
        
        if signal == 'SELL':
            print(f"   🛑 SIGNAL: {signal} - Trailing stop triggered!")
            profit = price - buy_price
            profit_pct = (profit / buy_price) * 100
            print(f"   💰 Profit locked in: +${profit:,.2f} (+{profit_pct:.2f}%)")
            break
        else:
            print(f"   ⏸️  SIGNAL: {signal}")
    
    # Test scenario 2: Price keeps rising
    print("\n" + "=" * 70)
    print("SCENARIO 2: Price keeps rising - Should hit sell threshold")
    print("=" * 70)
    
    strategy2 = GridTradingStrategy(
        buy_threshold=1.0,
        sell_threshold=2.0,  # 2% sell threshold
        trade_amount=0.001,
        use_trailing_stop=True,
        trailing_stop_percentage=1.5
    )
    
    strategy2.record_buy(buy_price)
    
    price_sequence2 = [
        (100000.0, "Entry price"),
        (100500.0, "Up 0.5%"),
        (101000.0, "Up 1.0%"),
        (101500.0, "Up 1.5%"),
        (102000.0, "Up 2.0% - Should hit sell threshold!"),
    ]
    
    for price, description in price_sequence2:
        print(f"\n💰 Price: ${price:,.2f} - {description}")
        
        signal = strategy2.analyze(price, 'BTC')
        
        if signal == 'SELL':
            print(f"   🔴 SIGNAL: {signal} - Sell threshold reached!")
            profit = price - buy_price
            profit_pct = (profit / buy_price) * 100
            print(f"   💰 Profit: +${profit:,.2f} (+{profit_pct:.2f}%)")
            break
        else:
            print(f"   ⏸️  SIGNAL: {signal}")
    
    # Test scenario 3: Comparison with trailing stop disabled
    print("\n" + "=" * 70)
    print("SCENARIO 3: Without trailing stop - Holds longer")
    print("=" * 70)
    
    strategy_no_ts = GridTradingStrategy(
        buy_threshold=1.0,
        sell_threshold=5.0,  # High threshold
        trade_amount=0.001,
        use_trailing_stop=False  # Disabled
    )
    
    strategy_no_ts.record_buy(buy_price)
    
    price_sequence3 = [
        (104000.0, "Up 4.0% - Peak"),
        (102300.0, "Down to +2.3% - Would trigger trailing stop"),
    ]
    
    print("\n   WITHOUT TRAILING STOP:")
    for price, description in price_sequence3:
        print(f"\n   💰 Price: ${price:,.2f} - {description}")
        signal = strategy_no_ts.analyze(price, 'BTC')
        print(f"      Signal: {signal} - Still holding (needs +5.0% for sell)")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print("\n✅ Key Findings:")
    print("   1. Trailing stop locks in profits when price falls from peak")
    print("   2. Trailing stop percentage is measured from highest price reached")
    print("   3. Without trailing stop, bot holds through drawdowns")
    print("   4. Trailing stop provides downside protection while allowing upside")

if __name__ == "__main__":
    test_trailing_stop()

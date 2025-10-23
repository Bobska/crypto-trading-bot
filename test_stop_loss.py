"""
Test stop-loss functionality
"""
from strategy import GridTradingStrategy

print("=" * 60)
print("Testing Stop-Loss Functionality")
print("=" * 60)
print()

# Create strategy with 3% stop-loss
strategy = GridTradingStrategy(
    buy_threshold=1.0,
    sell_threshold=1.0,
    trade_amount=0.001,
    stop_loss_percentage=3.0
)

print(f"Strategy initialized with {strategy.stop_loss_percentage}% stop-loss")
print()

# Simulate a buy at $100,000
buy_price = 100000.0
strategy.record_buy(buy_price)
print(f"Simulated BUY at ${buy_price:,.2f}")
print()

# Test scenarios
test_prices = [
    (99000.0, "1% loss - should NOT trigger"),
    (98000.0, "2% loss - should NOT trigger"),
    (97500.0, "2.5% loss - should NOT trigger"),
    (96900.0, "3.1% loss - SHOULD TRIGGER"),
    (95000.0, "5% loss - SHOULD TRIGGER"),
]

print("Testing stop-loss at various price levels:")
print("-" * 60)

for price, description in test_prices:
    triggered = strategy.check_stop_loss(price, 'BTC')
    loss_pct = ((buy_price - price) / buy_price) * 100
    status = "✓ TRIGGERED" if triggered else "✗ Not triggered"
    print(f"${price:,.2f} ({loss_pct:.1f}%): {status} - {description}")

print()
print("=" * 60)
print("Stop-loss test completed!")
print("=" * 60)

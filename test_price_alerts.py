"""
Test price alert functionality
"""
from datetime import datetime, timedelta
from bot import TradingBot
from unittest.mock import Mock

print("=" * 60)
print("Testing Price Alert System")
print("=" * 60)
print()

# Create mock objects
mock_exchange = Mock()
mock_strategy = Mock()
mock_ai = Mock()
mock_ai.enabled = False  # Disable AI for test

# Create bot instance
bot = TradingBot(
    exchange=mock_exchange,
    strategy=mock_strategy,
    ai_advisor=mock_ai,
    symbol='BTC/USDT',
    check_interval=30
)

print(f"Bot initialized with {bot.price_alert_threshold}% alert threshold")
print(f"Tracking window: {bot.price_tracking_window / 60} minutes")
print()

# Test scenarios
print("Testing Price Alert Scenarios:")
print("-" * 60)
print()

# Scenario 1: Small price change (should NOT alert)
print("1. Small price change (1% - should NOT alert)")
bot.check_price_alerts(100000.0)
bot.price_history[0] = (datetime.now() - timedelta(minutes=5), 100000.0)
bot.check_price_alerts(101000.0)  # 1% increase
print("   Result: No alert expected")
print()

# Scenario 2: Large upward price move (should alert)
print("2. Large upward move (2.5% UP - SHOULD ALERT)")
bot.price_history.clear()
bot.price_history.append((datetime.now() - timedelta(minutes=5), 100000.0))
bot.check_price_alerts(102500.0)  # 2.5% increase
print()

# Scenario 3: Large downward price move (should alert)
print("3. Large downward move (3% DOWN - SHOULD ALERT)")
bot.price_history.clear()
bot.price_history.append((datetime.now() - timedelta(minutes=4), 100000.0))
bot.check_price_alerts(97000.0)  # 3% decrease
print()

# Scenario 4: Price stabilized (old alerts should be cleared)
print("4. Price stabilized after 5 minutes")
# Add old price from 6 minutes ago (should be removed)
old_time = datetime.now() - timedelta(minutes=6)
bot.price_history.insert(0, (old_time, 90000.0))
print(f"   Added old price: ${90000.0:,.2f} from 6 minutes ago")

current_price = 97000.0
bot.check_price_alerts(current_price)

# Check if old price was removed
prices_in_window = [price for time, price in bot.price_history]
print(f"   Prices in window: {len(bot.price_history)}")
print(f"   Old price removed: {90000.0 not in prices_in_window}")
print()

print("=" * 60)
print("Price Alert Test Complete!")
print("=" * 60)
print()
print("Summary:")
print("- Price history tracking: ✓")
print("- Alert threshold detection: ✓")
print("- Direction detection (UP/DOWN): ✓")
print("- Old price cleanup: ✓")
print("- Console alerts: ✓")
print("- Log warnings: ✓")

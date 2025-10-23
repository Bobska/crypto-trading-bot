"""
Test technical indicators module
"""
from indicators import calculate_sma, calculate_rsi, is_trending, get_market_condition, calculate_volatility

print("=" * 60)
print("Testing Technical Indicators")
print("=" * 60)
print()

# Test data: simulated ranging market
ranging_prices = [
    100, 102, 101, 99, 100, 103, 101, 98, 100, 102,
    101, 99, 100, 103, 102, 100, 99, 101, 100, 102,
    101, 100, 99, 101, 102, 100, 99, 101, 100, 102,
    101, 100, 99, 102, 101, 100, 99, 101, 103, 100,
    99, 101, 102, 100, 99, 101, 100, 102, 101, 100,
    99, 101, 100, 102, 101, 100, 99, 101, 100, 102
]

# Test data: simulated trending market (uptrend)
trending_prices = [
    100, 101, 102, 103, 104, 105, 106, 107, 108, 109,
    110, 111, 112, 113, 114, 115, 116, 117, 118, 119,
    120, 121, 122, 123, 124, 125, 126, 127, 128, 129,
    130, 131, 132, 133, 134, 135, 136, 137, 138, 139,
    140, 141, 142, 143, 144, 145, 146, 147, 148, 149,
    150, 151, 152, 153, 154, 155, 156, 157, 158, 159
]

print("1. Testing SMA Calculation")
print("-" * 60)
sma_20 = calculate_sma(ranging_prices, 20)
sma_50 = calculate_sma(ranging_prices, 50)
print(f"SMA(20): {sma_20:.2f}" if sma_20 else "SMA(20): Not enough data")
print(f"SMA(50): {sma_50:.2f}" if sma_50 else "SMA(50): Not enough data")
print()

print("2. Testing RSI Calculation")
print("-" * 60)
rsi = calculate_rsi(ranging_prices)
print(f"RSI(14): {rsi:.2f}" if rsi else "RSI: Not enough data")
if rsi:
    if rsi > 70:
        print("  Status: OVERBOUGHT (>70)")
    elif rsi < 30:
        print("  Status: OVERSOLD (<30)")
    else:
        print("  Status: NEUTRAL (30-70)")
print()

print("3. Testing Market Condition Detection")
print("-" * 60)

# Test ranging market
is_trending_ranging = is_trending(ranging_prices)
condition_ranging = get_market_condition(ranging_prices)
print(f"Ranging Market Test:")
print(f"  is_trending(): {is_trending_ranging}")
print(f"  Condition: {condition_ranging}")
print(f"  Expected: RANGING")
print(f"  Result: {'✓ PASS' if condition_ranging == 'RANGING' else '✗ FAIL'}")
print()

# Test trending market
is_trending_trend = is_trending(trending_prices)
condition_trending = get_market_condition(trending_prices)
print(f"Trending Market Test:")
print(f"  is_trending(): {is_trending_trend}")
print(f"  Condition: {condition_trending}")
print(f"  Expected: TRENDING")
print(f"  Result: {'✓ PASS' if condition_trending == 'TRENDING' else '✗ FAIL'}")
print()

print("4. Testing Volatility Calculation")
print("-" * 60)
vol_ranging = calculate_volatility(ranging_prices, 20)
vol_trending = calculate_volatility(trending_prices, 20)
print(f"Ranging Market Volatility: {vol_ranging:.2f}%" if vol_ranging else "Not enough data")
print(f"Trending Market Volatility: {vol_trending:.2f}%" if vol_trending else "Not enough data")
print()

print("=" * 60)
print("Technical Indicators Test Complete!")
print("=" * 60)

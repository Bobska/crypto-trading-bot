# Trading Profiles

This directory contains pre-configured trading profiles for different risk appetites and market conditions.

## Available Profiles

### 🛡️ Conservative (`conservative.env`)
**Best for:** Volatile markets, risk-averse traders, learning phase

- **Grid Width:** 2.0% (wider grids = fewer trades)
- **Position Size:** 0.0005 BTC (smaller positions = lower risk)
- **Check Interval:** 60 seconds
- **AI Confirmation:** Required (human-in-loop)
- **Use Case:** Capital preservation, high volatility, testing strategies

### ⚖️ Balanced (`balanced.env`)
**Best for:** Normal market conditions, experienced traders, default settings

- **Grid Width:** 1.0% (moderate grids = balanced trading frequency)
- **Position Size:** 0.001 BTC (moderate positions = balanced risk/reward)
- **Check Interval:** 30 seconds
- **AI Confirmation:** Optional
- **Use Case:** General purpose, proven strategies, stable markets

### 🚀 Aggressive (`aggressive.env`)
**Best for:** Stable markets, risk-tolerant traders, experienced users

- **Grid Width:** 0.5% (tight grids = frequent trades)
- **Position Size:** 0.002 BTC (larger positions = higher risk/reward)
- **Check Interval:** 15 seconds
- **AI Confirmation:** Optional
- **Use Case:** High-frequency trading, strong trends, maximize profits

## Usage

### Command Line
```bash
# Use conservative profile
python main.py --profile conservative

# Use balanced profile (default)
python main.py --profile balanced

# Use aggressive profile
python main.py --profile aggressive
```

### Multi-Bot System
```bash
# Run multi-bot with specific profile
python multi_bot.py --profile aggressive
```

## Profile Comparison

| Parameter | Conservative | Balanced | Aggressive |
|-----------|-------------|----------|------------|
| Buy Threshold | 2.0% | 1.0% | 0.5% |
| Sell Threshold | 2.0% | 1.0% | 0.5% |
| Trade Amount | 0.0005 BTC | 0.001 BTC | 0.002 BTC |
| Min Position | 0.0003 BTC | 0.0005 BTC | 0.001 BTC |
| Max Position | 0.001 BTC | 0.002 BTC | 0.004 BTC |
| Check Interval | 60s | 30s | 15s |
| Trailing Stop | 1.5% | 1.5% | 1.0% |
| AI Confirm | Required | Optional | Optional |

## Creating Custom Profiles

1. Copy an existing profile:
   ```bash
   cp profiles/balanced.env profiles/custom.env
   ```

2. Edit the parameters in `custom.env`

3. Update `config.py` to include your profile in the choices:
   ```python
   choices=['conservative', 'balanced', 'aggressive', 'custom']
   ```

4. Run with your custom profile:
   ```bash
   python main.py --profile custom
   ```

## Profile Parameters Explained

### Trading Parameters
- **BUY_THRESHOLD:** % price must drop before buying (lower = more frequent buys)
- **SELL_THRESHOLD:** % price must rise before selling (lower = quicker profits)
- **TRADE_AMOUNT:** Base amount of BTC per trade

### Risk Management
- **STOP_LOSS_PERCENTAGE:** Maximum acceptable loss per trade
- **USE_TRAILING_STOP:** Follow price up, sell on pullback
- **TRAILING_STOP_PERCENTAGE:** Pullback % to trigger sell

### Position Sizing
- **MIN_POSITION_SIZE:** Minimum trade size (after losses)
- **MAX_POSITION_SIZE:** Maximum trade size (after wins)
- **BASE_POSITION_SIZE:** Starting trade size

### Execution
- **CHECK_INTERVAL:** Seconds between price checks (lower = more responsive)

## Best Practices

1. **Start Conservative:** Begin with conservative profile to learn
2. **Test First:** Run on testnet before switching to aggressive
3. **Monitor Performance:** Use `python analytics.py` to evaluate profile effectiveness
4. **Match Market Conditions:** Switch profiles based on volatility
5. **Log Analysis:** Check logs to verify profile is active

## Profile Selection Tips

### Use Conservative When:
- Market is highly volatile
- You're new to algorithmic trading
- Testing new strategies
- Capital preservation is priority
- Unsure about current market conditions

### Use Balanced When:
- Market conditions are normal
- You have trading experience
- Want general-purpose settings
- Following proven strategies

### Use Aggressive When:
- Market is stable with clear trends
- You're experienced with risks
- Want to maximize profit opportunities
- Have analyzed market extensively
- Can monitor bot frequently

## Troubleshooting

**Profile not loading:**
```bash
# Check if profile file exists
ls profiles/

# Verify profile name spelling
python main.py --profile balanced  # correct
python main.py --profile ballanced  # incorrect
```

**Wrong settings active:**
```bash
# Check which profile is loaded in logs
grep "Active Profile" logs/trades_*.log

# Verify .env file is being read
python -c "import config; print(config.ACTIVE_PROFILE)"
```

**Profile not in logs:**
- Check that main.py logs the profile on startup
- Verify config.ACTIVE_PROFILE is set correctly
- Restart the bot after changing profiles

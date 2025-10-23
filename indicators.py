"""
Technical Indicators Module

Provides technical analysis functions for trading strategy enhancement.
Includes moving averages, momentum indicators, and trend detection.
"""
import pandas as pd
import numpy as np
from typing import List, Optional

def calculate_sma(prices: List[float], period: int) -> Optional[float]:
    """
    Calculate Simple Moving Average
    
    Args:
        prices: List of historical prices (oldest to newest)
        period: Number of periods for the average
        
    Returns:
        SMA value or None if insufficient data
    """
    if len(prices) < period:
        return None
    
    # Use pandas for efficient calculation
    series = pd.Series(prices)
    sma = series.rolling(window=period).mean().iloc[-1]
    
    return float(sma) if not pd.isna(sma) else None

def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
    """
    Calculate Relative Strength Index
    
    The RSI measures the magnitude of recent price changes to evaluate
    overbought or oversold conditions. Values range from 0 to 100:
    - RSI > 70: Overbought (potential sell signal)
    - RSI < 30: Oversold (potential buy signal)
    
    Args:
        prices: List of historical prices (oldest to newest)
        period: RSI calculation period (default: 14)
        
    Returns:
        RSI value (0-100) or None if insufficient data
    """
    if len(prices) < period + 1:
        return None
    
    # Convert to pandas Series
    series = pd.Series(prices)
    
    # Calculate price changes
    delta = series.diff()
    
    # Separate gains and losses
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    
    # Calculate average gain and loss using Wilder's smoothing
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    
    # Calculate RS (Relative Strength)
    rs = avg_gain / avg_loss
    
    # Calculate RSI
    rsi = 100.0 - (100.0 / (1.0 + rs))
    
    # Return the most recent RSI value
    rsi_value = rsi.iloc[-1]
    
    return float(rsi_value) if not pd.isna(rsi_value) else None

def is_trending(prices: List[float], sma_short: int = 20, sma_long: int = 50, threshold: float = 0.02) -> bool:
    """
    Determine if market is trending or ranging
    
    Uses multiple indicators to identify market conditions:
    - Compares short-term vs long-term moving averages
    - Checks for consistent directional movement
    - Analyzes price volatility patterns
    
    Trending Market:
    - Clear directional bias (up or down)
    - Short MA significantly above/below long MA
    - Grid trading performs poorly
    
    Ranging Market:
    - Price oscillates within a range
    - Moving averages converge
    - Grid trading performs well
    
    Args:
        prices: List of historical prices (oldest to newest)
        sma_short: Short-term MA period (default: 20)
        sma_long: Long-term MA period (default: 50)
        threshold: Percentage difference threshold (default: 2%)
        
    Returns:
        True if trending, False if ranging
    """
    # Need sufficient data for both MAs
    if len(prices) < sma_long:
        # Not enough data - assume ranging (safe default for grid trading)
        return False
    
    # Calculate moving averages
    short_ma = calculate_sma(prices, sma_short)
    long_ma = calculate_sma(prices, sma_long)
    
    if short_ma is None or long_ma is None:
        return False
    
    # Calculate percentage difference between MAs
    ma_diff_percent = abs(short_ma - long_ma) / long_ma
    
    # If MAs are significantly separated, market is trending
    if ma_diff_percent > threshold:
        return True
    
    # Additional check: measure price consistency
    # Calculate how many times price crosses the long MA
    series = pd.Series(prices[-sma_long:])
    crosses = 0
    
    for i in range(1, len(series)):
        if (series.iloc[i-1] < long_ma and series.iloc[i] > long_ma) or \
           (series.iloc[i-1] > long_ma and series.iloc[i] < long_ma):
            crosses += 1
    
    # Many crosses = ranging market, few crosses = trending market
    # Threshold: more than 4 crosses in the period = ranging
    if crosses >= 4:
        return False  # Ranging
    
    # Check recent price momentum
    recent_prices = prices[-10:]  # Last 10 prices
    if len(recent_prices) >= 10:
        series_recent = pd.Series(recent_prices)
        
        # Calculate linear regression slope
        x = np.arange(len(series_recent))
        coefficients = np.polyfit(x, series_recent, 1)
        slope = coefficients[0]
        
        # Normalize slope by price level
        normalized_slope = abs(slope / series_recent.mean())
        
        # Strong slope = trending, weak slope = ranging
        if normalized_slope > 0.001:  # 0.1% per period
            return True
    
    # Default to ranging market
    return False

def get_market_condition(prices: List[float]) -> str:
    """
    Get human-readable market condition
    
    Args:
        prices: List of historical prices
        
    Returns:
        'TRENDING' or 'RANGING'
    """
    return 'TRENDING' if is_trending(prices) else 'RANGING'

def calculate_volatility(prices: List[float], period: int = 20) -> Optional[float]:
    """
    Calculate price volatility (standard deviation)
    
    Args:
        prices: List of historical prices
        period: Number of periods for calculation
        
    Returns:
        Volatility as percentage or None if insufficient data
    """
    if len(prices) < period:
        return None
    
    series = pd.Series(prices[-period:])
    std_dev = series.std()
    mean_price = series.mean()
    
    # Return as percentage of mean price
    volatility_pct = (std_dev / mean_price) * 100
    
    return float(volatility_pct)

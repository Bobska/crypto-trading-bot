"""
Backtesting Utility for Grid Trading Strategy

Downloads historical price data and simulates the grid trading strategy
to evaluate performance and optimize parameters before live trading.

Features:
- Downloads 7 days of hourly BTC/USDT data
- Simulates trades using actual GridTradingStrategy
- Tracks P&L and statistics
- Tests multiple threshold settings
- Helps find optimal parameters

Usage: python backtest.py
"""
import ccxt
from datetime import datetime, timedelta
from strategy import GridTradingStrategy
from typing import List, Dict, Tuple
import time

class Backtester:
    """
    Backtesting engine for grid trading strategy
    """
    
    def __init__(self, symbol: str = 'BTC/USDT', days: int = 7):
        """
        Initialize backtester
        
        Args:
            symbol: Trading pair to backtest
            days: Number of days of historical data
        """
        self.symbol = symbol
        self.days = days
        self.exchange = ccxt.binance()
        
    def fetch_historical_data(self) -> List[Tuple[datetime, float]]:
        """
        Fetch historical OHLCV data from exchange
        
        Returns:
            List of (timestamp, close_price) tuples
        """
        print(f"Fetching {self.days} days of hourly data for {self.symbol}...")
        
        # Calculate timestamp for N days ago
        since = int((datetime.now() - timedelta(days=self.days)).timestamp() * 1000)
        
        # Fetch OHLCV data (timestamp, open, high, low, close, volume)
        ohlcv = self.exchange.fetch_ohlcv(
            self.symbol,
            timeframe='1h',
            since=since,
            limit=self.days * 24
        )
        
        # Convert to (datetime, close_price) format
        price_data = [
            (datetime.fromtimestamp(candle[0] / 1000), candle[4])
            for candle in ohlcv
        ]
        
        print(f"✓ Fetched {len(price_data)} hourly candles")
        print(f"  Date range: {price_data[0][0].strftime('%Y-%m-%d %H:%M')} to {price_data[-1][0].strftime('%Y-%m-%d %H:%M')}")
        print(f"  Price range: ${min(p[1] for p in price_data):,.2f} to ${max(p[1] for p in price_data):,.2f}")
        print()
        
        return price_data
    
    def run_backtest(
        self, 
        price_data: List[Tuple[datetime, float]], 
        buy_threshold: float, 
        sell_threshold: float,
        trade_amount: float = 0.001,
        starting_balance: float = 10000.0
    ) -> Dict:
        """
        Run backtest simulation with given parameters
        
        Args:
            price_data: List of (timestamp, price) tuples
            buy_threshold: Buy threshold percentage
            sell_threshold: Sell threshold percentage
            trade_amount: BTC amount per trade
            starting_balance: Starting USDT balance
            
        Returns:
            Dictionary with backtest results
        """
        # Initialize strategy
        strategy = GridTradingStrategy(
            buy_threshold=buy_threshold,
            sell_threshold=sell_threshold,
            trade_amount=trade_amount
        )
        
        # Initialize state
        position = 'USDT'
        balance_usdt = starting_balance
        balance_btc = 0.0
        
        trades = []
        
        # Simulate trading through historical data
        for timestamp, price in price_data:
            # Get trading signal
            signal = strategy.analyze(price, position)
            
            # Execute simulated trades
            if signal == 'BUY' and position == 'USDT':
                # Calculate cost
                cost = price * trade_amount
                
                if balance_usdt >= cost:
                    # Execute buy
                    balance_usdt -= cost
                    balance_btc += trade_amount
                    position = 'BTC'
                    strategy.record_buy(price)
                    
                    trades.append({
                        'timestamp': timestamp,
                        'type': 'BUY',
                        'price': price,
                        'amount': trade_amount,
                        'cost': cost
                    })
            
            elif signal == 'SELL' and position == 'BTC':
                # Calculate proceeds
                proceeds = price * trade_amount
                
                if balance_btc >= trade_amount:
                    # Execute sell
                    balance_btc -= trade_amount
                    balance_usdt += proceeds
                    position = 'USDT'
                    strategy.record_sell(price)
                    
                    trades.append({
                        'timestamp': timestamp,
                        'type': 'SELL',
                        'price': price,
                        'amount': trade_amount,
                        'proceeds': proceeds
                    })
        
        # Calculate final balance in USDT
        final_price = price_data[-1][1]
        total_value = balance_usdt + (balance_btc * final_price)
        
        # Calculate P&L
        total_pnl = total_value - starting_balance
        pnl_percent = (total_pnl / starting_balance) * 100
        
        # Get strategy stats
        stats = strategy.get_stats()
        
        # Count trades
        buy_count = sum(1 for t in trades if t['type'] == 'BUY')
        sell_count = sum(1 for t in trades if t['type'] == 'SELL')
        
        return {
            'buy_threshold': buy_threshold,
            'sell_threshold': sell_threshold,
            'starting_balance': starting_balance,
            'final_balance': total_value,
            'balance_usdt': balance_usdt,
            'balance_btc': balance_btc,
            'total_pnl': total_pnl,
            'pnl_percent': pnl_percent,
            'total_trades': len(trades),
            'buy_count': buy_count,
            'sell_count': sell_count,
            'wins': stats['wins'],
            'losses': stats['losses'],
            'win_rate': stats['win_rate'],
            'final_position': position,
            'trades': trades
        }
    
    def compare_strategies(self, price_data: List[Tuple[datetime, float]]) -> List[Dict]:
        """
        Test multiple threshold configurations
        
        Args:
            price_data: Historical price data
            
        Returns:
            List of results for each configuration
        """
        print("=" * 70)
        print("BACKTESTING MULTIPLE THRESHOLD CONFIGURATIONS")
        print("=" * 70)
        print()
        
        # Test configurations
        configs = [
            (0.5, 0.5),
            (1.0, 1.0),
            (1.5, 1.5),
            (2.0, 2.0),
        ]
        
        results = []
        
        for buy_threshold, sell_threshold in configs:
            print(f"Testing: Buy {buy_threshold}% / Sell {sell_threshold}%...")
            
            result = self.run_backtest(
                price_data,
                buy_threshold,
                sell_threshold
            )
            
            results.append(result)
            
            # Brief summary
            print(f"  Result: {result['total_trades']} trades, "
                  f"P&L: ${result['total_pnl']:,.2f} ({result['pnl_percent']:.2f}%), "
                  f"Win Rate: {result['win_rate']:.1f}%")
            print()
        
        return results
    
    def print_results(self, results: List[Dict]) -> None:
        """
        Print formatted backtest results
        
        Args:
            results: List of backtest results
        """
        print("=" * 70)
        print("BACKTEST RESULTS SUMMARY")
        print("=" * 70)
        print()
        
        # Sort by P&L
        sorted_results = sorted(results, key=lambda x: x['total_pnl'], reverse=True)
        
        print(f"{'Thresholds':<20} {'Trades':<10} {'Win Rate':<12} {'P&L ($)':<15} {'P&L (%)':<10}")
        print("-" * 70)
        
        for result in sorted_results:
            thresholds = f"{result['buy_threshold']:.1f}% / {result['sell_threshold']:.1f}%"
            trades = str(result['total_trades'])
            win_rate = f"{result['win_rate']:.1f}%"
            pnl_dollar = f"${result['total_pnl']:,.2f}"
            pnl_percent = f"{result['pnl_percent']:.2f}%"
            
            print(f"{thresholds:<20} {trades:<10} {win_rate:<12} {pnl_dollar:<15} {pnl_percent:<10}")
        
        print()
        
        # Best configuration
        best = sorted_results[0]
        print("🏆 BEST CONFIGURATION:")
        print(f"   Thresholds: {best['buy_threshold']:.1f}% Buy / {best['sell_threshold']:.1f}% Sell")
        print(f"   Total P&L: ${best['total_pnl']:,.2f} ({best['pnl_percent']:.2f}%)")
        print(f"   Total Trades: {best['total_trades']}")
        print(f"   Win Rate: {best['win_rate']:.1f}%")
        print(f"   Final Position: {best['final_position']}")
        print()
        
        # Detailed best results
        print("=" * 70)
        print("DETAILED RESULTS - BEST CONFIGURATION")
        print("=" * 70)
        print()
        print(f"Starting Balance:    ${best['starting_balance']:,.2f} USDT")
        print(f"Final Balance:       ${best['final_balance']:,.2f} USDT")
        print(f"  ├─ USDT:           ${best['balance_usdt']:,.2f}")
        print(f"  └─ BTC:            {best['balance_btc']:.6f}")
        print()
        print(f"Total P&L:           ${best['total_pnl']:,.2f} ({best['pnl_percent']:+.2f}%)")
        print()
        print(f"Trading Activity:")
        print(f"  ├─ Total Trades:   {best['total_trades']}")
        print(f"  ├─ Buy Orders:     {best['buy_count']}")
        print(f"  ├─ Sell Orders:    {best['sell_count']}")
        print(f"  ├─ Wins:           {best['wins']}")
        print(f"  ├─ Losses:         {best['losses']}")
        print(f"  └─ Win Rate:       {best['win_rate']:.1f}%")
        print()
        
        # Recent trades sample
        if best['trades']:
            print("Recent Trades (last 5):")
            print("-" * 70)
            for trade in best['trades'][-5:]:
                trade_type = trade['type']
                timestamp = trade['timestamp'].strftime('%Y-%m-%d %H:%M')
                price = trade['price']
                
                print(f"  {timestamp} | {trade_type:4} | ${price:,.2f}")
            print()
        
        print("=" * 70)

def main():
    """
    Main backtesting function
    """
    print("=" * 70)
    print("GRID TRADING STRATEGY BACKTESTER")
    print("=" * 70)
    print()
    
    # Initialize backtester
    backtester = Backtester(symbol='BTC/USDT', days=7)
    
    try:
        # Fetch historical data
        price_data = backtester.fetch_historical_data()
        
        if not price_data:
            print("❌ No historical data retrieved. Please check your connection.")
            return
        
        # Add delay to avoid rate limits
        time.sleep(1)
        
        # Test multiple configurations
        results = backtester.compare_strategies(price_data)
        
        # Print summary
        backtester.print_results(results)
        
        print("✓ Backtest complete!")
        print()
        print("💡 Tips:")
        print("   - Use the best threshold settings in your .env file")
        print("   - Remember: past performance doesn't guarantee future results")
        print("   - Always start with testnet to verify live trading")
        print()
        
    except ccxt.NetworkError as e:
        print(f"❌ Network error: {e}")
        print("   Please check your internet connection.")
    except ccxt.ExchangeError as e:
        print(f"❌ Exchange error: {e}")
        print("   The exchange may be unavailable or rate limiting.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

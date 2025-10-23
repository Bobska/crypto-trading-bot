"""
Performance Analytics Module
Analyzes trading performance from log files and generates detailed reports
"""
import re
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

class PerformanceAnalyzer:
    """
    Analyzes trading performance and calculates key metrics
    
    Parses trade logs to extract trade history and computes:
    - Sharpe ratio (risk-adjusted returns)
    - Maximum drawdown
    - Win/loss statistics
    - Best/worst trading hours
    - Performance by market conditions
    """
    
    def __init__(self, log_dir: str = 'logs'):
        """
        Initialize Performance Analyzer
        
        Args:
            log_dir: Directory containing trade log files
        """
        self.log_dir = Path(log_dir)
        self.trades: List[Dict] = []
        self.equity_curve: List[float] = []
        
    def parse_logs(self, days: int = 7) -> None:
        """
        Parse log files to extract trade history
        
        Args:
            days: Number of recent days to analyze (default: 7)
        """
        self.trades = []
        
        # Get all log files in directory
        log_files = sorted(self.log_dir.glob('trades_*.log'), reverse=True)
        
        if not log_files:
            print(f"⚠️  No log files found in {self.log_dir}")
            return
        
        # Limit to recent days
        log_files = log_files[:days]
        
        print(f"📊 Analyzing {len(log_files)} log file(s)...")
        
        for log_file in log_files:
            self._parse_log_file(log_file)
        
        print(f"✅ Parsed {len(self.trades)} trades")
        
        # Sort trades by timestamp
        self.trades.sort(key=lambda x: x['timestamp'])
        
        # Build equity curve
        self._build_equity_curve()
    
    def _parse_log_file(self, log_file: Path) -> None:
        """Parse a single log file for trade records"""
        
        # Pattern to match: 2025-10-23 08:14:00 - GridTradingStrategy - INFO - 📝 BUY RECORDED: $65,000.00 (Trade #1)
        buy_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*BUY RECORDED: \$([0-9,]+\.\d{2})'
        sell_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*SELL RECORDED: \$([0-9,]+\.\d{2})'
        
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all buys
        for match in re.finditer(buy_pattern, content):
            timestamp_str = match.group(1)
            price_str = match.group(2).replace(',', '')
            
            self.trades.append({
                'type': 'BUY',
                'price': float(price_str),
                'timestamp': datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S'),
                'hour': int(timestamp_str.split()[1].split(':')[0])
            })
        
        # Find all sells
        for match in re.finditer(sell_pattern, content):
            timestamp_str = match.group(1)
            price_str = match.group(2).replace(',', '')
            
            self.trades.append({
                'type': 'SELL',
                'price': float(price_str),
                'timestamp': datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S'),
                'hour': int(timestamp_str.split()[1].split(':')[0])
            })
    
    def _build_equity_curve(self) -> None:
        """Build equity curve from trade history"""
        if not self.trades:
            return
        
        self.equity_curve = [10000.0]  # Starting capital
        last_buy_price = None
        
        for trade in self.trades:
            if trade['type'] == 'BUY':
                last_buy_price = trade['price']
            elif trade['type'] == 'SELL' and last_buy_price:
                # Calculate profit/loss
                profit_pct = (trade['price'] - last_buy_price) / last_buy_price
                new_equity = self.equity_curve[-1] * (1 + profit_pct)
                self.equity_curve.append(new_equity)
                last_buy_price = None
    
    def calculate_sharpe_ratio(self, risk_free_rate: float = 0.0) -> float:
        """
        Calculate Sharpe ratio (risk-adjusted returns)
        
        Args:
            risk_free_rate: Annual risk-free rate (default: 0.0)
            
        Returns:
            Sharpe ratio
        """
        if len(self.equity_curve) < 2:
            return 0.0
        
        # Calculate returns
        returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
        
        if len(returns) == 0 or np.std(returns) == 0:
            return 0.0
        
        # Sharpe ratio = (mean return - risk free rate) / std dev of returns
        sharpe = (np.mean(returns) - risk_free_rate) / np.std(returns)
        
        # Annualize (assuming daily trading)
        return sharpe * np.sqrt(365)
    
    def calculate_max_drawdown(self) -> Tuple[float, int, int]:
        """
        Calculate maximum drawdown
        
        Returns:
            Tuple of (max_drawdown_pct, peak_index, trough_index)
        """
        if len(self.equity_curve) < 2:
            return 0.0, 0, 0
        
        equity = np.array(self.equity_curve)
        
        # Calculate running maximum
        running_max = np.maximum.accumulate(equity)
        
        # Calculate drawdown at each point
        drawdown = (equity - running_max) / running_max * 100
        
        # Find maximum drawdown
        max_dd_idx = int(np.argmin(drawdown))
        max_dd = float(drawdown[max_dd_idx])
        
        # Find the peak before this drawdown
        peak_idx = int(np.argmax(equity[:max_dd_idx+1])) if max_dd_idx > 0 else 0
        
        return abs(max_dd), peak_idx, max_dd_idx
    
    def calculate_win_loss_stats(self) -> Dict:
        """Calculate win/loss statistics"""
        if len(self.trades) < 2:
            return {
                'total_trades': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'profit_factor': 0.0
            }
        
        wins = []
        losses = []
        last_buy_price = None
        
        for trade in self.trades:
            if trade['type'] == 'BUY':
                last_buy_price = trade['price']
            elif trade['type'] == 'SELL' and last_buy_price:
                profit_pct = (trade['price'] - last_buy_price) / last_buy_price * 100
                
                if profit_pct > 0:
                    wins.append(profit_pct)
                else:
                    losses.append(abs(profit_pct))
                
                last_buy_price = None
        
        total_trades = len(wins) + len(losses)
        win_rate = (len(wins) / total_trades * 100) if total_trades > 0 else 0.0
        avg_win = np.mean(wins) if wins else 0.0
        avg_loss = np.mean(losses) if losses else 0.0
        
        # Profit factor = gross profit / gross loss
        gross_profit = sum(wins) if wins else 0.0
        gross_loss = sum(losses) if losses else 0.0
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0.0
        
        return {
            'total_trades': total_trades,
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor
        }
    
    def analyze_hourly_performance(self) -> Dict[int, Dict]:
        """Analyze performance by hour of day"""
        hourly_stats: Dict[int, Dict] = defaultdict(lambda: {'wins': 0, 'losses': 0, 'total': 0, 'win_rate': 0.0})
        
        last_buy = None
        
        for trade in self.trades:
            if trade['type'] == 'BUY':
                last_buy = trade
            elif trade['type'] == 'SELL' and last_buy:
                hour = trade['hour']
                profit = (trade['price'] - last_buy['price']) / last_buy['price']
                
                hourly_stats[hour]['total'] += 1
                if profit > 0:
                    hourly_stats[hour]['wins'] += 1
                else:
                    hourly_stats[hour]['losses'] += 1
                
                last_buy = None
        
        # Calculate win rates
        for hour in hourly_stats:
            total = hourly_stats[hour]['total']
            wins = hourly_stats[hour]['wins']
            hourly_stats[hour]['win_rate'] = float((wins / total * 100) if total > 0 else 0.0)
        
        return dict(hourly_stats)
    
    def generate_report(self) -> None:
        """Generate and print formatted performance report"""
        print("\n" + "=" * 80)
        print("TRADING PERFORMANCE ANALYSIS")
        print("=" * 80)
        
        if not self.trades:
            print("\n⚠️  No trades found in logs")
            print("   Run the bot to generate trading data")
            return
        
        # Basic info
        print(f"\n📅 Analysis Period:")
        print(f"   First Trade: {self.trades[0]['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Last Trade:  {self.trades[-1]['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Total Trades: {len(self.trades)}")
        
        # Win/Loss Statistics
        stats = self.calculate_win_loss_stats()
        print(f"\n📊 Win/Loss Statistics:")
        print(f"   Completed Trades: {stats['total_trades']}")
        print(f"   Wins: {stats['wins']} | Losses: {stats['losses']}")
        print(f"   Win Rate: {stats['win_rate']:.1f}%")
        print(f"   Average Win: +{stats['avg_win']:.2f}%")
        print(f"   Average Loss: -{stats['avg_loss']:.2f}%")
        print(f"   Profit Factor: {stats['profit_factor']:.2f}")
        
        # Risk Metrics
        if len(self.equity_curve) > 1:
            sharpe = self.calculate_sharpe_ratio()
            max_dd, peak_idx, trough_idx = self.calculate_max_drawdown()
            
            print(f"\n📉 Risk Metrics:")
            print(f"   Sharpe Ratio: {sharpe:.2f}")
            print(f"   Maximum Drawdown: {max_dd:.2f}%")
            
            # Equity curve stats
            initial_equity = self.equity_curve[0]
            final_equity = self.equity_curve[-1]
            total_return = (final_equity - initial_equity) / initial_equity * 100
            
            print(f"\n💰 Equity Curve:")
            print(f"   Starting Capital: ${initial_equity:,.2f}")
            print(f"   Ending Capital: ${final_equity:,.2f}")
            print(f"   Total Return: {total_return:+.2f}%")
        
        # Hourly Performance
        hourly = self.analyze_hourly_performance()
        if hourly:
            print(f"\n⏰ Best/Worst Trading Hours:")
            
            # Sort by win rate
            sorted_hours = sorted(hourly.items(), key=lambda x: x[1]['win_rate'], reverse=True)
            
            if sorted_hours:
                best_hour, best_stats = sorted_hours[0]
                worst_hour, worst_stats = sorted_hours[-1]
                
                print(f"   Best Hour: {best_hour}:00 (Win Rate: {best_stats['win_rate']:.1f}%, {best_stats['total']} trades)")
                print(f"   Worst Hour: {worst_hour}:00 (Win Rate: {worst_stats['win_rate']:.1f}%, {worst_stats['total']} trades)")
                
                # Show top 3 hours if available
                if len(sorted_hours) >= 3:
                    print(f"\n   Top 3 Hours:")
                    for i, (hour, stats) in enumerate(sorted_hours[:3], 1):
                        print(f"   {i}. {hour}:00 - Win Rate: {stats['win_rate']:.1f}% ({stats['total']} trades)")
        
        print("\n" + "=" * 80)
    
    def plot_equity_curve(self) -> None:
        """Plot equity curve using matplotlib"""
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("⚠️  matplotlib not installed. Install with: pip install matplotlib")
            return
        
        if len(self.equity_curve) < 2:
            print("⚠️  Not enough data to plot equity curve")
            return
        
        plt.figure(figsize=(12, 6))
        plt.plot(self.equity_curve, linewidth=2, color='#2E86AB')
        plt.title('Equity Curve', fontsize=14, fontweight='bold')
        plt.xlabel('Trade Number', fontsize=12)
        plt.ylabel('Equity ($)', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Add horizontal line at starting equity
        plt.axhline(y=self.equity_curve[0], color='gray', linestyle='--', alpha=0.5, label='Starting Capital')
        
        # Highlight max drawdown
        max_dd, peak_idx, trough_idx = self.calculate_max_drawdown()
        if max_dd > 0:
            plt.plot([peak_idx, trough_idx], 
                    [self.equity_curve[peak_idx], self.equity_curve[trough_idx]], 
                    'r--', linewidth=2, label=f'Max Drawdown: {max_dd:.1f}%')
        
        plt.legend()
        plt.tight_layout()
        plt.savefig('equity_curve.png', dpi=150)
        print("📊 Equity curve saved to equity_curve.png")
        plt.show()


def main():
    """Run performance analysis as standalone script"""
    print("🔍 Crypto Trading Bot - Performance Analytics\n")
    
    # Create analyzer
    analyzer = PerformanceAnalyzer()
    
    # Parse logs (last 7 days)
    analyzer.parse_logs(days=7)
    
    # Generate report
    analyzer.generate_report()
    
    # Ask if user wants to plot equity curve
    if len(analyzer.equity_curve) > 1:
        print("\n📈 Generate equity curve plot? (requires matplotlib)")
        response = input("Enter 'y' to plot, any other key to skip: ").lower()
        
        if response == 'y':
            analyzer.plot_equity_curve()


if __name__ == "__main__":
    main()

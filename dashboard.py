"""
Trading Bot Dashboard

A comprehensive analytics dashboard that displays trading performance metrics,
profit/loss analysis, and activity patterns from log files.

Features:
- Total P&L calculation
- Win/loss ratio and statistics
- Best and worst trades
- Hourly trading activity patterns
- Formatted display with colors
- Auto-refresh every 5 minutes

Usage: python dashboard.py
Exit: Ctrl+C
"""
import os
import re
import time
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Tuple, Optional

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_all_log_files() -> List[Path]:
    """
    Get all log files from the logs directory
    
    Returns:
        List of Path objects for log files, sorted by date
    """
    logs_dir = Path('logs')
    
    if not logs_dir.exists():
        return []
    
    log_files = list(logs_dir.glob('trades_*.log'))
    return sorted(log_files, key=lambda x: x.stat().st_mtime)

def parse_trade(line: str) -> Optional[Dict]:
    """
    Parse a trade line from the log
    
    Args:
        line: Log line containing trade information
        
    Returns:
        Dictionary with trade data or None if not a trade line
    """
    # Extract timestamp
    timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
    if not timestamp_match:
        return None
    
    timestamp = timestamp_match.group(1)
    
    # Parse BUY orders
    buy_match = re.search(r'BUY ORDER PLACED.*?([0-9.]+) BTC.*?market price', line)
    if buy_match:
        amount = float(buy_match.group(1))
        
        # Try to find price in nearby context (usually logged separately)
        price_match = re.search(r'\$([0-9,]+\.[0-9]+)', line)
        price = float(price_match.group(1).replace(',', '')) if price_match else None
        
        return {
            'timestamp': timestamp,
            'type': 'BUY',
            'amount': amount,
            'price': price
        }
    
    # Parse SELL orders
    sell_match = re.search(r'SELL ORDER PLACED.*?([0-9.]+) BTC.*?market price', line)
    if sell_match:
        amount = float(sell_match.group(1))
        
        price_match = re.search(r'\$([0-9,]+\.[0-9]+)', line)
        price = float(price_match.group(1).replace(',', '')) if price_match else None
        
        return {
            'timestamp': timestamp,
            'type': 'SELL',
            'amount': amount,
            'price': price
        }
    
    return None

def extract_price_from_context(lines: List[str], index: int) -> Optional[float]:
    """
    Extract price from surrounding lines
    
    Args:
        lines: All log lines
        index: Index of the trade line
        
    Returns:
        Price as float or None
    """
    # Look at previous 5 lines for price information
    start = max(0, index - 5)
    context_lines = lines[start:index + 1]
    
    for line in reversed(context_lines):
        # Look for "Executing BUY/SELL order at $XXX"
        price_match = re.search(r'Executing (?:BUY|SELL) order at \$([0-9,]+\.[0-9]+)', line)
        if price_match:
            return float(price_match.group(1).replace(',', ''))
        
        # Look for "Current price for BTC/USDT: $XXX"
        price_match = re.search(r'Current price for .+?: \$([0-9,]+\.[0-9]+)', line)
        if price_match:
            return float(price_match.group(1).replace(',', ''))
    
    return None

def parse_all_trades() -> Tuple[List[Dict], Dict]:
    """
    Parse all trades from all log files
    
    Returns:
        Tuple of (list of trades, metadata dictionary)
    """
    log_files = get_all_log_files()
    
    if not log_files:
        return [], {}
    
    all_trades = []
    metadata = {
        'first_trade': None,
        'last_trade': None,
        'total_files': len(log_files)
    }
    
    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                trade = parse_trade(line)
                
                if trade:
                    # If price not found in trade line, look at context
                    if trade['price'] is None:
                        trade['price'] = extract_price_from_context(lines, i)
                    
                    if trade['price']:  # Only add trades with valid prices
                        all_trades.append(trade)
                        
                        # Update metadata
                        if metadata['first_trade'] is None:
                            metadata['first_trade'] = trade['timestamp']
                        metadata['last_trade'] = trade['timestamp']
        
        except Exception as e:
            print(f"Error reading {log_file}: {e}")
    
    return all_trades, metadata

def calculate_pnl(trades: List[Dict]) -> Dict:
    """
    Calculate profit and loss from trades
    
    Args:
        trades: List of trade dictionaries
        
    Returns:
        Dictionary with P&L statistics
    """
    if not trades:
        return {
            'total_pnl': 0.0,
            'total_pnl_percent': 0.0,
            'wins': 0,
            'losses': 0,
            'win_rate': 0.0,
            'best_trade': None,
            'worst_trade': None,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'trade_pairs': []
        }
    
    # Pair buy and sell orders
    buy_stack = []
    trade_pairs = []
    
    for trade in trades:
        if trade['type'] == 'BUY':
            buy_stack.append(trade)
        elif trade['type'] == 'SELL' and buy_stack:
            buy_trade = buy_stack.pop(0)  # FIFO
            
            # Calculate P&L for this pair
            buy_price = buy_trade['price']
            sell_price = trade['price']
            amount = trade['amount']
            
            pnl = (sell_price - buy_price) * amount
            pnl_percent = ((sell_price - buy_price) / buy_price) * 100
            
            trade_pair = {
                'buy_time': buy_trade['timestamp'],
                'sell_time': trade['timestamp'],
                'buy_price': buy_price,
                'sell_price': sell_price,
                'amount': amount,
                'pnl': pnl,
                'pnl_percent': pnl_percent
            }
            trade_pairs.append(trade_pair)
    
    # Calculate statistics
    if not trade_pairs:
        return {
            'total_pnl': 0.0,
            'total_pnl_percent': 0.0,
            'wins': 0,
            'losses': 0,
            'win_rate': 0.0,
            'best_trade': None,
            'worst_trade': None,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'trade_pairs': []
        }
    
    total_pnl = sum(pair['pnl'] for pair in trade_pairs)
    wins = [pair for pair in trade_pairs if pair['pnl'] > 0]
    losses = [pair for pair in trade_pairs if pair['pnl'] <= 0]
    
    win_count = len(wins)
    loss_count = len(losses)
    win_rate = (win_count / len(trade_pairs)) * 100 if trade_pairs else 0.0
    
    best_trade = max(trade_pairs, key=lambda x: x['pnl'])
    worst_trade = min(trade_pairs, key=lambda x: x['pnl'])
    
    avg_win = sum(pair['pnl'] for pair in wins) / len(wins) if wins else 0.0
    avg_loss = sum(pair['pnl'] for pair in losses) / len(losses) if losses else 0.0
    
    # Calculate overall P&L percentage (weighted average)
    total_invested = sum(pair['buy_price'] * pair['amount'] for pair in trade_pairs)
    total_pnl_percent = (total_pnl / total_invested * 100) if total_invested > 0 else 0.0
    
    return {
        'total_pnl': total_pnl,
        'total_pnl_percent': total_pnl_percent,
        'wins': win_count,
        'losses': loss_count,
        'win_rate': win_rate,
        'best_trade': best_trade,
        'worst_trade': worst_trade,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'trade_pairs': trade_pairs
    }

def calculate_hourly_activity(trades: List[Dict]) -> Dict[int, int]:
    """
    Calculate trading activity by hour of day
    
    Args:
        trades: List of trade dictionaries
        
    Returns:
        Dictionary mapping hour (0-23) to trade count
    """
    hourly_counts = defaultdict(int)
    
    for trade in trades:
        try:
            dt = datetime.strptime(trade['timestamp'], '%Y-%m-%d %H:%M:%S')
            hourly_counts[dt.hour] += 1
        except:
            continue
    
    return dict(hourly_counts)

def format_currency(value: float) -> str:
    """Format value as currency with color"""
    if value > 0:
        return f"{Colors.GREEN}+${value:,.2f}{Colors.ENDC}"
    elif value < 0:
        return f"{Colors.RED}-${abs(value):,.2f}{Colors.ENDC}"
    else:
        return f"${value:,.2f}"

def format_percent(value: float) -> str:
    """Format value as percentage with color"""
    if value > 0:
        return f"{Colors.GREEN}+{value:.2f}%{Colors.ENDC}"
    elif value < 0:
        return f"{Colors.RED}{value:.2f}%{Colors.ENDC}"
    else:
        return f"{value:.2f}%"

def create_bar_chart(data: Dict[int, int], max_width: int = 30) -> str:
    """
    Create a simple ASCII bar chart
    
    Args:
        data: Dictionary mapping hour to count
        max_width: Maximum width of the bars
        
    Returns:
        Formatted bar chart string
    """
    if not data:
        return "No data available"
    
    max_count = max(data.values()) if data else 1
    chart_lines = []
    
    for hour in range(24):
        count = data.get(hour, 0)
        bar_width = int((count / max_count) * max_width) if max_count > 0 else 0
        bar = '█' * bar_width
        
        # Color the bar based on activity level
        if count == 0:
            bar_color = Colors.ENDC
        elif count <= max_count * 0.3:
            bar_color = Colors.YELLOW
        elif count <= max_count * 0.7:
            bar_color = Colors.CYAN
        else:
            bar_color = Colors.GREEN
        
        chart_lines.append(f"{hour:02d}:00 {bar_color}{bar}{Colors.ENDC} {count}")
    
    return '\n'.join(chart_lines)

def display_dashboard(trades: List[Dict], pnl_stats: Dict, metadata: Dict):
    """
    Display the formatted dashboard
    
    Args:
        trades: List of all trades
        pnl_stats: P&L statistics
        metadata: Metadata about the data
    """
    clear_screen()
    
    # Header
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'📊 CRYPTO TRADING BOT DASHBOARD 📊'.center(80)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.ENDC}")
    print()
    print(f"{Colors.BOLD}Last Updated:{Colors.ENDC} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Colors.BOLD}Data Range:{Colors.ENDC} {metadata.get('first_trade', 'N/A')} to {metadata.get('last_trade', 'N/A')}")
    print(f"{Colors.BOLD}Log Files:{Colors.ENDC} {metadata.get('total_files', 0)}")
    print()
    
    # Trading Summary
    print(f"{Colors.BOLD}{Colors.BLUE}{'─' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}💼 TRADING SUMMARY{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'─' * 80}{Colors.ENDC}")
    
    total_trades = len(trades)
    buy_count = sum(1 for t in trades if t['type'] == 'BUY')
    sell_count = sum(1 for t in trades if t['type'] == 'SELL')
    completed_pairs = len(pnl_stats.get('trade_pairs', []))
    
    print(f"{Colors.BOLD}Total Trades:{Colors.ENDC}       {total_trades}")
    print(f"  ├─ Buy Orders:      {Colors.GREEN}{buy_count}{Colors.ENDC}")
    print(f"  ├─ Sell Orders:     {Colors.RED}{sell_count}{Colors.ENDC}")
    print(f"  └─ Completed Pairs: {Colors.CYAN}{completed_pairs}{Colors.ENDC}")
    print()
    
    # P&L Analysis
    print(f"{Colors.BOLD}{Colors.BLUE}{'─' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}💰 PROFIT & LOSS ANALYSIS{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'─' * 80}{Colors.ENDC}")
    
    if completed_pairs > 0:
        print(f"{Colors.BOLD}Total P&L:{Colors.ENDC}         {format_currency(pnl_stats['total_pnl'])} ({format_percent(pnl_stats['total_pnl_percent'])})")
        print(f"{Colors.BOLD}Win Rate:{Colors.ENDC}          {format_percent(pnl_stats['win_rate'])} ({pnl_stats['wins']}W / {pnl_stats['losses']}L)")
        print(f"{Colors.BOLD}Average Win:{Colors.ENDC}       {format_currency(pnl_stats['avg_win'])}")
        print(f"{Colors.BOLD}Average Loss:{Colors.ENDC}      {format_currency(pnl_stats['avg_loss'])}")
        print()
        
        # Best and Worst Trades
        print(f"{Colors.BOLD}{Colors.BLUE}{'─' * 80}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.BLUE}🏆 BEST & WORST TRADES{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'─' * 80}{Colors.ENDC}")
        
        best = pnl_stats['best_trade']
        worst = pnl_stats['worst_trade']
        
        if best:
            print(f"{Colors.BOLD}{Colors.GREEN}🎯 BEST TRADE:{Colors.ENDC}")
            print(f"  Buy:  ${best['buy_price']:,.2f} at {best['buy_time']}")
            print(f"  Sell: ${best['sell_price']:,.2f} at {best['sell_time']}")
            print(f"  P&L:  {format_currency(best['pnl'])} ({format_percent(best['pnl_percent'])})")
            print()
        
        if worst:
            print(f"{Colors.BOLD}{Colors.RED}⚠️  WORST TRADE:{Colors.ENDC}")
            print(f"  Buy:  ${worst['buy_price']:,.2f} at {worst['buy_time']}")
            print(f"  Sell: ${worst['sell_price']:,.2f} at {worst['sell_time']}")
            print(f"  P&L:  {format_currency(worst['pnl'])} ({format_percent(worst['pnl_percent'])})")
            print()
    else:
        print(f"{Colors.YELLOW}No completed trade pairs yet.{Colors.ENDC}")
        print()
    
    # Hourly Activity
    print(f"{Colors.BOLD}{Colors.BLUE}{'─' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}📈 HOURLY TRADING ACTIVITY{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'─' * 80}{Colors.ENDC}")
    
    hourly_data = calculate_hourly_activity(trades)
    
    if hourly_data:
        bar_chart = create_bar_chart(hourly_data)
        print(bar_chart)
    else:
        print(f"{Colors.YELLOW}No activity data available.{Colors.ENDC}")
    
    print()
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.CYAN}🔄 Auto-refreshing in 5 minutes... (Press Ctrl+C to exit){Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.ENDC}")

def main():
    """
    Main dashboard loop
    """
    print(f"{Colors.BOLD}{Colors.CYAN}🚀 Starting Trading Dashboard...{Colors.ENDC}")
    print()
    
    try:
        while True:
            # Parse all trades and calculate statistics
            trades, metadata = parse_all_trades()
            
            if not trades:
                clear_screen()
                print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.ENDC}")
                print(f"{Colors.BOLD}{Colors.CYAN}{'📊 CRYPTO TRADING BOT DASHBOARD 📊'.center(80)}{Colors.ENDC}")
                print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.ENDC}")
                print()
                print(f"{Colors.YELLOW}⚠️  NO TRADING DATA FOUND{Colors.ENDC}")
                print()
                print("No log files or trades detected yet.")
                print("Please start the bot with: python main.py")
                print()
                print("The dashboard will check again in 5 minutes...")
                print(f"Press Ctrl+C to exit")
                print()
                print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.ENDC}")
                time.sleep(300)  # 5 minutes
                continue
            
            # Calculate P&L statistics
            pnl_stats = calculate_pnl(trades)
            
            # Display dashboard
            display_dashboard(trades, pnl_stats, metadata)
            
            # Wait 5 minutes before refreshing
            time.sleep(300)
    
    except KeyboardInterrupt:
        print()
        print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.ENDC}")
        print(f"{Colors.CYAN}👋 Dashboard stopped by user{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.ENDC}")
        print()

if __name__ == "__main__":
    main()

"""
Trade Export Utility

Parses trading bot log files and exports trade history to CSV format
for analysis in Excel or other spreadsheet applications.

Features:
- Extracts completed trade pairs (BUY + SELL)
- Calculates P&L for each trade
- Exports to CSV with detailed columns
- Prints performance summary

Usage: python export_trades.py
Output: trades_history.csv
"""
import csv
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

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
    buy_match = re.search(r'BUY ORDER PLACED.*?([0-9.]+) BTC', line)
    if buy_match:
        amount = float(buy_match.group(1))
        return {
            'timestamp': timestamp,
            'type': 'BUY',
            'amount': amount,
            'price': None  # Will be filled from context
        }
    
    # Parse SELL orders
    sell_match = re.search(r'SELL ORDER PLACED.*?([0-9.]+) BTC', line)
    if sell_match:
        amount = float(sell_match.group(1))
        return {
            'timestamp': timestamp,
            'type': 'SELL',
            'amount': amount,
            'price': None  # Will be filled from context
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

def parse_all_trades() -> List[Dict]:
    """
    Parse all trades from all log files
    
    Returns:
        List of trade dictionaries
    """
    log_files = get_all_log_files()
    
    if not log_files:
        return []
    
    all_trades = []
    
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
        
        except Exception as e:
            print(f"Error reading {log_file}: {e}")
    
    return all_trades

def pair_trades(trades: List[Dict]) -> List[Dict]:
    """
    Pair BUY and SELL trades together and calculate P&L
    
    Args:
        trades: List of individual trades
        
    Returns:
        List of completed trade pairs with P&L
    """
    buy_stack = []
    trade_pairs = []
    
    for trade in trades:
        if trade['type'] == 'BUY':
            buy_stack.append(trade)
        elif trade['type'] == 'SELL' and buy_stack:
            buy_trade = buy_stack.pop(0)  # FIFO
            
            # Parse timestamps
            buy_time = datetime.strptime(buy_trade['timestamp'], '%Y-%m-%d %H:%M:%S')
            sell_time = datetime.strptime(trade['timestamp'], '%Y-%m-%d %H:%M:%S')
            
            # Calculate P&L
            buy_price = buy_trade['price']
            sell_price = trade['price']
            amount = trade['amount']
            
            pnl_dollar = (sell_price - buy_price) * amount
            pnl_percent = ((sell_price - buy_price) / buy_price) * 100
            
            status = 'Win' if pnl_dollar > 0 else ('Loss' if pnl_dollar < 0 else 'Break-even')
            
            trade_pair = {
                'buy_date': buy_time.strftime('%Y-%m-%d'),
                'buy_time': buy_time.strftime('%H:%M:%S'),
                'buy_price': buy_price,
                'sell_date': sell_time.strftime('%Y-%m-%d'),
                'sell_time': sell_time.strftime('%H:%M:%S'),
                'sell_price': sell_price,
                'amount': amount,
                'pnl_dollar': pnl_dollar,
                'pnl_percent': pnl_percent,
                'status': status,
                'duration_minutes': (sell_time - buy_time).total_seconds() / 60
            }
            
            trade_pairs.append(trade_pair)
    
    return trade_pairs

def export_to_csv(trade_pairs: List[Dict], filename: str = 'trades_history.csv') -> None:
    """
    Export trade pairs to CSV file
    
    Args:
        trade_pairs: List of completed trade pairs
        filename: Output CSV filename
    """
    if not trade_pairs:
        print("No completed trades to export.")
        return
    
    # Define CSV columns
    fieldnames = [
        'Buy Date',
        'Buy Time',
        'Buy Price',
        'Sell Date',
        'Sell Time',
        'Sell Price',
        'Amount (BTC)',
        'P&L ($)',
        'P&L (%)',
        'Status',
        'Duration (min)'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header
        writer.writeheader()
        
        # Write trade data
        for pair in trade_pairs:
            writer.writerow({
                'Buy Date': pair['buy_date'],
                'Buy Time': pair['buy_time'],
                'Buy Price': f"${pair['buy_price']:,.2f}",
                'Sell Date': pair['sell_date'],
                'Sell Time': pair['sell_time'],
                'Sell Price': f"${pair['sell_price']:,.2f}",
                'Amount (BTC)': f"{pair['amount']:.6f}",
                'P&L ($)': f"${pair['pnl_dollar']:,.2f}",
                'P&L (%)': f"{pair['pnl_percent']:.2f}%",
                'Status': pair['status'],
                'Duration (min)': f"{pair['duration_minutes']:.1f}"
            })
    
    print(f"✓ Exported {len(trade_pairs)} trades to {filename}")

def print_summary(trade_pairs: List[Dict]) -> None:
    """
    Print trading performance summary
    
    Args:
        trade_pairs: List of completed trade pairs
    """
    if not trade_pairs:
        print("\nNo completed trades found.")
        return
    
    # Calculate statistics
    total_trades = len(trade_pairs)
    wins = [p for p in trade_pairs if p['pnl_dollar'] > 0]
    losses = [p for p in trade_pairs if p['pnl_dollar'] < 0]
    
    win_count = len(wins)
    loss_count = len(losses)
    win_rate = (win_count / total_trades) * 100 if total_trades > 0 else 0
    
    total_pnl = sum(p['pnl_dollar'] for p in trade_pairs)
    avg_pnl = total_pnl / total_trades if total_trades > 0 else 0
    
    best_trade = max(trade_pairs, key=lambda x: x['pnl_dollar'])
    worst_trade = min(trade_pairs, key=lambda x: x['pnl_dollar'])
    
    avg_duration = sum(p['duration_minutes'] for p in trade_pairs) / total_trades if total_trades > 0 else 0
    
    # Print summary
    print("\n" + "=" * 70)
    print("TRADING PERFORMANCE SUMMARY".center(70))
    print("=" * 70)
    print()
    print(f"Total Completed Trades:  {total_trades}")
    print(f"  ├─ Wins:               {win_count}")
    print(f"  ├─ Losses:             {loss_count}")
    print(f"  └─ Win Rate:           {win_rate:.2f}%")
    print()
    print(f"Total P&L:               ${total_pnl:,.2f}")
    print(f"Average P&L per Trade:   ${avg_pnl:,.2f}")
    print()
    print(f"Best Trade:")
    print(f"  └─ P&L:                ${best_trade['pnl_dollar']:,.2f} ({best_trade['pnl_percent']:.2f}%)")
    print(f"     Buy: ${best_trade['buy_price']:,.2f} → Sell: ${best_trade['sell_price']:,.2f}")
    print()
    print(f"Worst Trade:")
    print(f"  └─ P&L:                ${worst_trade['pnl_dollar']:,.2f} ({worst_trade['pnl_percent']:.2f}%)")
    print(f"     Buy: ${worst_trade['buy_price']:,.2f} → Sell: ${worst_trade['sell_price']:,.2f}")
    print()
    print(f"Average Trade Duration:  {avg_duration:.1f} minutes")
    print()
    
    # Date range
    if trade_pairs:
        first_trade = min(trade_pairs, key=lambda x: x['buy_date'] + ' ' + x['buy_time'])
        last_trade = max(trade_pairs, key=lambda x: x['sell_date'] + ' ' + x['sell_time'])
        print(f"Trading Period:")
        print(f"  └─ From: {first_trade['buy_date']} {first_trade['buy_time']}")
        print(f"     To:   {last_trade['sell_date']} {last_trade['sell_time']}")
    
    print()
    print("=" * 70)

def main():
    """
    Main export function
    """
    print("=" * 70)
    print("CRYPTO TRADING BOT - TRADE EXPORT UTILITY".center(70))
    print("=" * 70)
    print()
    
    # Check for log files
    log_files = get_all_log_files()
    if not log_files:
        print("⚠️  No log files found in 'logs/' directory.")
        print("   Please run the trading bot to generate trade data.")
        print()
        return
    
    print(f"Found {len(log_files)} log file(s)")
    print("Parsing trade data...")
    print()
    
    # Parse trades
    trades = parse_all_trades()
    print(f"✓ Extracted {len(trades)} individual trades")
    
    # Pair trades and calculate P&L
    trade_pairs = pair_trades(trades)
    print(f"✓ Identified {len(trade_pairs)} completed trade pairs")
    print()
    
    # Export to CSV
    export_to_csv(trade_pairs)
    print()
    
    # Print summary
    print_summary(trade_pairs)
    
    print("\n✓ Export complete! Open 'trades_history.csv' in Excel for analysis.")
    print()

if __name__ == "__main__":
    main()

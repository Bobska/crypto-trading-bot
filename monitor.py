"""
Trading Bot Monitor

A real-time monitoring utility that displays bot activity from log files.
Shows recent activity, trading summary, and current status without
the full detail of the main bot output.

Usage: python monitor.py
Exit: Ctrl+C
"""
import os
import time
import re
from datetime import datetime
from pathlib import Path

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_latest_log_file():
    """
    Find the most recent log file in the logs directory
    
    Returns:
        Path to the latest log file, or None if no logs exist
    """
    logs_dir = Path('logs')
    
    if not logs_dir.exists():
        return None
    
    # Find all log files matching the pattern
    log_files = list(logs_dir.glob('trades_*.log'))
    
    if not log_files:
        return None
    
    # Return the most recent log file
    return max(log_files, key=lambda x: x.stat().st_mtime)

def parse_log_data(log_file):
    """
    Parse log file to extract summary information
    
    Args:
        log_file: Path to the log file
        
    Returns:
        Dictionary containing parsed data
    """
    data = {
        'total_trades': 0,
        'buy_orders': 0,
        'sell_orders': 0,
        'last_price': None,
        'current_position': None,
        'last_signal': None,
        'balance_usdt': None,
        'balance_btc': None,
        'win_rate': None,
        'recent_lines': []
    }
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Get last 20 lines
        data['recent_lines'] = lines[-20:] if len(lines) >= 20 else lines
        
        # Parse all lines for summary data
        for line in lines:
            # Count buy orders
            if 'BUY ORDER PLACED' in line or 'Executing BUY order' in line:
                data['buy_orders'] += 1
                data['total_trades'] += 1
                
            # Count sell orders
            if 'SELL ORDER PLACED' in line or 'Executing SELL order' in line:
                data['sell_orders'] += 1
                data['total_trades'] += 1
            
            # Extract current price
            price_match = re.search(r'Current price for .+?: \$([0-9,]+\.[0-9]+)', line)
            if price_match:
                data['last_price'] = price_match.group(1)
            
            # Extract signals
            if 'BUY SIGNAL' in line:
                data['last_signal'] = 'BUY'
            elif 'SELL SIGNAL' in line:
                data['last_signal'] = 'SELL'
            elif 'HOLD' in line and 'signal' in line.lower():
                data['last_signal'] = 'HOLD'
            
            # Extract balance
            balance_match = re.search(r'Account Balance - USDT: ([0-9,]+\.[0-9]+), BTC: ([0-9]+\.[0-9]+)', line)
            if balance_match:
                data['balance_usdt'] = balance_match.group(1)
                data['balance_btc'] = balance_match.group(2)
            
            # Extract position from bot initialization
            if 'Starting position:' in line:
                if 'USDT' in line:
                    data['current_position'] = 'USDT'
                elif 'BTC' in line:
                    data['current_position'] = 'BTC'
            
            # Extract win rate
            win_rate_match = re.search(r'Win Rate: ([0-9]+\.[0-9]+)%', line)
            if win_rate_match:
                data['win_rate'] = win_rate_match.group(1)
        
        # Infer current position from trade count if not explicitly found
        if data['current_position'] is None:
            if data['buy_orders'] > data['sell_orders']:
                data['current_position'] = 'BTC'
            elif data['sell_orders'] > data['buy_orders']:
                data['current_position'] = 'USDT'
            else:
                data['current_position'] = 'USDT'  # Default starting position
                
    except Exception as e:
        print(f"Error parsing log file: {e}")
    
    return data

def format_log_line(line):
    """
    Format a log line for display (clean up encoding issues)
    
    Args:
        line: Raw log line
        
    Returns:
        Formatted line
    """
    # Remove any encoding artifacts
    line = line.replace('âœ…', '✅')
    line = line.replace('ðŸš€', '🚀')
    line = line.replace('ðŸŸ¢', '🟢')
    line = line.replace('ðŸ"´', '🔴')
    line = line.replace('ðŸ¤–', '🤖')
    line = line.replace('ðŸ"¸ï¸', '⏸️')
    line = line.replace('âš ï¸', '⚠️')
    line = line.replace('â�Œ', '❌')
    
    return line.strip()

def display_monitor(log_file, data):
    """
    Display the monitoring interface
    
    Args:
        log_file: Path to the log file being monitored
        data: Parsed log data dictionary
    """
    clear_screen()
    
    # Header
    print("=" * 70)
    print("🔍 CRYPTO TRADING BOT MONITOR".center(70))
    print("=" * 70)
    print()
    
    # File info
    print(f"📄 Log File: {log_file.name}")
    print(f"🕐 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Trading Summary
    print("=" * 70)
    print("📊 TRADING SUMMARY")
    print("=" * 70)
    print(f"Total Trades Today:    {data['total_trades']}")
    print(f"  └─ Buy Orders:       {data['buy_orders']}")
    print(f"  └─ Sell Orders:      {data['sell_orders']}")
    print()
    
    # Current Status
    print("=" * 70)
    print("📈 CURRENT STATUS")
    print("=" * 70)
    
    if data['last_price']:
        print(f"Last Price Checked:    ${data['last_price']}")
    else:
        print(f"Last Price Checked:    Not available")
    
    if data['current_position']:
        position_emoji = "💵" if data['current_position'] == 'USDT' else "₿"
        print(f"Current Position:      {position_emoji} {data['current_position']}")
    else:
        print(f"Current Position:      Unknown")
    
    if data['last_signal']:
        signal_emoji = "🟢" if data['last_signal'] == 'BUY' else ("🔴" if data['last_signal'] == 'SELL' else "⏸️")
        print(f"Last Signal:           {signal_emoji} {data['last_signal']}")
    else:
        print(f"Last Signal:           None yet")
    
    print()
    
    # Balance
    if data['balance_usdt'] and data['balance_btc']:
        print("=" * 70)
        print("💰 ACCOUNT BALANCE")
        print("=" * 70)
        print(f"USDT:                  ${data['balance_usdt']}")
        print(f"BTC:                   {data['balance_btc']}")
        
        if data['win_rate']:
            print(f"Win Rate:              {data['win_rate']}%")
        print()
    
    # Recent Activity
    print("=" * 70)
    print("📜 RECENT ACTIVITY (Last 20 lines)")
    print("=" * 70)
    
    for line in data['recent_lines']:
        formatted_line = format_log_line(line)
        # Only show lines with actual content (not empty)
        if formatted_line:
            print(formatted_line)
    
    print()
    print("=" * 70)
    print("🔄 Refreshing in 60 seconds... (Press Ctrl+C to exit)")
    print("=" * 70)

def main():
    """
    Main monitoring loop
    """
    print("🔍 Starting Trading Bot Monitor...")
    print("Looking for log files...")
    print()
    
    try:
        while True:
            # Find latest log file
            log_file = get_latest_log_file()
            
            if log_file is None:
                clear_screen()
                print("=" * 70)
                print("⚠️  NO LOG FILES FOUND")
                print("=" * 70)
                print()
                print("The bot hasn't created any log files yet.")
                print("Please start the bot with: python main.py")
                print()
                print("Checking again in 60 seconds...")
                print("Press Ctrl+C to exit")
                print("=" * 70)
                time.sleep(60)
                continue
            
            # Parse log data
            data = parse_log_data(log_file)
            
            # Display monitoring interface
            display_monitor(log_file, data)
            
            # Wait before refreshing
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n")
        print("=" * 70)
        print("👋 Monitor stopped by user")
        print("=" * 70)
        print()

if __name__ == "__main__":
    main()

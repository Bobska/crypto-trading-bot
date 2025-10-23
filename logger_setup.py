"""
Logger setup module for Crypto Trading Bot
Configures logging to both console and file with date-based filenames
"""
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

def setup_logger(name: str = 'TradingBot', log_suffix: Optional[str] = None) -> logging.Logger:
    """
    Set up a logger that writes to both console and file
    
    Args:
        name: Name of the logger (default: 'TradingBot')
        log_suffix: Optional suffix for log filename (e.g., 'BTC' creates trades_BTC.log)
                   If None, uses date-based filename (trades_YYYYMMDD.log)
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    # Create unique logger name to avoid conflicts between bots
    logger_key = f"{name}_{log_suffix}" if log_suffix else name
    logger = logging.getLogger(logger_key)
    
    # Only configure if logger doesn't have handlers (avoid duplicate handlers)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler with custom or date-based filename
        if log_suffix:
            # Use custom suffix (e.g., trades_BTC.log, trades_ETH.log)
            log_filename = logs_dir / f'trades_{log_suffix}.log'
        else:
            # Use date-based filename (e.g., trades_20251023.log)
            current_date = datetime.now().strftime('%Y%m%d')
            log_filename = logs_dir / f'trades_{current_date}.log'
        
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Prevent logging messages from being passed to the root logger
        logger.propagate = False
    
    return logger
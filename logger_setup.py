"""
Logger setup module for Crypto Trading Bot
Configures logging to both console and file with date-based filenames
"""
import logging
import os
from datetime import datetime
from pathlib import Path

def setup_logger(name: str = 'TradingBot') -> logging.Logger:
    """
    Set up a logger that writes to both console and file
    
    Args:
        name: Name of the logger (default: 'TradingBot')
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    
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
        
        # File handler with date-based filename
        current_date = datetime.now().strftime('%Y%m%d')
        log_filename = logs_dir / f'trades_{current_date}.log'
        
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Prevent logging messages from being passed to the root logger
        logger.propagate = False
    
    return logger
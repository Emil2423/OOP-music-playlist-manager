"""Logging configuration module for music playlist manager.

Sets up centralized logging with timestamped log files in the logs/ directory.
All application logging is directed to files, keeping the terminal clean for
CLI output only.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path


def setup_logging() -> logging.Logger:
    """Configure application-wide logging with timestamped log files.
    
    Creates logs/ directory if it doesn't exist and initializes logging
    with a timestamped log file. All logging is directed to files only,
    no terminal output.
    
    Log levels:
    - DEBUG: Detailed information for debugging (e.g., SQL queries)
    - INFO: General informational messages (e.g., CREATE operations)
    - WARNING: Warning messages (e.g., data validation issues)
    - ERROR: Error messages (e.g., database failures)
    
    Returns:
        logging.Logger: Configured root logger
        
    Note:
        Log files are stored in logs/ directory with format:
        app_YYYY-MM-DD_HH-MM-SS.log
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Generate timestamped log filename
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_file = log_dir / f"app_{timestamp}.log"
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Create file handler with rotation
    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.DEBUG)
    
    # Create formatter with detailed information
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    # Log initialization
    logger.info(f"Logging initialized - Log file: {log_file}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module.
    
    Args:
        name (str): Module name (usually __name__)
        
    Returns:
        logging.Logger: Logger instance for the module
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Module initialized")
    """
    return logging.getLogger(name)

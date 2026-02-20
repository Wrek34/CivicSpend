"""Logging configuration for CivicSpend."""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from civicspend.config import config


def setup_logging(name: str = "civicspend") -> logging.Logger:
    """Setup logging with file and console handlers."""
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    level = getattr(logging, config.log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Format
    formatter = logging.Formatter(
        config.get('logging.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (rotating)
    log_file = config.get('logging.file', 'data/civicspend.log')
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=config.get('logging.max_bytes', 10485760),
        backupCount=config.get('logging.backup_count', 3)
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


# Default logger
logger = setup_logging()

import logging
import os
from pathlib import Path
from .settings import Settings


def setup_logger(name: str = "payroll") -> logging.Logger:
    """
    Set up and configure logger.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Path(Settings.LOG_SETTINGS["file"]).parent
    os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, Settings.LOG_SETTINGS["level"]))
    
    # Create handlers
    file_handler = logging.FileHandler(Settings.LOG_SETTINGS["file"])
    console_handler = logging.StreamHandler()
    
    # Set level for handlers
    file_handler.setLevel(getattr(logging, Settings.LOG_SETTINGS["level"]))
    console_handler.setLevel(getattr(logging, Settings.LOG_SETTINGS["level"]))
    
    # Create formatter
    formatter = logging.Formatter(Settings.LOG_SETTINGS["format"])
    
    # Add formatter to handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Create default logger instance
logger = setup_logger()
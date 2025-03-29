import os
from pathlib import Path
from typing import Dict, Any, List


class Settings:
    """
    Global settings for the payroll application.
    
    Includes configuration for paths, states, and other application-level settings.
    """
    
    # Project base directory
    BASE_DIR = Path(__file__).parent.parent
    
    # Data directory
    DATA_DIR = BASE_DIR / "data"
    
    # Report output directory
    REPORTS_DIR = BASE_DIR / "reports"
    
    # Supported states
    SUPPORTED_STATES = ["maharashtra", "karnataka"]
    
    # API settings
    API_SETTINGS = {
        "title": "Payroll MVP API",
        "description": "API for payroll calculations with state-specific compliance",
        "version": "0.1.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }
    
    # Logging settings
    LOG_SETTINGS = {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": BASE_DIR / "logs" / "payroll.log"
    }
    
    @classmethod
    def get_state_file_path(cls, state: str) -> Path:
        """
        Get the file path for a state's data file.
        
        Args:
            state: State name (case-insensitive)
            
        Returns:
            Path to the state data file
        """
        state = state.lower()
        return cls.DATA_DIR / f"{state}.json"
    
    @classmethod
    def create_directories(cls) -> None:
        """
        Create necessary directories if they don't exist.
        """
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.REPORTS_DIR, exist_ok=True)
        os.makedirs(cls.BASE_DIR / "logs", exist_ok=True)
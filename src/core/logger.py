"""
Logging configuration for JARVIS
Provides structured logging with file rotation
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime


class JarvisLogger:
    """Centralized logging system for JARVIS."""
    
    def __init__(self, log_dir: Path, log_level: str = "INFO"):
        """
        Initialize logging system.
        
        Args:
            log_dir: Directory for log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create loggers
        self.main_logger = self._setup_logger(
            "jarvis.main",
            log_dir / "jarvis.log",
            log_level
        )
        
        self.command_logger = self._setup_logger(
            "jarvis.commands",
            log_dir / "commands.log",
            "INFO"
        )
        
        self.error_logger = self._setup_logger(
            "jarvis.errors",
            log_dir / "errors.log",
            "ERROR"
        )
    
    def _setup_logger(self, name: str, log_file: Path, level: str) -> logging.Logger:
        """Setup a logger with file rotation."""
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level))
        
        # Remove existing handlers
        logger.handlers.clear()
        
        # File handler with rotation (10MB max, keep 5 backups)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # Only warnings+ to console
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def info(self, message: str):
        """Log info message."""
        self.main_logger.info(message)
    
    def debug(self, message: str):
        """Log debug message."""
        self.main_logger.debug(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.main_logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False):
        """Log error message."""
        self.main_logger.error(message, exc_info=exc_info)
        self.error_logger.error(message, exc_info=exc_info)
    
    def command(self, user_input: str, is_command: bool, success: bool, response: str = ""):
        """Log command execution."""
        status = "SUCCESS" if success else "FAILED"
        cmd_type = "COMMAND" if is_command else "LLM_QUERY"
        self.command_logger.info(f"{cmd_type} [{status}] - Input: {user_input[:100]} - Response: {response[:100]}")
    
    def session_start(self, mode: str):
        """Log session start."""
        self.main_logger.info(f"=== SESSION START === Mode: {mode}")
    
    def session_end(self):
        """Log session end."""
        self.main_logger.info("=== SESSION END ===")
    
    def model_switch(self, old_mode: str, new_mode: str, model: str):
        """Log model switching."""
        self.main_logger.info(f"Model switch: {old_mode} -> {new_mode} (using {model})")

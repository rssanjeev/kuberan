"""
Centralized Logging Configuration for Kuberan

Provides structured logging with:
- Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Colored console output for development
- JSON formatting option for production
- Per-module log configuration
- Timestamp and module information

Usage:
    from app.core.logging_config import get_logger
    
    logger = get_logger(__name__)
    logger.info("Application started")
    logger.error("Failed to fetch data", extra={"ticker": "AAPL"})
"""

import logging
import sys
from typing import Optional
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds colors to console output.
    Uses ANSI color codes for different log levels.
    """
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    # Emoji prefixes for different log levels
    EMOJIS = {
        'DEBUG': '🔍',
        'INFO': '✓',
        'WARNING': '⚠️',
        'ERROR': '✗',
        'CRITICAL': '🔥'
    }
    
    def format(self, record):
        # Add color and emoji to levelname
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.EMOJIS.get(levelname, '')} {levelname}"
            
            # Color the entire message
            color = self.COLORS[levelname]
            reset = self.COLORS['RESET']
            
            # Format the base message
            formatted = super().format(record)
            
            # Apply color
            return f"{color}{formatted}{reset}"
        
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging in production.
    Outputs logs as JSON objects for easy parsing and aggregation.
    """
    
    def format(self, record):
        import json
        
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data)


def setup_logging(
    level: str = "INFO",
    format_type: str = "colored",
    log_file: Optional[str] = None
) -> None:
    """
    Configure logging for the entire application.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: 'colored' for console, 'json' for structured logs
        log_file: Optional file path for file logging
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    if format_type == "json":
        console_formatter = JSONFormatter()
    else:
        # Colored formatter for development
        console_formatter = ColoredFormatter(
            fmt='[%(asctime)s] %(levelname)s [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        
        # Always use JSON format for file logs
        file_formatter = JSONFormatter()
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.INFO)
    logging.getLogger("beanie").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
        
    Example:
        logger = get_logger(__name__)
        logger.info("Processing transaction", extra={"amount": 100})
    """
    return logging.getLogger(name)


# Default configuration
# This will be called when the module is imported
def initialize_default_logging():
    """Initialize default logging configuration."""
    import os
    
    # Get log level from environment or default to INFO
    log_level = os.getenv("LOG_LEVEL", "INFO")
    
    # Get format type from environment or default to colored
    format_type = os.getenv("LOG_FORMAT", "colored")
    
    # Get optional log file from environment
    log_file = os.getenv("LOG_FILE")
    
    setup_logging(
        level=log_level,
        format_type=format_type,
        log_file=log_file
    )


# Initialize logging when module is imported
initialize_default_logging()

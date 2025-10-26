"""
Thesis Guidance Logger Module

This module provides centralized logging configuration for the thesis guidance chat application.
It sets up structured logging with colorized console output and JSON file logging capabilities.

The logger is configured to provide:
- Colorized console output for better readability during development
- JSON formatted file output for structured logging and analysis
- Rotating file handlers to manage log file sizes effectively

Example:
    Basic usage:
        from tg_logger import setup_logger
        logger = setup_logger()
        logger.info("Application started")
        logger.debug("Debug information")
        logger.error("Error occurred")

Author: Jukka Veijanen
"""

import logging
import logging.config
import yaml
import os
import colorlog
from datetime import datetime
from pathlib import Path


def setup_logger():
    """
    Set up and configure the application logger with colorized console output.

    This function initializes a dual-output logging system:
    1. Colorized console output using colorlog for immediate visual feedback
    2. JSON formatted file output for structured logging and analysis

    The logger configuration includes:
    - Color-coded console output with timestamps and log levels
    - JSON formatted file output for structured logging
    - Rotating file handler to manage log file sizes
    - Debug level logging for comprehensive information
    - Daily log file rotation with date-based naming

    Color scheme:
    - DEBUG: Cyan
    - INFO: Green
    - WARNING: Yellow
    - ERROR: Red
    - CRITICAL: Bold red with white background

    Returns:
        logging.Logger: Configured logger instance named 'tg_logger'

    Raises:
        OSError: If logs directory cannot be created
        Exception: If logger configuration fails

    Example:
        >>> logger = setup_logger()
        >>> logger.info("Application initialized successfully")  # Green text
        >>> logger.debug("Processing user request")              # Cyan text
        >>> logger.error("Database connection failed")           # Red text

    Note:
        The function ensures the 'logs' directory exists before configuring
        the file handler. Log files are stored with date-based naming:
        'logs/tg_logger_YYYY-MM-DD.log' with automatic daily rotation.
        Console output uses colorized formatting while file output uses
        plain text with timestamps.
    """
    # Ensure the logs directory exists
    Path("logs").mkdir(exist_ok=True)

    # Create log filename with current date
    log_filename = f"logs/tg_logger_{datetime.now().strftime('%Y-%m-%d')}.log"

    # Define colorized formatter for console output
    color_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red,bg_white",
        },
    )

    # Define plain formatter for file output
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Set up file handler with UTF-8 encoding
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)

    # Set up colorized console handler
    console_handler = colorlog.StreamHandler()
    console_handler.setFormatter(color_formatter)
    console_handler.setLevel(logging.DEBUG)

    # Configure the logger
    logger = logging.getLogger("tg_logger")
    logger.setLevel(logging.DEBUG)

    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()

    # Add both handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Prevent propagation to root logger to avoid duplicate messages
    logger.propagate = False

    return logger


def get_logger():
    """
    Get the configured logger instance.

    This is a convenience function that returns the existing logger
    or creates a new one if it doesn't exist.

    Returns:
        logging.Logger: The configured tg_logger instance

    Example:
        >>> logger = get_logger()
        >>> logger.info("Using existing logger configuration")
    """
    return (
        logging.getLogger("tg_logger")
        if logging.getLogger("tg_logger").handlers
        else setup_logger()
    )


if __name__ == "__main__":
    """
    Test the logger configuration when run as a standalone script.

    This section demonstrates the logger functionality with sample
    messages at each logging level to verify color output and
    file logging are working correctly.
    """
    logger = setup_logger()

    logger.debug("This is a DEBUG message - should appear in cyan")
    logger.info("This is an INFO message - should appear in green")
    logger.warning("This is a WARNING message - should appear in yellow")
    logger.error("This is an ERROR message - should appear in red")
    logger.critical(
        "This is a CRITICAL message - should appear in bold red with white background"
    )

    print(f"\n✅ Logger test completed. Check logs in 'logs/' directory.")
    print(f"📁 Log file: logs/tg_logger_{datetime.now().strftime('%Y-%m-%d')}.log")

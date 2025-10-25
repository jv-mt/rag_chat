"""
Thesis Guidance Logger Module

This module provides centralized logging configuration for the thesis guidance chat application.
It sets up structured JSON logging with both console and file output capabilities.

The logger is configured using YAML configuration files and supports rotating file handlers
to manage log file sizes effectively.

Example:
    Basic usage:
        from tg_logger import setup_logger
        logger = setup_logger()
        logger.info("Application started")
        logger.debug("Debug information")
        logger.error("Error occurred")

Author: Jukka Veijanen
Dependencies: pyyaml, logging, logging.config
"""

import logging
import logging.config
import yaml
import os


def setup_logger():
    """
    Set up and configure the application logger.
    
    This function initializes the logging system using configuration from a YAML file.
    It creates the logs directory if it doesn't exist and configures both console
    and file logging with JSON formatting.
    
    The logger configuration includes:
    - JSON formatted output for structured logging
    - Console output to stderr for immediate feedback
    - Rotating file handler to manage log file sizes
    - Debug level logging for comprehensive information
    
    Returns:
        logging.Logger: Configured logger instance named 'tg_logger'
        
    Raises:
        FileNotFoundError: If the logger configuration file is not found
        yaml.YAMLError: If the configuration file contains invalid YAML
        
    Example:
        >>> logger = setup_logger()
        >>> logger.info("Application initialized successfully")
        >>> logger.debug("Processing user request")
        >>> logger.error("Database connection failed")
        
    Note:
        The function ensures the 'logs' directory exists before configuring
        the file handler. Log files are stored as 'logs/chat_app.log.jsonl'
        with automatic rotation when they exceed 10MB.
    """
    # Ensure the logs directory exists
    os.makedirs("logs", exist_ok=True)

    with open("configs/logger_config.yml", "r") as file:
        config = yaml.safe_load(file.read())
        logging.config.dictConfig(config)

    return logging.getLogger("tg_logger")

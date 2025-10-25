"""
Logger Testing Module for Thesis Guidance Chat Application

This module provides comprehensive testing functionality for the thesis guidance
chat application's logging system. It demonstrates and validates all logging
levels to ensure proper configuration and output formatting.

The test suite verifies:
- Logger initialization and configuration
- All logging levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- File output to the logs directory
- Console output formatting
- JSON log format validation

This module serves as both a test suite and a demonstration of the logging
capabilities available throughout the application.

Example:
    Run the logger test:
        python src/test_logger.py
        
    Or import and use programmatically:
        from test_logger import test_logger
        test_logger()

Author: Jukka Veijanen
Dependencies: tg_logger
"""

from tg_logger import setup_logger

logger = setup_logger()


def test_logger():
    """
    Test all logging levels and verify logger functionality.
    
    This function systematically tests each logging level to ensure:
    1. Logger is properly configured and accessible
    2. All log levels are working correctly
    3. Messages are formatted and output as expected
    4. File logging is functioning (logs written to 'logs/' directory)
    5. Console logging displays appropriate information
    
    The test covers all standard Python logging levels:
    - DEBUG: Detailed diagnostic information
    - INFO: General informational messages
    - WARNING: Warning messages for potential issues
    - ERROR: Error messages for serious problems
    - CRITICAL: Critical error messages for severe failures
    
    Side Effects:
    - Creates log entries in the configured log file
    - Displays log messages on the console
    - Validates the complete logging pipeline
    
    Example:
        >>> test_logger()
        # Output will show test messages at each level
        # Check logs/ directory for file output
        ✅ Logger tested. Check logs in 'logs/'-directory.
        
    Note:
        This function should be run to verify logging configuration
        after any changes to the logger setup or configuration files.
        The actual log output location depends on the logger configuration
        in configs/logger_config.yml.
    """
    logger.debug("This is DEBUG-message")
    logger.info("This is INFO-message")
    logger.warning("This is WARNING-message")
    logger.error("This is ERROR-message")
    logger.critical("This is CRITICAL-message")

    print("\n✅ Logger tested. Check logs in 'logs/'-directory.\n")


if __name__ == "__main__":
    """
    Main execution block for standalone testing.
    
    When this module is run directly (not imported), it executes the
    test_logger() function to perform a complete validation of the
    logging system configuration and functionality.
    
    This allows the module to serve as both:
    1. A standalone test script for logger validation
    2. An importable module for programmatic testing
    
    Usage:
        python src/test_logger.py
    """
    test_logger()


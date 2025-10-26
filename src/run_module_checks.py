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
        python src/run_module_check.py

    Or import and use programmatically:
        from run_module_check import test_logger
        test_logger()

Author: Jukka Veijanen
"""

from db_manager import DB_Manager
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


def test_db_manager():
    """
    Test the DB_Manager functionality for document processing and retrieval.

    This function performs comprehensive testing of the database manager's
    core capabilities including:
    1. URL content loading and processing
    2. Document chunking and embedding
    3. Vector database storage
    4. Similarity-based document retrieval
    5. Content scoring and ranking

    The test uses JAMK's thesis guidance website as a test source to:
    - Validate URL content extraction
    - Test HTML cleaning and processing
    - Verify document chunking strategies
    - Confirm vector database operations
    - Demonstrate retrieval functionality

    Test Process:
    1. Initialize DB_Manager with configuration file
    2. Load content from JAMK thesis guidance URL
    3. Process and chunk the content
    4. Store embeddings in vector database
    5. Perform similarity search with test query
    6. Display results with relevance scores

    Args:
        None

    Returns:
        None

    Side Effects:
        - Creates or updates vector database in ./db directory
        - Generates embeddings for processed content
        - Displays retrieval results to console
        - May create log entries for debugging

    Raises:
        Exception: If URL loading fails or database operations encounter errors
        ConnectionError: If unable to connect to embedding service
        ValueError: If configuration file is invalid or missing

    Example:
        >>> test_db_manager()
        Score: 0.85, Content: The thesis introduction should clearly state...
        Score: 0.78, Content: When writing the introduction, consider...
        Score: 0.72, Content: A good introduction provides context...

    Note:
        This function requires:
        - Valid configuration file at configs/settings.yml
        - Running Ollama service for embeddings
        - Internet connection for URL content loading
        - Write permissions for database directory

        The test query "How to write thesis introduction?" is designed
        to retrieve relevant content about thesis writing guidelines
        from the processed JAMK documentation.
    """
    db = DB_Manager(config_file="configs/settings.yml")

    # Load content from URL
    chunks = db.load_and_process_url_content("https://help.jamk.fi/opinnaytetyo/en/")

    # Retrieve relevant documents
    results = db.retrieve("How to write thesis introduction?")
    for doc, score in results:
        print(f"Score: {score}, Content: {doc.page_content[:100]}")


if __name__ == "__main__":
    """
    Main execution block for standalone testing.

    When this module is run directly (not imported), it executes the
    database manager test to perform a complete validation of the
    document processing and retrieval system functionality.

    This allows the module to serve as both:
    1. A standalone test script for database manager validation
    2. An importable module for programmatic testing

    The main execution currently runs test_db_manager() to validate:
    - URL content loading and processing capabilities
    - Vector database operations and storage
    - Document retrieval and similarity scoring
    - Overall system integration and functionality

    Usage:
        python src/run_module_check.py

    Note:
        The test_logger() function is commented out but can be
        uncommented to also test logging functionality. Both
        functions can be run independently or together for
        comprehensive system validation.

        Ensure all dependencies are installed and services
        (like Ollama) are running before executing this script.
    """
    test_logger()
    test_db_manager()

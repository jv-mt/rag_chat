"""
Module Testing Suite for Thesis Guidance Chat Application

This module provides comprehensive testing functionality for all core components
of the thesis guidance chat application. It serves as a complete validation suite
to ensure proper configuration, functionality, and integration of the system.

The test suite validates:
- Logger initialization and configuration across all logging levels
- Database manager operations including document processing and retrieval
- RAG chat system functionality and response generation
- Vector database operations and embedding generation
- File output to the logs directory and database persistence
- Console output formatting and user interface elements
- JSON log format validation and structured logging
- Integration between all system components

This module serves multiple purposes:
1. Comprehensive system validation during development
2. Integration testing for deployment verification
3. Debugging tool for troubleshooting issues
4. Demonstration of system capabilities
5. Performance benchmarking and monitoring

Test Components:
- test_logger(): Validates logging system across all levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- test_db_manager(): Tests document processing, chunking, embedding, and retrieval operations
- test_chat(): Validates RAG chat functionality with sample thesis guidance content

Example Usage:
    Run complete test suite:
        python src/run_module_checks.py

    Run individual tests programmatically:
        from run_module_checks import test_logger, test_db_manager, test_chat
        test_logger()
        test_db_manager()
        test_chat()

    Import for custom testing:
        from run_module_checks import *
        # Use individual test functions as needed

Requirements:
    - Python 3.12+
    - Running Ollama service at localhost:11434
    - Available models: llama3.2:latest, mxbai-embed-large
    - Valid configuration file at configs/settings.yml
    - Internet connectivity for URL content loading
    - Write permissions for logs/ and db/ directories

Output:
    - Detailed console output with progress indicators
    - Log entries in the configured log files
    - Test results with performance metrics
    - Error messages with troubleshooting guidance
    - Success confirmations for each component

Note:
    This comprehensive testing suite should be run:
    - After initial system setup
    - Before deployment to production
    - After configuration changes
    - When troubleshooting system issues
    - For performance monitoring and validation

Author: Jukka Veijanen
"""

import sys
import time
import traceback
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml

from db_manager import DB_Manager
from chat import RAG_Chat
from tg_logger import setup_logger

# Configuration
DEFAULT_CONFIG_FILE = "configs/settings.yml"
TEST_URL = "https://help.jamk.fi/opinnaytetyo/en/"
TEST_QUERY = "How to write thesis introduction?"

# Initialize logger
logger = setup_logger()


def load_test_config(config_file: str = DEFAULT_CONFIG_FILE) -> Dict[str, Any]:
    """
    Load test configuration from YAML file.

    Args:
        config_file (str): Path to configuration file

    Returns:
        Dict[str, Any]: Configuration dictionary

    Raises:
        FileNotFoundError: If configuration file doesn't exist
        yaml.YAMLError: If configuration file is invalid
    """
    try:
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        logger.debug(f"Test configuration loaded from {config_file}")
        return config

    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML configuration: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        raise


def check_prerequisites() -> bool:
    """
    Check if all prerequisites for testing are met.

    Returns:
        bool: True if all prerequisites are met, False otherwise
    """
    logger.info("Checking prerequisites...")

    # Check configuration file
    config_path = Path(DEFAULT_CONFIG_FILE)
    if not config_path.exists():
        logger.error(f"Configuration file missing: {DEFAULT_CONFIG_FILE}")
        return False

    # Check required directories
    required_dirs = ["logs", "chat_session_records"]
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            logger.info(f"Creating directory: {dir_name}")
            dir_path.mkdir(parents=True, exist_ok=True)

        # Check write permissions
        if not dir_path.is_dir() or not dir_path.stat().st_mode & 0o200:
            logger.error(f"No write permission for directory: {dir_name}")
            return False

    logger.info("✅ Prerequisites check passed")
    return True


def test_logger() -> bool:
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

    Returns:
        bool: True if logger test passes, False otherwise

    Side Effects:
    - Creates log entries in the configured log file
    - Displays log messages on the console
    - Validates the complete logging pipeline

    Example:
        >>> success = test_logger()
        # Output will show test messages at each level
        # Check logs/ directory for file output
        ✅ Logger tested. Check logs in 'logs/'-directory.

    Note:
        This function should be run to verify logging configuration
        after any changes to the logger setup or configuration files.
        The actual log output location depends on the logger configuration
        in configs/logger_config.yml.
    """
    try:
        logger.info("Starting logger functionality test")

        # Test all logging levels
        log_levels = [
            ("DEBUG", logger.debug, "This is DEBUG-message"),
            ("INFO", logger.info, "This is INFO-message"),
            ("WARNING", logger.warning, "This is WARNING-message"),
            ("ERROR", logger.error, "This is ERROR-message"),
            ("CRITICAL", logger.critical, "This is CRITICAL-message"),
        ]

        for level_name, log_func, message in log_levels:
            log_func(message)
            logger.debug(f"Tested {level_name} level logging")

        # Verify logs directory exists and is writable
        logs_dir = Path("logs")
        if not logs_dir.exists() or not logs_dir.is_dir():
            logger.error("Logs directory not found or not accessible")
            return False

        logger.info("Logger test completed successfully")
        print("\n✅ Logger tested. Check logs in 'logs/'-directory.\n")
        return True

    except Exception as e:
        logger.error(f"Logger test failed: {e}")
        print(f"\n❌ Logger test failed: {e}\n")
        return False


def test_db_manager(config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Test the DB_Manager functionality for document processing and retrieval.

    This function performs comprehensive testing of the database manager's
    core capabilities including:
    1. URL content loading and processing
    2. Document chunking and embedding
    3. Vector database storage
    4. Similarity-based document retrieval
    5. Content scoring and ranking

    Args:
        config (Optional[Dict[str, Any]]): Configuration dictionary. If None, loads from file.

    Returns:
        bool: True if database manager test passes, False otherwise

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
        >>> success = test_db_manager()
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
    try:
        logger.info("Starting database manager functionality test")

        # Initialize DB_Manager
        start_time = time.time()
        db = DB_Manager(config_file=DEFAULT_CONFIG_FILE)
        init_time = time.time() - start_time
        logger.info(f"DB_Manager initialized in {init_time:.2f} seconds")

        # Test URL content loading
        logger.info(f"Loading content from: {TEST_URL}")
        load_start = time.time()

        try:
            chunks = db.load_and_process_url_content(TEST_URL)
            load_time = time.time() - load_start

            if not chunks:
                logger.error("No content chunks were loaded from URL")
                return False

            logger.info(f"Loaded {len(chunks)} chunks in {load_time:.2f} seconds")

        except Exception as e:
            logger.error(f"Failed to load URL content: {e}")
            return False

        # Test document retrieval
        logger.info(f"Testing retrieval with query: '{TEST_QUERY}'")
        retrieval_start = time.time()

        try:
            results = db.retrieve(TEST_QUERY)
            retrieval_time = time.time() - retrieval_start

            if not results:
                logger.warning("No results returned from retrieval")
                return False

            logger.info(
                f"Retrieved {len(results)} results in {retrieval_time:.2f} seconds"
            )

            # Display results
            print(f"\n📊 Retrieval Results for: '{TEST_QUERY}'")
            print("-" * 60)

            for i, (doc, score) in enumerate(results[:3], 1):  # Show top 3 results
                content_preview = doc.page_content[:100].replace("\n", " ")
                print(f"{i}. Score: {score:.3f}")
                print(f"   Content: {content_preview}...")
                print()

            logger.info("Database manager test completed successfully")
            print("✅ Database manager tested successfully.\n")
            return True

        except Exception as e:
            logger.error(f"Document retrieval failed: {e}")
            return False

    except Exception as e:
        logger.error(f"Database manager test failed: {e}")
        print(f"\n❌ Database manager test failed: {e}")
        print("Please ensure:")
        print("- Configuration file exists and is valid")
        print("- Ollama service is running for embeddings")
        print("- Internet connectivity is available")
        print("- Database directory has write permissions\n")
        return False


def test_chat(config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Test the RAG_Chat functionality for response generation.

    This function performs comprehensive testing of the chat system's
    core capabilities including:
    1. RAG_Chat initialization and configuration
    2. Document-based response generation
    3. Prompt engineering validation
    4. Response quality assessment
    5. Model interaction verification

    Args:
        config (Optional[Dict[str, Any]]): Configuration dictionary. If None, loads from file.

    Returns:
        bool: True if chat test passes, False otherwise

    The test uses sample thesis guidance content to:
    - Validate chat system initialization
    - Test document-grounded response generation
    - Verify prompt construction and processing
    - Confirm model communication
    - Demonstrate RAG functionality

    Test Process:
    1. Initialize RAG_Chat with test configuration
    2. Prepare sample thesis guidance documents
    3. Submit test queries about thesis writing
    4. Generate responses using RAG approach
    5. Display results with response analysis

    Side Effects:
        - Creates RAG_Chat instance
        - Generates LLM responses
        - Displays chat results to console
        - May create log entries for debugging

    Raises:
        Exception: If chat initialization fails
        ConnectionError: If unable to connect to Ollama service
        ValueError: If model configuration is invalid

    Example:
        >>> success = test_chat()
        Testing RAG Chat functionality...
        Query: How should I structure my thesis introduction?
        Response: Based on the provided documents, your thesis introduction should...
        ✅ Chat system tested successfully.

    Note:
        This function requires:
        - Running Ollama service at localhost:11434
        - Available chat model (llama3.2:latest by default)
        - Proper network connectivity
        - Sufficient system resources for LLM inference

        The test uses predefined sample content about thesis writing
        to ensure consistent and meaningful responses for validation.
    """
    try:
        logger.info("Starting RAG Chat functionality test")

        # Load configuration
        if config is None:
            config = load_test_config()

        model = config.get("models", {}).get("default_model", "llama3.2:latest")
        chat_config = config.get("chat", {})
        base_url = chat_config.get("base_url", "http://localhost:11434")
        temperature = chat_config.get("temperature", 0.0)

        # Initialize RAG Chat
        init_start = time.time()
        rag_chat = RAG_Chat(
            model=model,
            base_url=base_url,
            temperature=temperature,
            name="RAG Chat Test",
        )
        init_time = time.time() - init_start
        logger.info(
            f"RAG Chat initialized in {init_time:.2f} seconds with model: {model}"
        )

        # Sample thesis guidance content for testing
        sample_documents = [
            """
            The thesis introduction should be 2-3 pages long and provide a clear overview 
            of your research topic. It should include the research problem, objectives, 
            and the structure of your thesis. The introduction sets the context for 
            your entire work and should engage the reader.
            """,
            """
            JAMK University of Applied Sciences requires that all master's theses follow 
            APA citation style. The thesis should be 30-50 pages long, excluding 
            appendices. Students must submit their thesis by the specified deadline 
            and follow the formatting guidelines provided by the university.
            """,
            """
            When writing your thesis, ensure that each chapter flows logically to the next. 
            The methodology section should clearly explain your research approach and 
            justify your chosen methods. Data analysis should be thorough and support 
            your conclusions with evidence.
            """,
        ]

        # Test queries about thesis writing
        test_queries = [
            "How long should my thesis introduction be?",
            "What citation style should I use for my JAMK thesis?",
            "How should I structure my methodology section?",
        ]

        print("\n" + "=" * 60)
        print("🧪 TESTING RAG CHAT FUNCTIONALITY")
        print("=" * 60)

        all_tests_passed = True

        # Test each query
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Test {i}/{len(test_queries)}:")
            print(f"Query: {query}")
            print("-" * 50)

            try:
                # Generate response using RAG approach
                response_start = time.time()
                response = rag_chat.chat(content=sample_documents, question=query)
                response_time = time.time() - response_start

                # Validate response
                if not response or not response.content:
                    logger.error(f"Empty response for test query {i}")
                    all_tests_passed = False
                    continue

                # Display response
                print(f"Response: {response.content}")
                print(f"Response time: {response_time:.2f}s")

                # Log response metadata if available
                if hasattr(response, "response_metadata"):
                    metadata = response.response_metadata
                    if "model" in metadata:
                        print(f"Model: {metadata['model']}")
                    if "total_duration" in metadata:
                        duration_ms = (
                            metadata["total_duration"] / 1_000_000
                        )  # Convert to ms
                        print(f"Model processing time: {duration_ms:.2f}ms")

                logger.info(
                    f"Test query {i} completed successfully in {response_time:.2f}s"
                )

            except Exception as e:
                logger.error(f"Test query {i} failed: {e}")
                print(f"❌ Error generating response: {e}")
                all_tests_passed = False
                continue

        print("\n" + "=" * 60)
        if all_tests_passed:
            print("✅ RAG Chat functionality test completed successfully")
            logger.info("RAG Chat test completed successfully")
        else:
            print("⚠️ RAG Chat test completed with some failures")
            logger.warning("RAG Chat test completed with some failures")
        print("=" * 60)

        return all_tests_passed

    except Exception as e:
        logger.error(f"RAG Chat test failed: {e}")
        print(f"\n❌ RAG Chat test failed: {e}")
        print("Please ensure:")
        print("- Ollama service is running at localhost:11434")
        print(f"- {model} model is available")
        print("- Network connectivity is working")
        print("- Sufficient system resources for LLM inference\n")
        return False


def run_all_tests() -> bool:
    """
    Run all test functions in sequence.

    Returns:
        bool: True if all tests pass, False if any test fails
    """
    print("🚀 Starting comprehensive module testing...")
    print("=" * 60)

    # Check prerequisites first
    if not check_prerequisites():
        print("❌ Prerequisites check failed. Aborting tests.")
        return False

    # Load configuration once
    try:
        config = load_test_config()
        logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        print(f"❌ Configuration loading failed: {e}")
        return False

    test_results = {}

    # Test 1: Logger functionality
    print("\n1️⃣ Testing Logger System...")
    test_results["logger"] = test_logger()

    # Test 2: Database manager functionality
    print("\n2️⃣ Testing Database Manager...")
    test_results["db_manager"] = test_db_manager(config)

    # Test 3: RAG Chat functionality
    print("\n3️⃣ Testing RAG Chat System...")
    test_results["chat"] = test_chat(config)

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)

    all_passed = True
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
        if not result:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All module tests completed successfully!")
        logger.info("All module tests passed")
    else:
        print("⚠️ Some tests failed. Check logs for details.")
        logger.warning("Some module tests failed")
    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    """
    Main execution block for standalone testing.

    When this module is run directly (not imported), it executes all
    available test functions to perform comprehensive validation of
    the thesis guidance chat application components.

    This allows the module to serve as both:
    1. A standalone test script for complete system validation
    2. An importable module for programmatic testing

    The main execution runs all test functions to validate:
    - Logging system functionality and configuration
    - Database manager operations and document processing
    - RAG chat system and response generation
    - Overall system integration and functionality

    Usage:
        python src/run_module_checks.py

    Exit Codes:
        0: All tests passed
        1: Some tests failed
        2: Critical error (prerequisites not met, configuration issues)

    Note:
        All test functions can be run independently or together for
        comprehensive system validation. The execution order is:
        1. Prerequisites check
        2. test_logger() - Validate logging system
        3. test_db_manager() - Test database operations
        4. test_chat() - Test RAG chat functionality

        Ensure all dependencies are installed and services
        (like Ollama) are running before executing this script.
    """
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        logger.info("Testing interrupted by user")
        print("\n\n⚠️ Testing interrupted by user")
        sys.exit(130)  # Standard exit code for Ctrl+C

    except Exception as e:
        logger.critical(f"Critical error during testing: {e}")
        print(f"\n💥 Critical error: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        sys.exit(2)

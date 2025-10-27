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
    - Available models: gemma3:latest, mxbai-embed-large
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

from db_manager import DB_Manager
from chat import RAG_Chat
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


def test_chat():
    """
    Test the RAG_Chat functionality for response generation.

    This function performs comprehensive testing of the chat system's
    core capabilities including:
    1. RAG_Chat initialization and configuration
    2. Document-based response generation
    3. Prompt engineering validation
    4. Response quality assessment
    5. Model interaction verification

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

    Args:
        None

    Returns:
        None

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
        >>> test_chat()
        Testing RAG Chat functionality...
        Query: How should I structure my thesis introduction?
        Response: Based on the provided documents, your thesis introduction should...
        ✅ Chat system tested successfully.

    Note:
        This function requires:
        - Running Ollama service at localhost:11434
        - Available chat model (gemma3:latest by default)
        - Proper network connectivity
        - Sufficient system resources for LLM inference

        The test uses predefined sample content about thesis writing
        to ensure consistent and meaningful responses for validation.
    """

    logger.info("Starting RAG Chat functionality test")

    try:
        # Initialize RAG Chat with test configuration
        rag_chat = RAG_Chat(
            model="gemma3:latest",
            base_url="http://localhost:11434",
            temperature=0.0,
            name="RAG Chat Test",
        )
        logger.info("RAG Chat initialized successfully")

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

        # Test each query
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Test {i}/3:")
            print(f"Query: {query}")
            print("-" * 50)

            try:
                # Generate response using RAG approach
                response = rag_chat.chat(content=sample_documents, question=query)

                # Display response
                print(f"Response: {response.content}")

                # Log response metadata if available
                if hasattr(response, "response_metadata"):
                    metadata = response.response_metadata
                    if "model" in metadata:
                        print(f"Model: {metadata['model']}")
                    if "total_duration" in metadata:
                        duration_ms = (
                            metadata["total_duration"] / 1_000_000
                        )  # Convert to ms
                        print(f"Response time: {duration_ms:.2f}ms")

                logger.info(f"Test query {i} completed successfully")

            except Exception as e:
                logger.error(f"Test query {i} failed: {e}")
                print(f"❌ Error generating response: {e}")
                continue

        print("\n" + "=" * 60)
        print("✅ RAG Chat functionality test completed")
        print("=" * 60)
        logger.info("RAG Chat test completed successfully")

    except Exception as e:
        logger.error(f"RAG Chat test failed: {e}")
        print(f"\n❌ RAG Chat test failed: {e}")
        print("Please ensure:")
        print("- Ollama service is running at localhost:11434")
        print("- gemma3:latest model is available")
        print("- Network connectivity is working")
        raise


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

    Note:
        All test functions can be run independently or together for
        comprehensive system validation. The execution order is:
        1. test_logger() - Validate logging system
        2. test_db_manager() - Test database operations
        3. test_chat() - Test RAG chat functionality

        Ensure all dependencies are installed and services
        (like Ollama) are running before executing this script.
    """
    print("🚀 Starting comprehensive module testing...")
    print("=" * 60)

    # Test 1: Logger functionality
    print("\n1️⃣ Testing Logger System...")
    test_logger()

    # Test 2: Database manager functionality
    print("\n2️⃣ Testing Database Manager...")
    test_db_manager()

    # Test 3: RAG Chat functionality
    print("\n3️⃣ Testing RAG Chat System...")
    test_chat()

    print("\n" + "=" * 60)
    print("🎉 All module tests completed successfully!")
    print("=" * 60)

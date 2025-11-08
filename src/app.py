"""
Thesis Guidance Chat Application - Main Streamlit Interface

This module provides the main web interface for the thesis guidance chat application.
It implements a Streamlit-based UI that allows users to load thesis guidance documents
from JAMK University websites and interact with them through a RAG (Retrieval-Augmented
Generation) chatbot.

The application supports:
- Loading and processing web content from JAMK thesis guidance pages
- Vector database storage for efficient document retrieval
- Interactive chat interface with multiple LLM models
- Results storage and viewing capabilities
- Progress tracking for data loading operations

Key Components:
- Document loading from predefined URLs
- Vector database management using Chroma
- RAG-based chat functionality with Ollama models
- CSV-based results storage and retrieval
- Streamlit UI with tabbed interface

Example:
    Run the application:
        streamlit run src/app.py

    Then navigate to the web interface to:
    1. Load thesis guidance documents
    2. Ask questions about thesis writing
    3. View chat history and results

Author: Jukka Veijanen
"""

import json
import pandas as pd
import time
from collections import deque
import streamlit as st
import os
from chat import RAG_Chat, CHAT_MODEL
from db_manager import DB_Manager
from tg_logger import setup_logger
import gc
import requests
import yaml
from typing import List, Dict, Any
import streamlit as st

VECTOR_DATABASE = "vector_database"
SESSION_STORAGE = "results"
DEFAULT_CONFIG_FILE = "configs/settings.yml"

logger = setup_logger()


# Load configuration
def load_config(config_file=DEFAULT_CONFIG_FILE):
    """
    Load application configuration from YAML file.

    Args:
        config_file (str): Path to configuration file

    Returns:
        dict: Configuration dictionary

    Raises:
        FileNotFoundError: If configuration file doesn't exist
        yaml.YAMLError: If configuration file is invalid
    """
    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        logger.info(f"Configuration loaded from {config_file}")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_file}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML configuration: {e}")
        raise


# Load configuration
config = load_config()

# Extract configuration values
app_config = config.get("app", {})
model_config = config.get("models", {})
network_config = config.get("network", {})
storage_config = config.get("storage", {})
ui_config = config.get("ui", {})

# Model configuration
models = model_config.get(
    "available_models", ["llama3.2:latest", "phi3:latest", "qwen3:4b"]
)
default_model = model_config.get("default_model", CHAT_MODEL)
default_index = models.index(default_model) if default_model in models else 0

# Streamlit page configuration
st.set_page_config(
    page_title=app_config.get("title", "Web UI with Loader and Retriever"),
    layout=app_config.get("layout", "wide"),
    initial_sidebar_state=app_config.get("sidebar_state", "expanded"),
)

# Sidebar configuration
st.sidebar.title("Menu")
action = st.sidebar.radio("Choose Action", ["Retrieve", "Load", "References"])
active_model = st.sidebar.selectbox(
    "Select a chat model from dropdown:", models, default_index
)

rag_chat = RAG_Chat(active_model.split(" ")[0])


def get_storage_configuration_file_path() -> str:
    """
    Get the file path for storage based on configuration.

    Returns:
        str: Full file path for storage

    Side Effects:
        Creates the results directory if it doesn't exist
    """
    results_dir = storage_config.get("results_directory", "chat_session_records")
    results_file = storage_config.get("results_filename", "chat_results.csv")

    os.makedirs(results_dir, exist_ok=True)
    file_path = os.path.join(results_dir, results_file)

    return file_path


def get_vector_database() -> DB_Manager:
    """
    Get or create a vector database instance.

    This function manages the vector database singleton in Streamlit's session state.
    If no database exists, it creates a new DB_Manager instance with default configuration.

    Returns:
        DB_Manager: Vector database manager instance

    Example:
        >>> db = get_vector_database()
        >>> documents = db.retrieve("thesis writing guidelines")
    """
    try:
        logger.debug(f"Vector Database: {st.session_state[VECTOR_DATABASE]}")
    except:
        logger.debug("Vector Database not found.")
    if VECTOR_DATABASE not in st.session_state:
        db_manager = DB_Manager(config_file=DEFAULT_CONFIG_FILE)
        st.session_state[VECTOR_DATABASE] = db_manager
        logger.debug(f"Created Vector Database: {st.session_state[VECTOR_DATABASE]}")
    return st.session_state[VECTOR_DATABASE]


def retrieve_documents(query) -> list[dict]:
    """
    Retrieve relevant documents based on a query.

    Args:
        query (str): Search query for document retrieval

    Returns:
        list[dict]: List of dictionaries containing retrieved documents and scores
                   Format: [{"result": Document, "score": float}, ...]

    Example:
        >>> docs = retrieve_documents("How to write thesis introduction?")
        >>> for doc in docs:
        ...     print(f"Score: {doc['score']}, Content: {doc['result'].page_content[:100]}")
    """
    db = get_vector_database()
    logger.debug(f"retrieve({query})")
    try:
        documents = db.retrieve(query=query)
        results = [{"result": r[0], "score": r[-1]} for r in documents]
        return results
    except Exception as e:
        logger.error(f"Error retrieving documents: {e}")
        st.error("Vector database collection not initialized. Please load data first.")
        return []


def get_urls() -> List[str]:
    """
    Get the list of JAMK thesis guidance URLs from file specified in configuration.

    Returns:
        List[str]: List of URLs containing thesis guidance information

    Raises:
        FileNotFoundError: If the URLs file specified in configuration doesn't exist
        ValueError: If no URLs file is configured

    Note:
        URLs are loaded from a text file (one URL per line) specified in the
        configuration file under data_sources.urls_file. Empty lines and lines
        starting with '#' are ignored. This allows for easy maintenance and
        updates without code changes.
    """
    urls_file = config.get("data_sources", {}).get("urls_file")

    if not urls_file:
        logger.error("No URLs file configured in data_sources.urls_file")
        raise ValueError("URLs file not configured in settings")

    try:
        with open(urls_file, "r", encoding="utf-8") as f:
            urls = [
                line.strip()
                for line in f
                if line.strip() and not line.strip().startswith("#")
            ]
        logger.info(f"Loaded {len(urls)} URLs from {urls_file}")
        return urls
    except FileNotFoundError:
        logger.error(f"URLs file not found: {urls_file}")
        raise
    except Exception as e:
        logger.error(f"Error reading URLs file {urls_file}: {e}")
        raise


def load_source_dataset() -> None:
    """
    Load and process thesis guidance documents from configured JAMK websites.

    This function creates a Streamlit interface for loading thesis guidance documents
    from URLs defined in the configuration file. It processes each URL sequentially,
    showing progress and handling errors gracefully.

    Features:
    - Progress bar showing loading status
    - Real-time display of currently processed URLs
    - Configurable timeout and retry settings
    - Automatic garbage collection for memory management

    The function processes both HTML pages and PDF documents, extracting content
    and storing it in the vector database for later retrieval.

    Raises:
        TimeoutError: If URL processing exceeds configured timeout
        Exception: For other processing errors (logged but not re-raised)

    Side Effects:
        - Updates vector database with processed documents
        - Displays progress in Streamlit UI
        - Creates log entries for processing status
    """
    st.write("## Load Source Datasets from JAMK's Web Pages.")
    st.write("This may take a while...")
    if st.button("Submit"):
        db = get_vector_database()
        urls = get_urls()
        len_urls = len(urls)

        # Get UI configuration
        progress_config = ui_config.get("progress_display", {})
        max_lines = progress_config.get("max_lines", 6)
        progress_text = progress_config.get("operation_text", "Operation in progress")
        timeout = network_config.get("request_timeout", 30)

        progress_bar = st.progress(0, text=progress_text)
        lines = deque(maxlen=max_lines)
        output_placeholder = st.empty()

        for i, url in enumerate(urls, 1):
            try:
                with requests.get(url, timeout=timeout) as response:
                    if url:
                        progress_bar.progress(
                            i / len_urls, f"{progress_text}: {i}/{len_urls}"
                        )
                        lines.append(url)
                        output_placeholder.write(list(lines))
                        content = db.load_and_process_url_content(url)
            except TimeoutError:
                logger.error(f"Timeout processing URL {url}")
                st.error(f"Timeout for URL {url}")
            except Exception as e:
                logger.error(f"Error processing URL {url}: {e}")
                st.error(f"Failed to process URL {url}: {e}")

        progress_bar.progress(1.0, "Completed")
        success_message = ui_config.get("messages", {}).get(
            "load_success", "URLs loaded and stored into vector database successfully!"
        )
        st.success(success_message)
        gc.collect()


def initialize_session_storage() -> None:
    """
    Initialize CSV storage for chat results using configured paths.

    This function sets up the CSV storage system in Streamlit's session state.
    It either loads existing results from a CSV file or creates a new DataFrame
    with the required columns. Storage paths are read from configuration.

    The CSV storage includes columns for:
    - timestamp: When the chat occurred
    - duration: Response time in seconds
    - model: Which LLM model was used
    - query: User's input question
    - response: LLM's response content
    - metadata: Response metadata from the LLM
    - documents: Retrieved documents used for context

    Side Effects:
        - Creates or loads DataFrame in session state
        - May create CSV file if it doesn't exist
        - Logs initialization status
    """
    if SESSION_STORAGE not in st.session_state:
        # Get storage configuration
        file_path = get_storage_configuration_file_path()
        columns = [
            "timestamp",
            "duration",
            "model",
            "query",
            "response",
            "metadata",
            "documents",
        ]

        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path, usecols=columns)
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                st.session_state[SESSION_STORAGE] = df
            except Exception as e:
                logger.error(f"Error loading CSV {file_path}: {e}")
                st.session_state[SESSION_STORAGE] = pd.DataFrame(columns=columns)
        else:
            st.session_state[SESSION_STORAGE] = pd.DataFrame(columns=columns)
        gc.collect()


def store_chat_results(
    duration: float,
    model: str,
    query: str,
    response: str,
    metadata: Dict[str, Any],
    documents: List[str],
) -> None:
    """
    Store chat interaction results to configured CSV file.

    Args:
        duration (float): Time taken to process the query in seconds
        model (str): Name of the LLM model used
        query (str): User's input question
        response (str): LLM's response content
        metadata (Dict[str, Any]): Response metadata from the LLM
        documents (List[str]): Retrieved documents used for context

    This function appends the chat results to both the session state DataFrame
    and the persistent CSV file using configured storage paths.

    Side Effects:
        - Updates session state with new chat result
        - Writes updated DataFrame to configured CSV location
        - Shows success/error messages in Streamlit sidebar
        - Performs garbage collection for memory management

    Raises:
        Exception: If CSV writing fails (logged but not re-raised)
    """
    initialize_session_storage()
    documents_json = json.dumps(documents)
    new_row = {
        "timestamp": pd.Timestamp.now(),
        "duration": duration,
        "model": model,
        "query": query,
        "response": response,
        "metadata": str(metadata),
        "documents": documents_json,
    }
    new_df = pd.DataFrame([new_row])
    st.session_state[SESSION_STORAGE] = pd.concat(
        [st.session_state[SESSION_STORAGE], new_df], ignore_index=True
    )

    # Get storage configuration
    file_path = get_storage_configuration_file_path()

    try:
        st.session_state[SESSION_STORAGE].to_csv(file_path, index=False)
        success_message = ui_config.get("messages", {}).get(
            "results_stored", "Chat results stored to"
        )
        st.sidebar.success(f"{success_message} {file_path}")
    except Exception as e:
        logger.error(f"Error saving CSV to {file_path}: {e}")
        st.sidebar.error(f"Failed to save results: {e}")
    del new_df
    gc.collect()


def chat_with_model(documents: List[Dict[str, Any]], input_text: str) -> None:
    """
    Process user query with retrieved documents and display results.

    Args:
        documents (List[Dict[str, Any]]): Retrieved documents with scores
            Format: [{"result": Document, "score": float}, ...]
        input_text (str): User's input question

    This function orchestrates the chat interaction by:
    1. Extracting document content for context
    2. Calling the RAG chat model
    3. Measuring response time
    4. Displaying results in the Streamlit interface
    5. Storing results for future reference

    The function displays:
    - LLM response content
    - Response metadata
    - Retrieved documents with sources and scores

    Side Effects:
        - Displays response in Streamlit UI
        - Shows retrieved documents with metadata
        - Stores results to CSV file
        - Performs garbage collection

    Error Handling:
        Logs errors and displays user-friendly error messages in Streamlit UI
    """
    logger.debug(f"Model: {rag_chat}")
    docs = [d.get("result").page_content for d in documents]
    try:
        start_time = time.time()
        chat_response = rag_chat.chat(docs, input_text)
        duration = time.time() - start_time
    except Exception as e:
        logger.error(f"Chat error: {e}")
        st.error(f"Failed to process chat query: {e}")
        return
    # Display response in a container
    st.write("### Response")
    with st.container(border=True):
        st.markdown(chat_response.content)

        # Metadata in expander for cleaner UI
        with st.expander("📊 Response Metadata", expanded=False):
            st.caption(f"⏱️ Duration: {duration:.2f} seconds")
            st.json(chat_response.response_metadata)

    st.divider()

    # Display retrieved documents in organized containers
    st.write("### Retrieved Documents")
    st.caption(f"Found {len(documents)} relevant document(s)")

    page_contents = [doc.get("result").page_content for doc in documents]

    # Documents section with better error handling and structured labeling
    for i, doc in enumerate(documents, start=1):
        try:
            doc_result = doc.get("result")
            if doc_result is None:
                st.error(f"Document {i} result is None")
                continue

            doc_score = doc.get("score", 0.0)
            doc_metadata = doc_result.metadata
            doc_content = doc_result.page_content

            # Get source information for the title
            source = doc_metadata.get("source", "Unknown Source")
            source_name = source.split("/")[-1] if "/" in source else source

            # Create unique document identifier for client-side processing
            doc_id = f"doc-{i}"

            # Create structured document label with machine-readable attributes
            doc_label = {
                "id": doc_id,
                "index": i,
                "source": source,
                "source_name": source_name,
                "relevance_score": doc_score,
                "content_length": len(doc_content) if doc_content else 0,
            }

            # Create expander with proper title and leave first one expanded
            # Use data attributes for client-side accessibility
            with st.expander(
                f"📄 Document {i}: {source_name} (Relevance: {doc_score:.3f})",
                expanded=(i == 1),
            ):
                # Add machine-readable document label at the top with full doc_label data
                doc_label_json = json.dumps(doc_label)
                st.markdown(
                    f'<div id="doc-label-{i}" class="doc-label" data-doc-id="{doc_id}" data-doc-index="{i}" data-doc-source="{source}" data-doc-score="{doc_score:.3f}" data-doc-label=\'{doc_label_json}\'></div>',
                    unsafe_allow_html=True,
                )

                # Show content info
                st.caption(
                    f"Content length: {len(doc_content) if doc_content else 0} characters"
                )

                # Metadata section with structured labeling
                with st.container():
                    st.markdown("**📋 Metadata**")
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.metric("Relevance Score", f"{doc_score:.3f}")
                    with col2:
                        st.caption("Source Information")
                        st.json(doc_metadata)

                st.divider()

                # Content section with labeled container for easy extraction
                with st.container():
                    st.markdown("**📖 Content**")
                    if doc_content and doc_content.strip():
                        # Wrap content in labeled div for client-side extraction
                        st.markdown(
                            f'<div class="document-content" data-doc-id="{doc_id}">',
                            unsafe_allow_html=True,
                        )
                        st.markdown(doc_content)
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.warning("No content available for this document")

        except Exception as e:
            st.error(f"Error loading document {i}: {str(e)}")

    store_chat_results(
        duration,
        active_model,
        input_text,
        chat_response.content,
        chat_response.response_metadata,
        page_contents,
    )
    gc.collect()


def retrieve() -> None:
    """
    Create and manage the document retrieval and chat interface.

    This function creates a tabbed interface with:
    1. Chat Tab: For asking questions and viewing responses
    2. Results Tab: For viewing stored chat history

    The chat tab includes:
    - Text input for user questions
    - Submit button to process queries
    - Display area for responses and retrieved documents

    The results tab shows:
    - DataFrame of all stored chat interactions
    - Timestamp, model, and query information
    - Download functionality for results

    Side Effects:
        - Creates Streamlit UI components
        - Manages user interactions
        - Displays chat history and results
    """
    chat_tab, history_tab = st.tabs(["Chat", "History"])
    with chat_tab:
        input_text = st.text_input("Enter your question into text box below:")
        if st.button("Submit"):
            documents = retrieve_documents(input_text)
            logger.debug(f"Retrieved {len(documents)} documents.")
            if documents:
                chat_with_model(documents, input_text)
            else:
                no_docs_message = ui_config.get("messages", {}).get(
                    "no_documents", "No documents found."
                )
                st.write(no_docs_message)
                raise ValueError("No documents found.")
    with history_tab:
        st.write("### Stored Chat Results")
        initialize_session_storage()
        df = st.session_state[SESSION_STORAGE]
        # st.dataframe(df, width=True)
        st.dataframe(df, use_container_width=True)
        if df.empty:
            no_results_message = ui_config.get("messages", {}).get(
                "no_results", "No results stored yet."
            )
            st.write(no_results_message)
        gc.collect()


def references() -> None:
    """
    Display references and documentation links.

    This function creates a references page with links to:
    - JAMK thesis guidance documentation
    - Application documentation
    - Technical references

    Side Effects:
        - Displays reference information in Streamlit UI
    """
    st.title("References")
    st.markdown("## JAMK Thesis Guidance Documentation")
    st.markdown("[JAMK Thesis Guidance](https://www.jamk.fi/en/search?s=thesis)")
    st.markdown("## Application Documentation")
    st.markdown(
        "[Thesis Guidance Chat Application Documentation](https://github.com/jv-mt/rag_chat)"
    )
    st.markdown("## Technical References")
    st.markdown("[LangChain Documentation](https://docs.langchain.com/)")
    st.markdown("[Streamlit Documentation](https://docs.streamlit.io/)")
    st.markdown("[Chroma Documentation](https://docs.trychroma.com/)")
    st.markdown("[Ollama Documentation](https://docs.ollama.com/)")


if action == "Load":
    load_source_dataset()
elif action == "Retrieve":
    retrieve()
elif action == "References":
    references()
else:
    pass

gc.collect()

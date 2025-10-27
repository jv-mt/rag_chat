"""
Database Manager for Thesis Guidance Chat Application

This module provides comprehensive database management functionality for the thesis
guidance chat application. It handles vector database operations, document processing,
and content retrieval using Chroma vector database and Ollama embeddings.

The DB_Manager class supports:
- Vector database initialization and management
- PDF and HTML content processing
- Document chunking and embedding
- Similarity-based document retrieval
- Metadata cleaning and management

Key Components:
- Chroma vector database for document storage
- Ollama embeddings for semantic search
- PyMuPDF for PDF processing
- BeautifulSoup for HTML cleaning
- Configurable text splitting strategies

Example:
    Basic usage:
        from db_manager import DB_Manager

        db = DB_Manager(config_file="configs/settings.yml")

        # Load content from URL
        chunks = db.load_and_process_url_content("https://example.com/thesis-guide")

        # Retrieve relevant documents
        results = db.retrieve("How to write thesis introduction?")
        for doc, score in results:
            print(f"Score: {score}, Content: {doc.page_content[:100]}")

Author: Jukka Veijanen
"""

import langchain_core
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import SentenceTransformersTokenTextSplitter
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import re
import os
import pymupdf
import pymupdf4llm
import yaml
import sqlite3
import gc

# import torch

from tg_logger import setup_logger

logger = setup_logger()


class DB_Manager:
    """
    Database Manager for vector database operations and document processing.

    This class manages all database operations for the thesis guidance chat application,
    including document loading, processing, embedding, and retrieval. It uses Chroma
    as the vector database backend with Ollama embeddings for semantic search.

    Attributes:
        config_file (str): Path to the configuration file
        config (dict): Loaded configuration settings
        embeddings (OllamaEmbeddings): Embedding model instance
        vector_database (Chroma): Vector database instance
        collection: Chroma collection for document storage
        persist_directory (str): Directory for database persistence

    Example:
        >>> db = DB_Manager(config_file="configs/settings.yml")
        >>> chunks = db.load_and_process_url_content("https://example.com")
        >>> results = db.retrieve("thesis writing guidelines")
    """

    def __init__(
        self,
        config_file: str = "configs/settings.yml",
    ):
        """
        Initialize the Database Manager.

        Args:
            config_file (str, optional): Path to configuration file.
                                       Defaults to "configs/settings.yml".
            persist_directory (str, optional): Database persistence directory.
                                             Defaults to PERSIST_DIRECTORY.

        Raises:
            FileNotFoundError: If configuration file is not found
            Exception: If database setup fails
        """
        self.config_file = config_file
        self.config = self.load_config()
        self.embeddings = None
        self.vector_database = None
        self.collection = None
        self.persist_directory = self.config["database"]["persist_directory"]
        self.setup_vector_database()

    def setup_vector_database(self):
        """
        Set up the vector database components.

        This method initializes:
        1. Persistence directory creation
        2. Ollama embeddings with CPU device configuration
        3. Chroma vector database instance
        4. Document collection setup

        The method ensures all components are properly configured and ready
        for document storage and retrieval operations.

        Side Effects:
        - Creates persistence directory if it doesn't exist
        - Initializes embeddings model on CPU device
        - Creates or connects to Chroma database
        - Sets up document collection
        """
        logger.debug("Setup Database.")
        if not os.path.exists(self.persist_directory):
            os.makedirs(self.persist_directory)
        if self.embeddings is None:
            # device = torch.device("cpu")
            # logger.debug(f"Device: {device}")
            # logger.debug(f'device.hasattr(to): {hasattr(self.embeddings, "to")}')
            self.embeddings = OllamaEmbeddings(
                model=self.config["database"]["ollama_embeddings_model"]
            )
            # if hasattr(self.embeddings, "to") and callable(self.embeddings.to):
            #     self.embeddings.to(device)
            #     logger.debug(f"Embeddings moved to {device}")
            logger.debug(f"Embeddings:{self.embeddings}")
        if self.vector_database is None:
            self.vector_database = Chroma(
                collection_name=self.config["database"]["collection_name"],
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
            )
        logger.debug(f"Vector database:{self.vector_database}")
        if self.collection is None:
            self.collection = self.vector_database._client.get_or_create_collection(
                self.config["database"]["collection_name"]
            )
        logger.debug(f"Collection:{self.collection}")

    def load_config(self):
        """
        Load configuration from YAML file.

        Returns:
            dict: Configuration dictionary loaded from YAML file

        Raises:
            FileNotFoundError: If configuration file doesn't exist
            yaml.YAMLError: If YAML parsing fails

        Example:
            >>> config = db.load_config()
            >>> tags_to_remove = config["source_loader"]["tags_by_name"]
        """
        try:
            with open(self.config_file, "r") as file:
                config = yaml.safe_load(file)
            logger.debug("Configuration loaded successfully.")
            return config
        except FileNotFoundError as fnf:
            logger.error(f"Configuration file {self.config_file} not found.")
            raise fnf

    def read_pdf(self, data: bytes) -> List[Dict]:
        """
        Extract text and metadata from PDF documents.

        This method processes PDF binary data and converts it to markdown format
        with page-based chunking. It extracts both text content and metadata
        for each page, making the content suitable for vector database storage.

        Args:
            data (bytes): Binary content of the PDF file

        Returns:
            List[Dict]: List of dictionaries containing text and metadata
                       Format: [{"text": "...", "metadata": {...}}, ...]

        Raises:
            ValueError: If PDF processing fails or no content is extracted
            Exception: For other PDF processing errors

        Example:
            >>> with open("thesis_guide.pdf", "rb") as f:
            ...     pdf_data = f.read()
            >>> chunks = db.read_pdf(pdf_data)
            >>> for chunk in chunks:
            ...     print(f"Page: {chunk['metadata']['page']}")
            ...     print(f"Content: {chunk['text'][:100]}...")
        """
        try:
            doc = pymupdf.Document(stream=data)
            md_text = pymupdf4llm.to_markdown(
                doc,
                page_chunks=True,
                image_format="png",
                image_path="images",
                embed_images=True,
                write_images=True,
                extract_words=False,
            )
            if not md_text or not isinstance(md_text, list):
                raise ValueError("PDF processing failed: No content extracted.")
            return md_text
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            raise e

    def clean_html(self, response: requests.Response, url: str) -> str:
        """
        Clean HTML content by removing unwanted elements.

        This method processes HTML responses to extract clean text content
        suitable for vector database storage. It removes specified HTML tags
        and elements based on configuration settings.

        Args:
            response (requests.Response): HTTP response containing HTML content
            url (str): Source URL for logging purposes

        Returns:
            str: Cleaned text content with normalized whitespace

        The cleaning process:
        1. Parses HTML with BeautifulSoup
        2. Removes tags specified in configuration
        3. Removes elements by class name
        4. Extracts and normalizes text content
        5. Performs memory cleanup

        Example:
            >>> response = requests.get("https://example.com/thesis-guide")
            >>> clean_text = db.clean_html(response, response.url)
            >>> print(f"Cleaned content length: {len(clean_text)}")
        """
        tags_by_name = self.config["source_loader"]["tags_by_name"]
        tags_by_classname = self.config["source_loader"]["tags_by_classname"]
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(tags_by_name):
            try:
                tag.decompose()
            except Exception as e:
                logger.debug(f"Error removing tag {tag}: {e} @ {url}")
        for tag, class_list in tags_by_classname.items():
            for class_name in class_list:
                try:
                    element = soup.find(tag, class_=class_name)
                    if element:
                        element.decompose()
                except Exception as e:
                    logger.debug(
                        f"Error removing tag {tag} class {class_name}: {e} @ {url}"
                    )
        cleared_text = re.sub(r"\n+", "\n", re.sub(r" +", " ", soup.get_text()))
        logger.debug(f"Web page from [{url}] cleaned successfully.")
        del soup
        gc.collect()
        return cleared_text

    def chunk_sources(self, s: str) -> List[str]:
        """
        Split text content into manageable chunks for processing.

        This method uses SentenceTransformersTokenTextSplitter to divide
        large text content into smaller, overlapping chunks suitable for
        embedding and vector database storage.

        Args:
            s (str): Input text to be chunked

        Returns:
            List[str]: List of text chunks with specified overlap

        Raises:
            Exception: If text splitting fails

        The chunking strategy:
        - Uses sentence-aware splitting
        - Maintains semantic coherence
        - Includes overlap between chunks for context preservation

        Example:
            >>> long_text = "This is a very long document about thesis writing..."
            >>> chunks = db.chunk_sources(long_text)
            >>> print(f"Created {len(chunks)} chunks")
            >>> for i, chunk in enumerate(chunks[:3]):
            ...     print(f"Chunk {i}: {chunk[:50]}...")
        """
        text_splitter = SentenceTransformersTokenTextSplitter(
            chunk_size=self.config["database"]["chunk_size"],
            chunk_overlap=self.config["database"]["chunk_overlap"],
        )
        try:
            chunks = text_splitter.split_text(s)
            return chunks if chunks else []
        except Exception as e:
            logger.error(f"Chunking error: {e}")
            raise e

    def clean_metadata(self, metadata: dict) -> dict:
        """
        Clean and normalize metadata dictionary.

        Args:
            metadata (dict): Raw metadata dictionary

        Returns:
            dict: Cleaned metadata with None values replaced by empty strings

        Example:
            >>> raw_meta = {"title": "Thesis Guide", "author": None, "page": 1}
            >>> clean_meta = db.clean_metadata(raw_meta)
            >>> print(clean_meta)  # {"title": "Thesis Guide", "author": "", "page": 1}
        """
        return {
            key: (value if value is not None else "") for key, value in metadata.items()
        }

    def load_and_process_url_content(self, url: str) -> List[str]:
        """
        Load and process content from a URL for vector database storage.

        This method handles the complete pipeline for processing web content:
        1. Fetches content via HTTP request
        2. Determines content type (PDF or HTML)
        3. Processes content appropriately
        4. Chunks the content for embedding
        5. Creates embeddings and stores in vector database

        Args:
            url (str): URL to fetch and process

        Returns:
            List[str]: List of processed text chunks

        Raises:
            Exception: If content type is unsupported
            Exception: If no chunks are generated
            sqlite3.OperationalError: If database operation fails

        Supported content types:
        - application/pdf: Processed with PyMuPDF
        - text/html: Cleaned with BeautifulSoup

        Example:
            >>> chunks = db.load_and_process_url_content(
            ...     "https://help.jamk.fi/thesis-guide"
            ... )
            >>> print(f"Processed {len(chunks)} chunks from URL")
        """
        if not self.config:
            self.config = self.load_config()
        with requests.get(url, timeout=30) as response:
            content_type = response.headers.get("Content-Type", "")
            if content_type == "application/pdf":
                md_text = self.read_pdf(response.content)
                chunks = [chunk["text"] for chunk in md_text if "text" in chunk]
                if not chunks:
                    logger.warning(f"No text extracted from PDF: {url}")
                    raise Exception("No chunks")
                metadatas = [doc["metadata"] for doc in md_text if "metadata" in doc]
                for i in range(len(metadatas)):
                    metadatas[i] = self.clean_metadata(metadatas[i])
                    metadatas[i]["source"] = str(url)
                logger.debug(f"Metadata copied and cleaned successfully for {url}")
            elif content_type.startswith("text/html"):
                cleared_text = self.clean_html(response, url)
                chunks = self.chunk_sources(cleared_text)
                metadatas = [{"source": str(url)} for _ in range(len(chunks))]
                logger.debug(f"Metadata created successfully for {url}")
            else:
                logger.critical(f"Unhandled content type: {content_type} @ {url}")
                raise Exception(
                    f"Reader for content type ['{content_type}'] not defined."
                )

            if not chunks:
                logger.warning(f"No chunks to process for {url}")
                raise Exception("No chunks")

            for i in range(len(metadatas)):
                metadatas[i]["content-type"] = content_type
            embedded = self.embeddings.embed_documents(chunks)
            ids = [str(url) + "-" + str(i) for i in range(len(chunks))]
            try:
                self.collection.add(
                    ids=ids, embeddings=embedded, documents=chunks, metadatas=metadatas
                )
            except (sqlite3.OperationalError, Exception) as e:
                logger.error(f"Error adding to collection: {e}")
                raise e

            return chunks

    def retrieve(self, query: str) -> List[langchain_core.documents.base.Document]:
        """
        Retrieve relevant documents based on similarity search.

        This method performs semantic similarity search in the vector database
        to find documents most relevant to the given query. It returns both
        the documents and their similarity scores.

        Args:
            query (str): Search query for document retrieval

        Returns:
            List[langchain_core.documents.base.Document]: List of tuples containing
                (Document, similarity_score) pairs, ordered by relevance

        The retrieval process:
        1. Converts query to embedding vector
        2. Performs similarity search in vector database
        3. Returns top-k most similar documents with scores
        4. Logs retrieval statistics for monitoring

        Example:
            >>> results = db.retrieve("How to write thesis introduction?")
            >>> for doc, score in results:
            ...     print(f"Score: {score:.4f}")
            ...     print(f"Source: {doc.metadata.get('source', 'Unknown')}")
            ...     print(f"Content: {doc.page_content[:100]}...")
            ...     print("---")
        """
        logger.debug(f"{self}.retrieve({query})")
        docs = self.vector_database.similarity_search_with_score(
            query, k=self.config["database"]["default_k"]
        )
        logger.debug(f"Found {len(docs)} documents with query:{query}")
        return docs

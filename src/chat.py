"""
RAG Chat Module for Thesis Guidance

This module implements a Retrieval-Augmented Generation (RAG) chat system
specifically designed for thesis guidance. It extends LangChain's ChatOllama
to provide document-grounded responses that strictly adhere to provided context.

The RAG_Chat class ensures that responses are based solely on the provided
documents, preventing hallucination and maintaining accuracy in thesis guidance.

Key Features:
- Strict adherence to provided document context
- Comprehensive prompt engineering to prevent hallucination
- Integration with Ollama LLM framework
- Structured logging for debugging and monitoring
- Configurable model selection and prompt templates

Example:
    Basic usage:
        from chat import RAG_Chat

        rag_chat = RAG_Chat(model="llama3.2:latest")
        documents = ["Thesis should have clear structure...", "Citations are required..."]
        question = "How should I structure my thesis?"
        response = rag_chat.chat(documents, question)
        print(response.content)

Author: Jukka Veijanen
"""

from langchain_ollama import ChatOllama
from tg_logger import setup_logger
import yaml
import os

logger = setup_logger()
print(f"Logger set up: {logger.name}")


def load_config(config_file="configs/settings.yml"):
    """
    Load chat configuration from YAML file.

    Args:
        config_file (str): Path to configuration file

    Returns:
        dict: Chat configuration dictionary

    Raises:
        FileNotFoundError: If configuration file doesn't exist
        yaml.YAMLError: If configuration file is invalid
    """
    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        # chat_config = config.get("chat", {})
        logger.debug(f"Configuration loaded from {config_file}")
        return config
    except FileNotFoundError:
        logger.warning(f"Configuration file not found: {config_file}, using defaults")
        return {}
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML configuration: {e}, using defaults")
        return {}


# Load configuration
config = load_config()

# Extract configuration values with fallbacks
CHAT_MODEL = config["models"]["default_model"]

# Chat configuration
_chat_config = config.get("chat", {})
DEFAULT_TEMPERATURE = _chat_config.get("temperature", 0.0)
DEFAULT_BASE_URL = _chat_config.get("base_url", "http://localhost:11434")
PROMPT_TEMPLATE = _chat_config.get("prompt_template")

NO_INFO_RESPONSE = _chat_config.get(
    "no_info_response",
    "I do not have enough information to answer this question based on the provided sources.",
)

# Logging configuration
_logging_config = _chat_config.get("logging", {})
LOG_PROMPT_LENGTH = _logging_config.get("log_prompt_length", True)
LOG_MODEL_INFO = _logging_config.get("log_model_info", True)
LOG_INPUT_PARAMS = _logging_config.get("log_input_params", True)


class RAG_Chat(ChatOllama):
    """
    Retrieval-Augmented Generation Chat for Thesis Guidance.

    This class extends ChatOllama to provide a specialized chat interface
    for thesis guidance that strictly uses provided documents as context.
    It implements comprehensive prompt engineering to ensure responses
    are grounded in the provided documentation.

    Attributes:
        model (str): The Ollama model name to use for chat
        _prompt_template (str): Internal prompt template for RAG responses

    Example:
        >>> rag_chat = RAG_Chat(model="llama3.2:latest")
        >>> docs = ["Thesis introduction should be 2-3 pages..."]
        >>> question = "How long should my introduction be?"
        >>> response = rag_chat.chat(docs, question)
        >>> print(response.content)
    """

    def __init__(self, model=None, **kwargs):
        """
        Initialize the RAG Chat instance.

        Args:
            model (str, optional): Ollama model name. Defaults to configured default.
            **kwargs: Additional arguments passed to ChatOllama parent class.
                     Common options include temperature, base_url, etc.

        Example:
            >>> rag_chat = RAG_Chat(
            ...     model="llama3.2:latest",
            ...     temperature=0.0,
            ...     base_url="http://localhost:11434"
            ... )
        """
        # Use configured defaults if not provided
        if model is None:
            model = CHAT_MODEL
        if "temperature" not in kwargs:
            kwargs["temperature"] = DEFAULT_TEMPERATURE
        if "base_url" not in kwargs:
            kwargs["base_url"] = DEFAULT_BASE_URL

        super().__init__(model=model, **kwargs)

        # Store prompt template as private attribute to avoid Pydantic validation
        object.__setattr__(self, "_prompt_template", PROMPT_TEMPLATE)

    @property
    def prompt_template(self):
        """Get the current prompt template."""
        return getattr(self, "_prompt_template", PROMPT_TEMPLATE)

    @prompt_template.setter
    def prompt_template(self, value):
        """Set the prompt template."""
        object.__setattr__(self, "_prompt_template", value)

    def chat(self, content, question):
        """
        Generate a response based on provided documents and user question.

        This method implements strict RAG principles by:
        1. Using only the provided documents as context
        2. Explicitly instructing the model to avoid hallucination
        3. Providing clear guidelines for response generation
        4. Logging the interaction for debugging purposes

        Args:
            content (list[str] or str): Document content to use as context.
                                      Can be a list of document strings or single string.
            question (str): User's question about the thesis guidance topic.

        Returns:
            AIMessage: LangChain response object containing:
                - content: The generated response text
                - response_metadata: Model metadata and statistics

        Example:
            >>> documents = [
            ...     "A thesis introduction should provide background...",
            ...     "The introduction typically spans 2-3 pages..."
            ... ]
            >>> question = "How should I write my thesis introduction?"
            >>> response = rag_chat.chat(documents, question)
            >>> print(f"Response: {response.content}")
            >>> print(f"Metadata: {response.response_metadata}")

        Note:
            The method uses a configurable prompt template that includes multiple
            instructions to prevent the model from using external knowledge
            or generating information not present in the provided documents.
        """
        if LOG_INPUT_PARAMS:
            logger.debug(f"chat(len:{len(content)}, {question})")
        if LOG_MODEL_INFO:
            logger.debug(f"Model:{self.model}")

        # Format the prompt using the configurable template
        prompt = self.prompt_template.format(content=content, question=question)

        if LOG_PROMPT_LENGTH:
            logger.debug(f"PROMPT length: {len(prompt)}")

        response = self.invoke(prompt)
        return response

    # def update_prompt_template(self, new_template):
    #     """
    #     Update the prompt template for this instance.

    #     Args:
    #         new_template (str): New prompt template with {content} and {question} placeholders

    #     Example:
    #         >>> rag_chat.update_prompt_template("Custom prompt: {content} Question: {question}")
    #     """
    #     self.prompt_template = new_template
    #     logger.info("Prompt template updated")

    # def get_default_response(self):
    #     """
    #     Get the configured default response for when no information is available.

    #     Returns:
    #         str: Default "no information" response
    #     """
    #     return NO_INFO_RESPONSE

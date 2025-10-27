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
- Configurable model selection

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

logger = setup_logger()
print(f"Logger set up: {logger.name}")

CHAT_MODEL = "gemma3:latest"


class RAG_Chat(ChatOllama):
    """
    Retrieval-Augmented Generation Chat for Thesis Guidance.

    This class extends ChatOllama to provide a specialized chat interface
    for thesis guidance that strictly uses provided documents as context.
    It implements comprehensive prompt engineering to ensure responses
    are grounded in the provided documentation.

    Attributes:
        model (str): The Ollama model name to use for chat

    Example:
        >>> rag_chat = RAG_Chat(model="llama3.2:latest")
        >>> docs = ["Thesis introduction should be 2-3 pages..."]
        >>> question = "How long should my introduction be?"
        >>> response = rag_chat.chat(docs, question)
        >>> print(response.content)
    """

    def __init__(self, model=CHAT_MODEL, **kwargs):
        """
        Initialize the RAG Chat instance.

        Args:
            model (str, optional): Ollama model name. Defaults to CHAT_MODEL.
            **kwargs: Additional arguments passed to ChatOllama parent class.

        Example:
            >>> rag_chat = RAG_Chat(
            ...     model="llama3.2:latest",
            ...     temperature=0.0,
            ...     base_url="http://localhost:11434"
            ... )
        """
        super().__init__(model=model, **kwargs)

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
            The method uses a carefully crafted prompt that includes multiple
            instructions to prevent the model from using external knowledge
            or generating information not present in the provided documents.
        """
        logger.debug(f"chat(len:{len(content)}, {question})")
        logger.debug(f"Model:{self.model}")

        PROMPT = f"""
        Answer the question only using the provided Documents.
        Your tasks are to follow these instructions:
            Use ONLY the provided Documents. If the information is not available, respond with: "I do not have enough information to answer this question based on the provided sources."
            DO NOT invent, assume, or infer information.
            DO NOT use your internal knowledge.
            DO NOT answer with any general information.
            DO NOT add any best practices OUTSIDE of provided Documents.
            DO NOT answer OUTSIDE of question topic.
            DO NOT answer OUTSIDE of provided Documents.
            Use example(s) from Documents only and EXACTLY as it is written in Documents if applicable.
            Answer the question concisely and shortly.
            
        Documents: {content}
        Question: {question}
        Answer:"""
        logger.debug(f"PROMPT length: {len(PROMPT)}")
        response = self.invoke(PROMPT)
        return response

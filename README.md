# Thesis Guidance Chat Application

> **Proof of Concept**: A Retrieval-Augmented Generation (RAG) system for providing AI-powered thesis guidance based on JAMK University's official documentation.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🎯 Overview

**This is a Proof of Concept (PoC)** demonstrating a RAG-based thesis guidance system.

The Thesis Guidance Chat Application helps students with thesis writing by providing accurate, document-grounded responses based on JAMK University's official thesis guidance materials. The system uses RAG (Retrieval-Augmented Generation) to ensure all responses are strictly based on loaded documents, preventing hallucination and maintaining academic accuracy.

### PoC Status

This project serves as a proof of concept to demonstrate:
- Feasibility of RAG for academic guidance
- Integration of local LLM models with document retrieval
- Effectiveness of vector-based semantic search for thesis documentation
- User experience patterns for educational AI assistants

### Key Features

- 🔍 **Semantic Document Retrieval** - Vector-based similarity search using Chroma DB
- 🤖 **RAG Chat Interface** - Context-aware responses using local LLM models
- 📚 **Multi-Source Loading** - Automatic scraping and processing of JAMK web pages and PDFs
- 💾 **Persistent Storage** - Vector database and CSV-based chat history
- 🎨 **User-Friendly UI** - Streamlit-based web interface
- ⚙️ **Configurable** - YAML-based configuration for easy customization

## 🚀 Quick Start

### Prerequisites

- Python 3.12 or higher
- [Ollama](https://ollama.ai/) installed and running
- Required Ollama models:
  ```bash
  ollama pull llama3.2:latest
  ollama pull mxbai-embed-large
  ```

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/jv-mt/rag_chat.git
cd rag_chat

# 2. Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 4. Install dependencies
uv pip install -r requirements.txt

# 5. Verify Ollama is running
curl http://localhost:11434/api/tags
```

### Running the Application

```bash
streamlit run src/app.py
```

The application will open in your browser at `http://localhost:8501`.

### First-Time Setup

1. Navigate to the **Load** tab
2. Click **Submit** to load JAMK thesis guidance documents (~5-10 minutes)
3. Once loaded, go to the **Retrieve** tab to start asking questions

## 📖 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[User Guide](docs/USER_GUIDE.md)** - How to use the application
- **[Architecture Guide](docs/ARCHITECTURE.md)** - System design and component interactions
- **[API Reference](docs/API.md)** - Complete API documentation
- **[Configuration Guide](docs/CONFIGURATION.md)** - Configuration options
- **[Development Guide](docs/DEVELOPMENT.md)** - Setup for contributors
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment instructions

## 🏗️ Architecture

The application follows a 3-tier architecture with clear separation of concerns. See [Architecture Guide](docs/ARCHITECTURE.md) for detailed information.

## 📁 Project Structure

```
rag_chat/
├── src/                      # Source code
│   ├── app.py               # Streamlit web interface
│   ├── chat.py              # RAG chat implementation
│   ├── db_manager.py        # Vector database manager
│   └── tg_logger.py         # Logging configuration
├── configs/                  # Configuration files
│   ├── settings.yml         # Application settings
│   └── logger_config.yml    # Logging configuration
├── docs/                     # Documentation
│   ├── README.md            # Documentation index
│   ├── ARCHITECTURE.md      # Architecture guide
│   ├── API.md               # API reference
│   ├── CONFIGURATION.md     # Configuration guide
│   ├── USER_GUIDE.md        # User guide
│   ├── DEVELOPMENT.md       # Development guide
│   └── DEPLOYMENT.md        # Deployment guide
├── chroma_db/               # Vector database storage (gitignored)
├── chat_session_records/    # Chat history CSV files (gitignored)
├── logs/                    # Application logs (gitignored)
└── requirements.txt         # Python dependencies
```

## 🔧 Configuration

All configuration is centralized in `configs/settings.yml`. See [Configuration Guide](docs/CONFIGURATION.md) for all options.

## 💡 Usage Examples

### Asking Questions

```
Question: How long should a bachelor's thesis introduction be?

Response: According to the JAMK thesis guidelines, a bachelor's 
thesis introduction should typically be 2-3 pages...
```

See [User Guide](docs/USER_GUIDE.md) for more examples.

## ⚠️ PoC Limitations

As a proof of concept, this application has the following limitations:

- **Scale**: Designed for demonstration with ~40 JAMK documents, not tested at large scale
- **Performance**: Not optimized for high-concurrency or production workloads
- **Security**: Basic implementation without authentication, authorization, or audit logging
- **Error Handling**: Simplified error handling suitable for demonstration purposes
- **Testing**: Limited test coverage (PoC focuses on functionality demonstration)
- **Monitoring**: Basic logging without comprehensive monitoring or alerting
- **Data Privacy**: No data encryption or privacy controls implemented

For production deployment, these areas would require significant enhancement.

## 🤝 Contributing

Contributions are welcome! Please see our [Development Guide](docs/DEVELOPMENT.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **JAMK University of Applied Sciences** for thesis guidance documentation
- **LangChain** for RAG framework
- **Ollama** for local LLM inference
- **Chroma** for vector database

## 📞 Support

- 📖 [User Guide](docs/USER_GUIDE.md)
- �� [Issue Tracker](https://github.com/jv-mt/rag_chat/issues)

---

**Status**: Proof of Concept
**Author**: Jukka Veijanen
**Version**: 1.0.0-PoC
**Last Updated**: 2025-10-29

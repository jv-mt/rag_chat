# Configuration Guide

This guide explains all configuration options available in the Thesis Guidance Chat Application.

## Table of Contents

- [Overview](#overview)
- [Configuration File Structure](#configuration-file-structure)
- [Database Configuration](#database-configuration)
- [Application Configuration](#application-configuration)
- [Model Configuration](#model-configuration)
- [Data Sources Configuration](#data-sources-configuration)
- [Network Configuration](#network-configuration)
- [Source Loader Configuration](#source-loader-configuration)
- [Storage Configuration](#storage-configuration)
- [UI Configuration](#ui-configuration)
- [Chat Configuration](#chat-configuration)
- [Environment-Specific Configurations](#environment-specific-configurations)

## Overview

All application configuration is centralized in `configs/settings.yml`. This YAML file controls:

- Vector database settings
- LLM model selection
- Data source URLs
- UI behavior and messages
- RAG prompt templates
- Logging preferences

**Configuration File**: `configs/settings.yml`

## Configuration File Structure

```yaml
database:          # Vector database settings
app:              # Streamlit application settings
models:           # LLM model configuration
data_sources:     # URLs to load
network:          # HTTP request settings
source_loader:    # HTML cleaning rules
storage:          # File storage paths
ui:               # UI messages and display
chat:             # RAG chat settings
```

## Database Configuration

Controls vector database behavior and document processing.

```yaml
database:
  persist_directory: "./chroma_db"
  collection_name: "docs"
  ollama_embeddings_model: "mxbai-embed-large"
  chunk_size: 256
  chunk_overlap: 50
  default_k: 3
  type: "chroma"
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `persist_directory` | string | `"./chroma_db"` | Directory for vector database storage |
| `collection_name` | string | `"docs"` | Chroma collection name |
| `ollama_embeddings_model` | string | `"mxbai-embed-large"` | Ollama embedding model |
| `chunk_size` | integer | `256` | Maximum tokens per chunk |
| `chunk_overlap` | integer | `50` | Overlapping tokens between chunks |
| `default_k` | integer | `3` | Number of documents to retrieve |
| `type` | string | `"chroma"` | Vector database type |

### Tuning Guidelines

**Chunk Size**:
- **Smaller (128-256)**: Better precision, more chunks, slower loading
- **Larger (512-1024)**: More context per chunk, fewer chunks, faster loading
- **Recommended**: 256 for balanced performance

**Chunk Overlap**:
- **Purpose**: Prevents context loss at chunk boundaries
- **Range**: 10-20% of chunk_size
- **Recommended**: 50 tokens for 256 chunk_size

**Default K**:
- **Smaller (1-3)**: More focused responses, less context
- **Larger (5-10)**: More comprehensive responses, potential noise
- **Recommended**: 3 for thesis guidance

### Embedding Models

Available Ollama embedding models:

| Model | Dimensions | Performance | Use Case |
|-------|-----------|-------------|----------|
| `mxbai-embed-large` | 1024 | High quality | **Recommended** |
| `nomic-embed-text` | 768 | Fast | Quick testing |
| `all-minilm` | 384 | Very fast | Development |

**Installation**:
```bash
ollama pull mxbai-embed-large
```

## Application Configuration

Controls Streamlit application behavior.

```yaml
app:
  title: "Web UI with Loader and Retriever"
  layout: "wide"
  sidebar_state: "expanded"
```

### Parameters

| Parameter | Type | Options | Description |
|-----------|------|---------|-------------|
| `title` | string | Any | Browser tab title |
| `layout` | string | `"wide"`, `"centered"` | Page layout mode |
| `sidebar_state` | string | `"expanded"`, `"collapsed"`, `"auto"` | Initial sidebar state |

## Model Configuration

Defines available LLM models and default selection.

```yaml
models:
  available_models:
    - "llama3.2:latest"
    - "phi3:latest"
    - "qwen3:4b"
  default_model: "llama3.2:latest"
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `available_models` | list | Models shown in UI dropdown |
| `default_model` | string | Pre-selected model on startup |

### Supported Models

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| `llama3.2:latest` | ~2GB | Medium | High | **Production** |
| `phi3:latest` | ~2.2GB | Fast | Good | Quick responses |
| `qwen3:4b` | ~2.6GB | Fast | Good | Alternative option |

**Installation**:
```bash
ollama pull llama3.2:latest
ollama pull phi3:latest
ollama pull qwen3:4b
```

**Adding Custom Models**:
```yaml
models:
  available_models:
    - "llama3.2:latest"
    - "mistral:latest"      # Add new model
    - "custom-model:v1"     # Custom fine-tuned model
  default_model: "llama3.2:latest"
```

## Data Sources Configuration

Specifies URLs to load for thesis guidance content.

```yaml
data_sources:
  urls:
    - "https://help.jamk.fi/opinnaytetyo/en/thesis/bachelors-thesis/"
    - "https://help.jamk.fi/opinnaytetyo/en/thesis/masters-thesis/"
    # ... more URLs
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `urls` | list | List of URLs to process |

### Supported Content Types

- **HTML Pages**: `text/html`
- **PDF Documents**: `application/pdf`

### Adding New Sources

```yaml
data_sources:
  urls:
    # Existing JAMK URLs
    - "https://help.jamk.fi/opinnaytetyo/en/thesis/bachelors-thesis/"
    
    # Add new sources
    - "https://example.com/additional-guide.pdf"
    - "https://example.com/thesis-templates/"
```

## Network Configuration

Controls HTTP request behavior.

```yaml
network:
  request_timeout: 30
  max_retries: 3
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `request_timeout` | integer | `30` | HTTP request timeout (seconds) |
| `max_retries` | integer | `3` | Maximum retry attempts |

## Source Loader Configuration

Defines HTML cleaning rules for web scraping.

```yaml
source_loader:
  tags_by_name:
    - style
    - script
    - dialog
    - header
    - footer
    - aside
    - meta
    - title
  
  tags_by_classname:
    a:
      - button-primary-icon
      - link-list lock
    div:
      - breadcrumb-item
      - mobile-menu
    nav:
      - nav-primary
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `tags_by_name` | list | HTML tags to remove by name |
| `tags_by_classname` | dict | Tags to remove by class name |

### Customization

**Remove Additional Tags**:
```yaml
source_loader:
  tags_by_name:
    - style
    - script
    - advertisement  # Add custom tag
```

**Remove by Class**:
```yaml
source_loader:
  tags_by_classname:
    div:
      - breadcrumb-item
      - custom-sidebar    # Add custom class
      - popup-overlay
```

## Storage Configuration

Defines file storage locations.

```yaml
storage:
  results_directory: "chat_session_records"
  results_filename: "chat_results.csv"
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `results_directory` | string | `"chat_session_records"` | Directory for CSV storage |
| `results_filename` | string | `"chat_results.csv"` | CSV filename |

## UI Configuration

Controls UI messages and display behavior.

```yaml
ui:
  progress_display:
    max_lines: 6
    operation_text: "Operation in progress"
  
  messages:
    load_success: "URLs loaded and stored into vector database successfully!"
    no_documents: "No documents found."
    db_not_initialized: "Vector database collection not initialized. Please load data first."
    results_stored: "Chat results stored to"
    no_results: "No results stored yet."
```

### Parameters

**Progress Display**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_lines` | integer | `6` | Max URLs shown during loading |
| `operation_text` | string | `"Operation in progress"` | Progress bar text |

**Messages**:
Customize all user-facing messages for internationalization or branding.

### Internationalization Example

```yaml
ui:
  messages:
    load_success: "Dokumentit ladattu onnistuneesti!"  # Finnish
    no_documents: "Dokumentteja ei löytynyt."
    # ... other messages in Finnish
```

## Chat Configuration

Controls RAG chat behavior and prompt engineering.

```yaml
chat:
  temperature: 0.0
  base_url: "http://localhost:11434"
  
  prompt_template: |
    Answer the question only using the provided Documents.
    Your tasks are to follow these instructions:
        Use ONLY the provided Documents...
        DO NOT invent, assume, or infer information...
    
    Documents: {content}
    Question: {question}
    Answer:
  
  no_info_response: "I do not have enough information to answer this question based on the provided sources."
  
  logging:
    log_prompt_length: true
    log_model_info: true
    log_input_params: true
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `temperature` | float | `0.0` | LLM sampling temperature (0.0-1.0) |
| `base_url` | string | `"http://localhost:11434"` | Ollama API endpoint |
| `prompt_template` | string | See config | RAG prompt template |
| `no_info_response` | string | See config | Fallback response |

### Temperature Settings

| Value | Behavior | Use Case |
|-------|----------|----------|
| `0.0` | Deterministic, focused | **Production (recommended)** |
| `0.3` | Slightly creative | Exploratory responses |
| `0.7` | More creative | Brainstorming |
| `1.0` | Very creative | Not recommended for RAG |

### Prompt Template Customization

The prompt template supports two placeholders:
- `{content}`: Retrieved documents
- `{question}`: User's question

**Example - Concise Responses**:
```yaml
chat:
  prompt_template: |
    Based on these documents: {content}
    
    Answer this question in 2-3 sentences: {question}
    
    Answer:
```

**Example - Structured Responses**:
```yaml
chat:
  prompt_template: |
    Documents: {content}
    
    Question: {question}
    
    Provide your answer in this format:
    1. Direct Answer: [answer]
    2. Source Reference: [which document]
    3. Additional Context: [if applicable]
```

### Logging Configuration

```yaml
chat:
  logging:
    log_prompt_length: true   # Log prompt character count
    log_model_info: true      # Log model name and settings
    log_input_params: true    # Log input parameters
```

## Environment-Specific Configurations

### Development Configuration

```yaml
# configs/settings.dev.yml
database:
  chunk_size: 128           # Smaller for faster testing
  default_k: 2

models:
  default_model: "phi3:latest"  # Faster model

chat:
  temperature: 0.0
  logging:
    log_prompt_length: true
    log_model_info: true
    log_input_params: true
```

### Production Configuration

```yaml
# configs/settings.prod.yml
database:
  chunk_size: 256
  default_k: 3

models:
  default_model: "llama3.2:latest"  # Best quality

chat:
  temperature: 0.0
  logging:
    log_prompt_length: false
    log_model_info: false
    log_input_params: false
```

### Loading Environment-Specific Config

Modify `src/app.py` and `src/db_manager.py`:

```python
import os

# Determine environment
env = os.getenv("APP_ENV", "dev")
config_file = f"configs/settings.{env}.yml"

# Load config
config = load_config(config_file)
```

## Configuration Validation

### Required Fields

The application requires these minimum fields:

```yaml
database:
  persist_directory: string
  collection_name: string
  ollama_embeddings_model: string

models:
  default_model: string

chat:
  prompt_template: string
```

### Validation Script

Create `scripts/validate_config.py`:

```python
import yaml
import sys

def validate_config(config_file):
    with open(config_file) as f:
        config = yaml.safe_load(f)
    
    required = [
        "database.persist_directory",
        "database.collection_name",
        "models.default_model",
        "chat.prompt_template"
    ]
    
    for field in required:
        keys = field.split(".")
        value = config
        for key in keys:
            value = value.get(key)
            if value is None:
                print(f"❌ Missing required field: {field}")
                sys.exit(1)
    
    print("✅ Configuration valid")

if __name__ == "__main__":
    validate_config("configs/settings.yml")
```

---

**Next Steps**: See [Development Guide](DEVELOPMENT.md) for development setup and best practices.


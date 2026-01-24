# AWR RAG Analysis

A Retrieval-Augmented Generation (RAG) tool for analyzing Oracle AWR (Automatic Workload Repository) reports using LLMs. It supports both a command-line interface (CLI) and a modern Web UI.

## Features

- **Multi-Report Analysis**: Ingest and analyze multiple AWR reports (HTML or Text) to understand performance trends over time.
- **Interactive Mode**: Ask sequential follow-up questions without re-processing the data.
- **Model Selection**: Switch between different LLMs (e.g., Gemma3, Llama3) on the fly.
- **Web UI**: Fast, interactive web interface with Markdown rendering for rich analysis output.
- **Smart CLI**: Automatically scans directories for reports and supports interactive sessions.

## Structure

- `app/`: FASTAPI Web application and CLI entry points.
- `ingestion/`: Parsing logic for AWR HTML/Text files and metadata extraction.
- `embeddings/`: Vector store (Qdrant) and embedding generation.
- `retrieval/`: Query rewriting and context retrieval.
- `reasoning/`: LLM integration (Ollama).
- `utils/`: Configuration and logging.
- `data/`: Directory for storing raw reports and vector data.

## Setup

1.  **Install Dependencies**:
    The project uses a virtual environment `.venv`.
    ```bash
    .venv/bin/pip install -r awr-rag/requirements.txt
    ```

2.  **Configuration**:
    - Manage available models and settings in `awr-rag/utils/config.py`.
    - Ensure your local LLM inference server (e.g., Ollama) is running at the configured URL.

## Usage

### 1. Web UI (Recommended)

Start the web server:
```bash
.venv/bin/python -m app.web
```
- Open **http://localhost:8000** in your browser.
- **Upload**: Select one or multiple AWR files.
- **Chat**: Select your preferred model and start analyzing.
- **Stop**: Click "Stop Server" in the UI when finished.

### 2. Command Line Interface (CLI)

Run the CLI tool. It automatically checks `data/raw` for reports if no files are specified.

**Default (scans `data/raw`):**
```bash
.venv/bin/python -m app.cli
```

**Specific Files or Directory:**
```bash
.venv/bin/python -m app.cli --files path/to/report1.html path/to/report2.html
# OR
.venv/bin/python -m app.cli --files path/to/directory
```

**Interactive Mode:**
After processing, the CLI enters an interactive loop. Type your questions, or `exit`/`quit` to stop.

## Development

- **Adding Models**: Update `AVAILABLE_MODELS` list in `utils/config.py`.
- **Customizing Prompt**: Edit templates in `reasoning/prompts.py`.

## Testing

Run the benchmark script to test ingestion and inference speed:
```bash
.venv/bin/python awr-rag/tests/benchmark.py
```

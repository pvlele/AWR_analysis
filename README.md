# AWR RAG Analysis

A Retrieval-Augmented Generation (RAG) tool for analyzing Oracle AWR (Automatic Workload Repository) reports using LLMs. It supports both a command-line interface (CLI) and a modern Web UI.

## Features

- **Multi-Report Analysis**: Ingest and analyze multiple AWR reports (HTML or Text) to understand performance trends over time.
- **Interactive Mode**: Ask sequential follow-up questions without re-processing the data.
- **Model Selection**: Switch between different LLMs (e.g., Gemma3, Llama3) on the fly.
- **Web UI**: Fast, interactive web interface with Markdown rendering for rich analysis output.
- **Smart CLI**: Automatically scans directories for reports and supports interactive sessions.

## Structure

- **`app/`**: Application entry points. Contains `web.py` for the FastAPI backend and `cli.py` for the command-line interface.
- **`ingestion/`**: Parsers for AWR reports. Handles both HTML (`awr_parser.py`) and text formats, extracting metadata and performance metrics.
- **`embeddings/`**: Management of vector data. Generates embeddings using `SentenceTransformer` and stores them in a local Qdrant vector database.
- **`retrieval/`**: Context retrieval logic. Uses semantic search to find relevant report chunks based on user queries, with optional re-ranking.
- **`reasoning/`**: LLM interaction layer. Manages prompts and communicates with the local inference server (e.g., Ollama) to generate answers.
- **`utils/`**: Shared utilities. Includes configuration management (`config.py`) and logging setup.
- **`data/`**: Storage for raw AWR report files (`raw/`) and the persistent vector database (`qdrant_data/`).

## Setup

1.  **Install Dependencies**:
    The project uses a virtual environment `.venv`.
    ```bash
    .venv/bin/pip install -r requirements.txt
    ```

2.  **Environment Configuration**:
    Create a `.env` file in the `awr-rag` directory with the following variables:
    ```env
    GEMINI_API_KEY=your_gemini_key
    LLM_TOKEN=your_llm_token
    ```

3.  **Application Configuration**:
    - Manage available models, base URL, and other settings in `utils/config.py`.
    - Ensure your local LLM inference server (e.g., Ollama/vLLM) is running at the configured `MODEL_BASE_URL`.

## Usage

### 1. Web UI (Recommended)

Start the web server:
```bash
# Linux/WSL
.venv/bin/python -m app.web

# Windows (PowerShell)
.venv\Scripts\python.exe -m app.web
```
- Open **http://localhost:8088** in your browser.
- **Upload**: Select one or multiple AWR files.
- **Chat**: Select your preferred model and start analyzing.
- **Stop**: Press `Ctrl+C` in the terminal.

### 2. Command Line Interface (CLI)

Run the CLI tool using the helper scripts:

**Linux/WSL:**
```bash
./run_cli.sh
```

**Windows (PowerShell):**
```powershell
.\run_cli.ps1
```

You can also run it directly via Python:
```bash
.venv/bin/python -m app.cli
```

**Analyze Specific Files:**

To analyze specific files instead of scanning the default directory, use the `--files` argument:

*   **Single File:**
    ```bash
    .venv/bin/python -m app.cli --files /path/to/report.html
    ```

*   **Multiple Files:**
    ```bash
    .venv/bin/python -m app.cli --files report1.html report2.txt /path/to/another/report.html
    ```

### 3. Troubleshooting

If you experience connection issues with the LLM, use the check scripts to verify connectivity:

**Linux/WSL:**
```bash
sh check_llm.sh
```

**Windows (PowerShell):**
```powershell
.\check_llm.ps1
```

## Performance Tuning

You can adjust these parameters in `utils/config.py` to optimize for your hardware and data:

### Ingestion
- **`CHUNK_SIZE` (Default: 1500)**: Size of text chunks for embedding. 
    - *Larger*: Fewer chunks, potentially losing detail. Good for broad summaries.
    - *Smaller*: More precision, but increases vector store size and retrieval noise.
- **`CHUNK_OVERLAP` (Default: 150)**: Overlap between chunks to maintain context continuity.

### Retrieval
- **`RETRIEVAL_LIMIT` (Default: 6)**: Number of similar chunks to retrieve.
    - *Higher*: More context for the LLM, but slower and risks hitting context limits.
    - *Lower*: Faster, but might miss relevant details.
- **`QUERIES_PER_SEARCH` (Default: 6)**: Number of search query variations generated. Reduced this if retrieval is too slow.

### Inference
- **`CONTEXT_SIZE` (Default: 4096)**: Maximum tokens the model can handle (Input + Output). Increase for very long reports, but requires more RAM/VRAM.
- **`NUM_PREDICT` (Default: 4096)**: Max tokens for the LLM's response.
- **`NUM_THREADS` (Default: 4)**: CPU threads for local inference (Ollama). Set to physical core count for best performance.

## Development

- **Adding Models**: Update `AVAILABLE_MODELS` list in `utils/config.py`.
- **Customizing Prompt**: Edit templates in `reasoning/prompts.py`.

## Testing

Run the benchmark script to test ingestion and inference speed:
```bash
.venv/bin/python tests/benchmark.py
```

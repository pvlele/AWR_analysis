# awr-rag

Project structure for RAG implementation on AWR data.

## Structure

- `data/`: Contains raw and processed data.
- `ingestion/`: Modules for parsing and chunking data.
- `embeddings/`: Embedding generation and vector store management.
- `retrieval/`: Retrieval logic and query re-writing.
- `reasoning/`: LLM prompting and analysis.
- `evaluation/`: Test cases and metrics for RAG performance.
- `app/`: API and CLI interfaces.
- `utils/`: Helper functions and logging.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables in `.env` (e.g., `OPENAI_API_KEY`).

## Usage

Run the CLI application from the project root:

```bash
python -m app.cli
```

Ensure `data/raw/awr_12345.txt` exists before running.

## Testing & Benchmarks

### 1. Verify Ollama Integration
To check if the local Ollama instance is correctly connected and responding:
```bash
python awr-rag/verify_ollama.py
```
This script runs a simple query ("Why was the database slow?") against mock data.

### 2. Context Window Test
To verify that the LLM can handle large context windows (up to 8192 tokens) and pass parameters correctly:
```bash
python awr-rag/test_ollama_ctx.py
```
This tests both flat and nested parameter structures for Ollama.

### 3. Performance Benchmark
To measure ingestion speed and inference latency across different models:
```bash
python awr-rag/tests/benchmark.py
```
**Note:** This requires `data/raw/awr_report.html` to be present. It benchmarks:
- Ingestion time (Load, Split, Chunk)
- Inference time for configured models (default: `ai/gemma3:4B-Q4_0`, `ai/llama3.1:8B-Q4_K_M`)
- Memory and CPU usage

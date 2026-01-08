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

from dotenv import load_dotenv
load_dotenv()

import argparse
from ingestion.ingest import ingest_awr
from embeddings.embedder import Embedder
from embeddings.vector_store import VectorStore
from retrieval.query_rewriter import rewrite
from retrieval.retriever import Retriever
from reasoning.analyzer import analyze
from utils.logging import setup_logger

logger = setup_logger()

def main():
    parser = argparse.ArgumentParser(description="RAG CLI for AWR Reports")
    parser.add_argument("--file", default="data/raw/awr_report.html", help="Path to the AWR report file")
    parser.add_argument("--question", default="Why was the database slow?", help="The question to ask about the AWR report")
    parser.add_argument("--output", help="Optional path to save processed chunks")
    args = parser.parse_args()

    logger.info(f"Processing file: {args.file}")

    try:
        chunks = ingest_awr(
            args.file,
            metadata={"db": "PROD", "instance": 1},
            output_path=args.output
        )
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        return

    embedder = Embedder()
    store = VectorStore()

    logger.info("Generating embeddings and upserting to vector store...")
    embeddings = embedder.embed([c["text"] for c in chunks])
    store.upsert(embeddings, chunks)

    logger.info(f"Analyzing question: {args.question}")
    queries = rewrite(args.question)

    retriever = Retriever(store)
    results = retriever.retrieve(queries)

    answer = analyze(args.question, results)
    print("\n--- Answer ---")
    print(answer)

if __name__ == "__main__":
    main()

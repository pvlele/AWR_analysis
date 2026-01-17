from dotenv import load_dotenv
load_dotenv()

from ingestion.ingest import ingest_awr
from embeddings.embedder import Embedder
from embeddings.vector_store import VectorStore
from retrieval.query_rewriter import rewrite
from retrieval.retriever import Retriever
from reasoning.analyzer import analyze
from utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    logger.info("Starting AWR Analysis...")
    try:
        chunks = ingest_awr(
            "data/raw/awr_report.html",
            metadata={"db": "PROD", "instance": 1}
        )
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        return

    try:
        embedder = Embedder()
        store = VectorStore()

        logger.info("Generating embeddings...")
        embeddings = embedder.embed([c["text"] for c in chunks])
        store.upsert(embeddings, chunks)
        # Verify collection exists (assuming get_collections returns a list of objects)
        logger.info(f"Qdrant Collections: {store.client.get_collections()}")
    except Exception as e:
        logger.error(f"Embedding/Storage failed: {e}")
        return

    question = "Why was the database slow?"
    queries = rewrite(question)
    logger.info(f"Generated queries: {queries}")

    # Dependency Injection: passing embedder to Retriever
    retriever = Retriever(store, embedder)
    results = retriever.retrieve(queries)
    logger.info(f"Retrieved {len(results)} chunks.")

    answer = analyze(question, results)
    
    save_report(answer)

def save_report(answer):
    # Construct Output with Metadata
    import datetime
    import os
    from utils.config import Config

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    output_content = f"""AWR Analysis Report
===================
Date: {timestamp}
Model: {Config.MODEL_NAME}
Base URL: {Config.MODEL_BASE_URL}

Configuration Settings:
-----------------------
Timeout: {Config.TIMEOUT}
Chunk Size: {Config.CHUNK_SIZE}
Chunk Overlap: {Config.CHUNK_OVERLAP}
Retrieval Limit: {Config.RETRIEVAL_LIMIT}
Queries Per Search: {Config.QUERIES_PER_SEARCH}

Analysis:
---------
{answer}
"""

    # Ensure outputs directory exists
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file_path = os.path.join(output_dir, f"analysis_report_{file_timestamp}.txt")
    
    with open(output_file_path, "w") as f:
        f.write(output_content)

    print("\nanalysis:\n")
    print(answer)
    print(f"\nReport saved to: {output_file_path}")

if __name__ == "__main__":
    main()

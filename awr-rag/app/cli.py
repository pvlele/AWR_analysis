from dotenv import load_dotenv
load_dotenv()

from ingestion.ingest import ingest_awr
from embeddings.embedder import Embedder
from embeddings.vector_store import VectorStore
from retrieval.query_rewriter import rewrite
from retrieval.retriever import Retriever
from reasoning.analyzer import analyze

def main():
    chunks = ingest_awr(
        "data/raw/awr_report.html",
        metadata={"db": "PROD", "instance": 1}
    )

    embedder = Embedder()
    store = VectorStore()

    embeddings = embedder.embed([c["text"] for c in chunks])
    store.upsert(embeddings, chunks)
    print(store.client.get_collections())  # ✅ DEBUG: verify Qdrant is alive

    question = "Why was the database slow?"
    queries = rewrite(question)

    retriever = Retriever(store)
    results = retriever.retrieve(queries)

    answer = analyze(question, results)
    print(answer)

if __name__ == "__main__":
    main()

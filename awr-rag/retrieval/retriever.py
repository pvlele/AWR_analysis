from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class Retriever:
    def __init__(self, store, embedder):
        self.store = store
        self.embedder = embedder
        self.limit = Config.RETRIEVAL_LIMIT

    def retrieve(self, queries):
        results = []
        try:
            vectors = self.embedder.embed(queries)
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            return []

        seen_texts = set()
        for v in vectors:
            try:
                hits = self.store.search(v, limit=Config.QUERIES_PER_SEARCH)
                for hit in hits:
                    text = hit.payload.get("text")
                    if text and text not in seen_texts:
                        results.append(hit)
                        seen_texts.add(text)
            except Exception as e:
                logger.error(f"Vector store search failed: {e}")
                continue
        
        return results[:self.limit]

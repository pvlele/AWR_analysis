from embeddings.embedder import Embedder

class Retriever:
    def __init__(self, store):
        self.embedder = Embedder()
        self.store = store

    def retrieve(self, queries):
        results = []
        vectors = self.embedder.embed(queries)

        seen_texts = set()
        for v in vectors:
            hits = self.store.search(v, limit=3) # Limit per query
            for hit in hits:
                # Assuming hit.payload is a dict and has 'text'
                text = hit.payload.get("text")
                if text and text not in seen_texts:
                    results.append(hit)
                    seen_texts.add(text)
        
        return results[:2] # Hard limit total chunks

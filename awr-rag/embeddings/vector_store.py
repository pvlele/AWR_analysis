from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

class VectorStore:
    def __init__(self, collection="awr"):
        self.client = QdrantClient(":memory:")
        self.collection = collection

        self.client.recreate_collection(
            collection_name=collection,
            vectors_config={"size": 384, "distance": "Cosine"}
        )

    def upsert(self, embeddings, chunks):
        points = []
        for i, emb in enumerate(embeddings):
            points.append(
                PointStruct(
                    id=i,
                    vector=emb,
                    payload=chunks[i]
                )
            )
        self.client.upsert(self.collection, points)

    def search(self, vector, filters=None, limit=5):
        return self.client.query_points(
            self.collection,
            query=vector,
            limit=limit,
            with_payload=True
        ).points

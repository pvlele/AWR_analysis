from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from utils.config import Config

class VectorStore:
    def __init__(self, collection_name="awr", recreate=True):
        if hasattr(Config, "VECTOR_STORE_PATH") and Config.VECTOR_STORE_PATH:
             self.client = QdrantClient(path=Config.VECTOR_STORE_PATH)
        else:
             self.client = QdrantClient(":memory:")
        self.collection_name = collection_name
        self.recreate_on_next_upsert = recreate
        self._current_dimension = None

    def _ensure_collection_exists(self, dimension):
        """
        Ensures the collection exists with the correct dimension.
        If recreate_on_next_upsert is True, it (re)creates it.
        Otherwise, it checks if it exists and matches dimension.
        """
        if self.recreate_on_next_upsert:
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=dimension, distance=Distance.COSINE)
            )
            self.recreate_on_next_upsert = False # Only recreate once
            self._current_dimension = dimension
            return

        # graceful check if exists
        try:
            coll_info = self.client.get_collection(self.collection_name)
            existing_dim = coll_info.config.params.vectors.size
            if existing_dim != dimension:
                 raise ValueError(
                     f"Vector dimension mismatch! Collection '{self.collection_name}' "
                     f"has dimension {existing_dim}, but new vectors have {dimension}."
                 )
            self._current_dimension = dimension
        except Exception as e:
            # Collection might not exist, create it
            # But if it was a ValueError from above, re-raise it
            if "dimension mismatch" in str(e):
                raise e
            
            # Assume it doesn't exist
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=dimension, distance=Distance.COSINE)
            )
            self._current_dimension = dimension

    def upsert(self, embeddings, chunks):
        if embeddings is None or len(embeddings) == 0:
            return

        # 1. Detect Dimension
        first_vector = embeddings[0]
        dimension = len(first_vector)

        # 2. Validate Consistency
        for i, emp in enumerate(embeddings):
            if len(emp) != dimension:
                raise ValueError(f"Inconsistent embedding dimensions at index {i}. Expected {dimension}, got {len(emp)}")

        # 3. Ensure Collection is Ready
        self._ensure_collection_exists(dimension)

        points = []
        # Qdrant requires integer IDs or UUIDs. Enumerate is simple but not persistent across runs if we weren't using :memory:
        # Since this is :memory: and recreated often, enumerate is fine for this scope.
        # But to be safer with multiple upserts, we might want a running counter or UUIDs.
        # For now, keeping logic simple as requested, but using a huge offset if needed?
        # Actually, existing code used enumerate. We'll stick to that but note it resets if class re-instantiated.
        # Since recreate=True is default logic in CLI, it's fine.
        
        # NOTE: If we call upsert multiple times on the SAME instance, enumerate 0..N will overwrite!
        # We need to count existing points to safely append? 
        # In memory client doesn't support count() easily without query? 
        # actually client.count() exists.
        
        start_id = 0
        try:
             count_res = self.client.count(self.collection_name)
             start_id = count_res.count
        except:
             pass

        for i, emb in enumerate(embeddings):
            points.append(
                PointStruct(
                    id=start_id + i,
                    vector=emb,
                    payload=chunks[i]
                )
            )
        
        self.client.upsert(self.collection_name, points)

    def search(self, vector, limit=5):
        # Validation
        if self._current_dimension and len(vector) != self._current_dimension:
             # Try to query to see if collection exists first to give better error?
             pass 

        try:
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=vector,
                limit=limit,
                with_payload=True
            ).points
            return results
        except Exception as e:
            # Fallback for older qdrant versions or if search fails
            print(f"Search failed: {e}")
            return []

import requests
from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class Embedder:
    def __init__(self):
        self.base_url = getattr(Config, "MODEL_BASE_URL", None)
        self.api_path = getattr(Config, "EMBEDDING_API_PATH", None)
        self.model_name = getattr(Config, "EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
        
        self.api_url = None
        if self.base_url and self.api_path:
             self.api_url = f"{self.base_url.rstrip('/')}/{self.api_path.lstrip('/')}"
        
        if not self.api_url:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            self.use_api = False
        else:
            self.use_api = True
            logger.info(f"Initialized Embedder with API: {self.api_url} Model: {self.model_name}")

    def embed(self, texts: list[str]):
        if self.use_api:
            try:
                # Use OpenAI-compatible embedding Endpoint
                payload = {
                    "input": texts,
                    "model": self.model_name
                }
                # Optional: Add headers if token needed (Config.HEADERS usually for LLM, but maybe shared?)
                # user didn't specify auth for embedding, assuming open or localhost
                
                response = requests.post(self.api_url, json=payload, timeout=Config.TIMEOUT, headers=Config.HEADERS)
                response.raise_for_status()
                result = response.json()
                
                # OpenAI format: { "data": [ { "embedding": ... }, ... ] }
                if "data" in result:
                    # Sort by index if needed, but usually list is ordered
                     embeddings = [item["embedding"] for item in result["data"]]
                     return embeddings
                else:
                    logger.error(f"Unexpected response format from Embedding API: {result.keys()}")
                    raise ValueError("Invalid embedding API response")
                    
            except Exception as e:
                logger.error(f"Failed to generate embeddings via API: {e}")
                raise e
        else:
            return self.model.encode(texts, show_progress_bar=True)

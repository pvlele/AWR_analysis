import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Model Settings
    # MODEL_BASE_URL = "http://localhost:11434/api/chat"
    MODEL_BASE_URL = "http://localhost:12435/v1/"
    MODEL_API_PATH = "chat/completions"
    MODEL_NAME = "docker.io/ai/llama3.1:8B-Q4_K_M"
    AVAILABLE_MODELS = [
        "docker.io/ai/llama3.1:8B-Q4_K_M",
        "docker.io/ai/gemma3:4B",
        "docker.io/ai/smollm2:latest"
    ]
    TIMEOUT = 1200
    
    # Embedding Settings
    # Use same base URL as model for simplicity if possible, or define separately
    EMBEDDING_API_PATH = "embeddings" 
    EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
    
    # Context Logic
    CONTEXT_SIZE = 4096
    NUM_PREDICT = 1024
    NUM_THREADS = 4
    
    # Request Headers
    HEADERS = {
        "Authorization": f"Bearer {os.getenv('TOKEN', '')}",
        "Content-Type": "application/json"
    }

    # Ingestion Settings
    CHUNK_SIZE = 2000
    CHUNK_OVERLAP = 150
    SQL_PREVIEW_LENGTH = 100

    # Retrieval Settings
    RETRIEVAL_LIMIT = 8
    QUERIES_PER_SEARCH = 10
    VECTOR_STORE_PATH = "./qdrant_data"

    # Offline Mode Settings
    HF_HUB_OFFLINE = 1
    TRANSFORMERS_OFFLINE = 1

# Set environment variables for libraries that read them directly
os.environ["HF_HUB_OFFLINE"] = str(Config.HF_HUB_OFFLINE)
os.environ["TRANSFORMERS_OFFLINE"] = str(Config.TRANSFORMERS_OFFLINE)
os.environ["OLLAMA_NUM_THREADS"] = str(Config.NUM_THREADS)

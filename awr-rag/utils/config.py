import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Model Settings
    MODEL_BASE_URL = "http://localhost:12434/v1"
    # MODEL_NAME = "ai/llama3.1:8B-Q4_K_M"
    MODEL_NAME = "ai/gemma3:4B-Q4_0"
    TIMEOUT = 1800
    
    # Request Headers
    HEADERS = {
        # "Authorization": "Bearer your-token",
        # "User-Agent": "AWR-RAG-Client/1.0"
    }

    # Ingestion Settings
    CHUNK_SIZE = 1500
    CHUNK_OVERLAP = 150

    # Retrieval Settings
    RETRIEVAL_LIMIT = 6
    QUERIES_PER_SEARCH = 6
    VECTOR_STORE_PATH = "./qdrant_data"

    # Offline Mode Settings
    HF_HUB_OFFLINE = 1
    TRANSFORMERS_OFFLINE = 1

# Set environment variables for libraries that read them directly
os.environ["HF_HUB_OFFLINE"] = str(Config.HF_HUB_OFFLINE)
os.environ["TRANSFORMERS_OFFLINE"] = str(Config.TRANSFORMERS_OFFLINE)

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Model Settings
    # MODEL_BASE_URL = "http://localhost:11434/api/chat"
    MODEL_BASE_URL = "http://localhost:12435/v1/chat/completions"
    MODEL_NAME = "llama3.1:8B-Q4_K_M"
    # MODEL_NAME = "gpt-oss:20b"
    AVAILABLE_MODELS = [
        "llama3.1:8B-Q4_K_M",
        "gemma3:4B",
        "smollm2:latest"
    ]
    TIMEOUT = 1800
    
    # Context Logic
    CONTEXT_SIZE = 4096
    NUM_PREDICT = 4096
    NUM_THREADS = 4
    
    # Request Headers
    HEADERS = {
        "Authorization": f"Bearer {os.getenv('LLM_TOKEN', '')}",
        # "User-Agent": "AWR-RAG-Client/1.0"
    }

    # Ingestion Settings
    CHUNK_SIZE = 1500
    CHUNK_OVERLAP = 150

    # Retrieval Settings
    RETRIEVAL_LIMIT = 15
    QUERIES_PER_SEARCH = 6
    VECTOR_STORE_PATH = "./qdrant_data"

    # Offline Mode Settings
    HF_HUB_OFFLINE = 1
    TRANSFORMERS_OFFLINE = 1

# Set environment variables for libraries that read them directly
os.environ["HF_HUB_OFFLINE"] = str(Config.HF_HUB_OFFLINE)
os.environ["TRANSFORMERS_OFFLINE"] = str(Config.TRANSFORMERS_OFFLINE)
os.environ["OLLAMA_NUM_THREADS"] = str(Config.NUM_THREADS)

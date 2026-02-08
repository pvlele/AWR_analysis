import requests
import json
import time
from utils.config import Config

# Generate a long dummy context (approx 3000 tokens)
long_context = "test " * 3000

def test_generation(config_override=None):
    payload = {
        "model": Config.MODEL_NAME,
        "messages": [
            {"role": "user", "content": f"Context: {long_context}\n\nTask: Explain the context briefly based on the above."}
        ],
        "stream": False,
        "options": {
            "num_predict": 500,
            "num_ctx": Config.CONTEXT_SIZE
        }
    }
    
    if config_override:
        payload.update(config_override)

    try:
        start = time.time()
        response = requests.post(
            Config.MODEL_BASE_URL,
            json=payload,
            timeout=600,
            headers=Config.HEADERS
        )
        response.raise_for_status()
        data = response.json()
        duration = time.time() - start
        content = data.get("response", "")
        print(f"Success! Duration: {duration:.2f}s, Response length: {len(content)}")
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False

print("Testing with standard payload...")
test_generation()


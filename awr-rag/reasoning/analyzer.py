import requests
from utils.config import Config
from utils.logger import setup_logger
from reasoning.prompts import SYSTEM_PROMPT, USER_TEMPLATE
from tenacity import retry, stop_after_attempt, wait_fixed
import time
import json

logger = setup_logger(__name__)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def _generate_response(model_name, messages):
    payload = {
        "model": model_name or Config.MODEL_NAME,
        "messages": messages,
        "stream": False,
        "options": {
            "num_predict": Config.NUM_PREDICT,
            "num_ctx": Config.CONTEXT_SIZE,
            "num_thread": Config.NUM_THREADS
        }
    }
    
    response = requests.post(
        Config.MODEL_BASE_URL,
        json=payload,
        timeout=Config.TIMEOUT,
        headers=Config.HEADERS
    )
    response.raise_for_status()
    result = response.json()
    # Handle chat completion response format
    if "choices" in result:
         return result["choices"][0]["message"]["content"]
    # Fallback/alternative format support if needed, but primary is standard chat
    return result.get("response", "")

def analyze(question, retrieved_chunks, model_name=None):
    context = "\n\n".join(
        chunk.payload["text"] for chunk in retrieved_chunks
    )

    user_prompt = USER_TEMPLATE.format(
        question=question,
        context=context
    )

    # Combine system and user prompt for the completion API
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    try:
        logger.info(f"Sending request to LLM: {model_name or Config.MODEL_NAME}")
        start_time = time.time()
        response_content = _generate_response(model_name, messages)
        end_time = time.time()
        logger.info(f"Model response time: {end_time - start_time:.2f} seconds")
        return response_content
    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        return "Error: Could not generate analysis due to LLM failure."

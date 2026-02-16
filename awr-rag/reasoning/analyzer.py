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
        f"{Config.MODEL_BASE_URL.rstrip('/')}/{Config.MODEL_API_PATH.lstrip('/')}",
        json=payload,
        timeout=Config.TIMEOUT,
        headers=Config.HEADERS
    )
    response.raise_for_status()
    result = response.json()
    
    usage = result.get("usage", {})
    
    # Handle chat completion response format
    if "choices" in result:
         return result["choices"][0]["message"]["content"], usage
    # Fallback/alternative format support if needed, but primary is standard chat
    return result.get("response", ""), usage

def analyze(question, retrieved_chunks, model_name=None):
    # Check if retrieving result is a dict (Comparison Mode)
    if isinstance(retrieved_chunks, dict):
        # Comparison logic
        snapshots = list(retrieved_chunks.keys())
        # If either snapshot missing required sections (empty list), return UNKNOWN
        for sid, chunks in retrieved_chunks.items():
            if not chunks:
                 return "UNKNOWN: Insufficient AWR evidence in one or both snapshots."

        # Construct Comparison Prompt
        # Prompt: "Compare the following two AWR snapshots: ... Explain key differences..."
        context_a = "\n\n".join(c.payload["text"] for c in retrieved_chunks[snapshots[0]])
        context_b = "\n\n".join(c.payload["text"] for c in retrieved_chunks[snapshots[1]])
        
        user_prompt = (
            f"Compare the following two AWR snapshots:\n\n"
            f"Snapshot A (ID: {snapshots[0]}):\n{context_a}\n\n"
            f"Snapshot B (ID: {snapshots[1]}):\n{context_b}\n\n"
            f"Question: {question}\n\n"
            f"Explain key differences in waits, CPU, and SQL."
        )
    else:
        # Standard Single/General Analysis
        if not retrieved_chunks:
            return "UNKNOWN: Insufficient AWR evidence."

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
        
        # Log prompt size
        total_chars = sum(len(m["content"]) for m in messages)
        est_tokens = total_chars / 4
        logger.info(f"Prompt Size: {total_chars} chars (approx {est_tokens} tokens)")
        
        start_time = time.time()
        response_content, usage = _generate_response(model_name, messages)
        end_time = time.time()
        
        # Print Token Usage
        if usage:
            p_tok = usage.get('prompt_tokens', 'N/A')
            c_tok = usage.get('completion_tokens', 'N/A')
            t_tok = usage.get('total_tokens', 'N/A')
            logger.info(f"Token Usage - Prompt: {p_tok}, Completion: {c_tok}, Total: {t_tok}")
            print(f"\nToken Usage:\n  Prompt Tokens: {p_tok}\n  Completion Tokens: {c_tok}\n  Total Tokens: {t_tok}\n")
        else:
            logger.info("Token usage data not returned by API.")

        logger.info(f"Model response time: {end_time - start_time:.2f} seconds")
        return response_content
    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        return "Error: Could not generate analysis due to LLM failure."

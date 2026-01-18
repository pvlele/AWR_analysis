from openai import OpenAI
from utils.config import Config
from utils.logger import setup_logger
from reasoning.prompts import SYSTEM_PROMPT, USER_TEMPLATE
from tenacity import retry, stop_after_attempt, wait_fixed
import time

logger = setup_logger(__name__)

client = OpenAI(
    base_url=Config.MODEL_BASE_URL,
    api_key="ollama",
    timeout=Config.TIMEOUT
)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def _generate_response(model_name, messages):
    return client.chat.completions.create(
        model=model_name or Config.MODEL_NAME,
        messages=messages,
        temperature=0.5,
        extra_body={
            "num_predict": 4096,
            "num_ctx": 8192,
            "options": {
                "num_predict": 4096,
                "num_ctx": 8192
            }
        }
    )

def analyze(question, retrieved_chunks, model_name=None):
    context = "\n\n".join(
        chunk.payload["text"] for chunk in retrieved_chunks
    )

    prompt = USER_TEMPLATE.format(
        question=question,
        context=context
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]

    try:
        logger.info(f"Sending request to LLM: {model_name or Config.MODEL_NAME}")
        start_time = time.time()
        response = _generate_response(model_name, messages)
        end_time = time.time()
        logger.info(f"Model response time: {end_time - start_time:.2f} seconds")
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        return "Error: Could not generate analysis due to LLM failure."

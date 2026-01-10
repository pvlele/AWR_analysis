from openai import OpenAI
from dotenv import load_dotenv
import os
from reasoning.prompts import SYSTEM_PROMPT, USER_TEMPLATE

load_dotenv()

client = OpenAI(
    base_url=os.getenv("MODEL_BASE_URL"),
    api_key="ollama",
    timeout=1800
)

def analyze(question, retrieved_chunks, model_name=None):
    context = "\n\n".join(
        chunk.payload["text"] for chunk in retrieved_chunks
    )

    prompt = USER_TEMPLATE.format(
        question=question,
        context=context
    )

    response = client.chat.completions.create(
        model=model_name or os.getenv("MODEL_NAME"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        extra_body={
            "num_predict": 4096,
            "num_ctx": 8192,
            "options": {
                "num_predict": 4096,
                "num_ctx": 8192
            }
        }
    )

    return response.choices[0].message.content

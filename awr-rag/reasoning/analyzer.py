from openai import OpenAI
from reasoning.prompts import SYSTEM_PROMPT, USER_TEMPLATE

client = OpenAI(
    base_url="http://localhost:12434/engines/llama.cpp/v1",
    api_key="ollama",
    timeout=1800
)

def analyze(question, retrieved_chunks):
    context = "\n\n".join(
        chunk.payload["text"] for chunk in retrieved_chunks
    )

    prompt = USER_TEMPLATE.format(
        question=question,
        context=context
    )

    response = client.chat.completions.create(
        model="ai/gemma3:4B-Q4_0",
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

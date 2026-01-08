from openai import OpenAI
import sys

client = OpenAI(
    base_url="http://localhost:12434/engines/llama.cpp/v1",
    api_key="ollama",
    timeout=600
)

# Generate a long dummy context (approx 3000 tokens)
long_context = "test " * 3000

print("Testing with flat extra_body...")
try:
    response = client.chat.completions.create(
        model="ai/gemma3:4B-Q4_0",
        messages=[
            {"role": "user", "content": f"Context: {long_context}\n\nTask: Explain the context briefly based on the above."}
        ],
        temperature=0,
        max_tokens=500,
        extra_body={
            "num_predict": 500,
            "num_ctx": 8192
        }
    )
    print("Flat extra_body Response length:", len(response.choices[0].message.content))
except Exception as e:
    print("Flat extra_body Failed:", e)

print("\nTesting with nested options in extra_body...")
try:
    response = client.chat.completions.create(
        model="ai/gemma3:4B-Q4_0",
        messages=[
            {"role": "user", "content": f"Context: {long_context}\n\nTask: Explain the context briefly based on the above."}
        ],
        temperature=0,
        max_tokens=500,
        extra_body={
            "options": {
                "num_predict": 500,
                "num_ctx": 8192
            }
        }
    )
    print("Nested options Response length:", len(response.choices[0].message.content))
except Exception as e:
    print("Nested options Failed:", e)

from dotenv import load_dotenv
import os
from reasoning.analyzer import analyze
from types import SimpleNamespace

# Load environment variables
load_dotenv()

def verify():
    print("Verifying Ollama Integration...")
    
    # Mock retrieved chunks
    mock_chunks = [
        SimpleNamespace(payload={"text": "The database was slow because of a missing index on the users table."}),
        SimpleNamespace(payload={"text": "High CPU usage was observed during the backup process."})
    ]

    question = "Why was the database slow?"
    
    try:
        print(f"Question: {question}")
        response = analyze(question, mock_chunks)
        print("\n✅ Response received from Ollama:")
        print(response)
    except Exception as e:
        print(f"\n❌ Error calling Ollama: {e}")

if __name__ == "__main__":
    verify()

#!/bin/bash
# check_llm.sh

# Base URL from config
# Base URL from config
# URL="http://localhost:11434/api/chat"
URL="http://localhost:12435/v1/chat/completions"

# Configuration from config
MODEL="docker.io/ai/llama3.1:8B-Q4_K_M"
PROMPT="Hello, are you running?"

# JSON Payload (Chat format matching analyzer.py)
DATA=$(cat <<EOF
{
  "model": "$MODEL",
  "messages": [
    {
      "role": "user",
      "content": "$PROMPT"
    }
  ],
  "stream": false,
  "options": {
      "num_predict": 100
  }
}
EOF
)

echo "Sending POST request to $URL..."
echo "Payload: $DATA"

# Send request
curl -s \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer my-token1" \
    -H "User-Agent: AWR-RAG-Check/1.0" \
    -d "$DATA" "$URL" | head -n 20
echo "" # Newline for formatting

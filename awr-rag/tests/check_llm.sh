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

# Load environment variables
SCRIPT_DIR=$(dirname "$(realpath "$0")")
PROJECT_ROOT=$(dirname "$SCRIPT_DIR")
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
fi

echo "Using Token: $TOKEN"

# Send request
curl -s \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -H "User-Agent: AWR-RAG-Check/1.0" \
    -d "$DATA" "$URL" | head -n 20
echo "" # Newline for formatting

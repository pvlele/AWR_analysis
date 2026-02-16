#!/bin/bash
# check_llm_direct.sh
# Diagnostic script to check LLM directly (bypassing proxy)

URL="http://localhost:12434/v1/chat/completions"
# Use a small model for quick testing if available, otherwise the default
MODEL="docker.io/ai/llama3.1:8B-Q4_K_M" 

echo "1. Checking API Tags (Service capability)..."
curl -s http://localhost:12434/api/tags | head -n 5
echo ""

echo "2. Sending Test Chat Request to $MODEL..."
# JSON Payload
DATA=$(cat <<EOF
{
  "model": "$MODEL",
  "messages": [
    {
      "role": "user",
      "content": "Hello, simply reply 'OK'."
    }
  ],
  "stream": false
}
EOF
)

# Send request with a max time of 30 seconds to fail fast
curl -v \
    -H "Content-Type: application/json" \
    -d "$DATA" "$URL" --max-time 30

echo ""

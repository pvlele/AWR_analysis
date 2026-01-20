#!/bin/bash
# check_llm.sh

# Load environment entries if needed, but for now we'll stick to a simple check
# You might want to source .env to get the Config.MODEL_BASE_URL if it varies.
# For this script we will default to the localhost address used in Config.

# Base URL for the Chat Completions API
URL="http://localhost:12434/v1/chat/completions"

# Configuration
MODEL="ai/gemma3:4B-Q4_0"
MESSAGE_CONTENT="Hello, are you running?"
MAX_TOKENS=100

# Define headers here
HEADER_ARGS=(
    -H "Content-Type: application/json"
    -H "Authorization: Bearer dummy-token-123"
    -H "User-Agent: AWR-RAG-Check/1.0"
    -H "X-Custom-Header-1: Value1"
    -H "X-Custom-Header-2: Value2"
    -H "X-Request-ID: req-abc-123"
)

# JSON Payload
# Using a heredoc for cleaner JSON formatting within the script
DATA=$(cat <<EOF
{
  "model": "$MODEL",
  "messages": [
    {
      "role": "user",
      "content": "$MESSAGE_CONTENT"
    }
  ],
  "max_tokens": $MAX_TOKENS
}
EOF
)

echo "Sending POST request to $URL..."
echo "Payload: $DATA"

# Send request
curl -s "${HEADER_ARGS[@]}" -d "$DATA" "$URL" | head -n 20
echo "" # Newline for formatting

#!/bin/bash

echo "Testing advice endpoint..."

curl -X POST http://127.0.0.1:8000/advice \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dafd3a427c8ce3de0624ab7d72b45bac5c041e6a3810967a7cea017da7e071c2" \
  -d '{
    "chore_id": "dishes", 
    "user_context": "testing"
  }' \
  --verbose

echo -e "\n\nTesting advice status endpoint..."

curl -X GET http://127.0.0.1:8000/advice/status \
  --verbose

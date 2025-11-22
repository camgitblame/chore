#!/bin/bash
# Keep the Cloud Run service warm by pinging every 4 minutes

API_URL="https://chore-api-rag-611389647575.us-central1.run.app"


while true; do
    echo "[$(date)] Pinging health endpoint..."
    curl -s "$API_URL/health" > /dev/null
    
    if [ $? -eq 0 ]; then
        echo "[$(date)] ✓ Service is warm"
    else
        echo "[$(date)] ✗ Ping failed"
    fi
    
    # Wait 4 minutes 
    sleep 240
done

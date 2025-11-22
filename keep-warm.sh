#!/bin/bash
# Keep the Cloud Run service warm by pinging it every 4 minutes
# Run this script in the background or as a cron job

API_URL="https://chore-api-rag-611389647575.us-central1.run.app"

echo "Starting keep-warm script for $API_URL"
echo "Press Ctrl+C to stop"

while true; do
    echo "[$(date)] Pinging health endpoint..."
    curl -s "$API_URL/health" > /dev/null
    
    if [ $? -eq 0 ]; then
        echo "[$(date)] ✓ Service is warm"
    else
        echo "[$(date)] ✗ Ping failed"
    fi
    
    # Wait 4 minutes (Cloud Run keeps instances alive for 5 minutes)
    sleep 240
done

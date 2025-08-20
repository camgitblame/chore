#!/bin/bash

# Deployment script for Chore App with RAG integration on GCP
# Usage: ./deploy-rag.sh [PROJECT_ID] [REGION]

PROJECT_ID=${1:-"your-project-id"}
REGION=${2:-"us-central1"}
SERVICE_NAME="chore-app-rag"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "Deploying Chore App with RAG to Google Cloud Run..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"

# Set the project
gcloud config set project $PROJECT_ID

# Build and push the Docker image
echo "Building Docker image..."
docker build -f Dockerfile.ollama -t $IMAGE_NAME .

echo "Pushing image to Google Container Registry..."
docker push $IMAGE_NAME

# Create secrets if they don't exist
echo "Creating secrets..."
gcloud secrets create chore-app-secrets --data-file=.env --quiet || echo "Secrets already exist"

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --region $REGION \
  --platform managed \
  --memory 8Gi \
  --cpu 4 \
  --timeout 3600 \
  --concurrency 10 \
  --allow-unauthenticated \
  --set-env-vars="OLLAMA_MODEL=llama3.1:8b,ADVICE_ENABLED=true" \
  --set-secrets="INTERNAL_API_KEY=chore-app-secrets:latest:internal-api-key" \
  --set-secrets="ELEVENLABS_API_KEY=chore-app-secrets:latest:elevenlabs-api-key"

echo "Deployment complete!"
echo "Service URL:"
gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'

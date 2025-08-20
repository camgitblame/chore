#!/bin/bash

# Deployment script for Chore App with RAG integration on GCP
# Usage: ./deploy-rag.sh

PROJECT_ID="chore-469009"
REGION="us-central1"
SERVICE_NAME="chore-api-rag"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 Deploying Chore App with RAG to Google Cloud Run..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"

# Set the project
gcloud config set project $PROJECT_ID

# Navigate to the FastAPI service directory
cd "$(dirname "$0")"

# Build and push the Docker image
echo "📦 Building Docker image..."
docker build -f Dockerfile.ollama -t $IMAGE_NAME .

echo "⬆️ Pushing image to Google Container Registry..."
docker push $IMAGE_NAME

# Create secrets if they don't exist
echo "🔐 Setting up secrets..."
echo "dafd3a427c8ce3de0624ab7d72b45bac5c041e6a3810967a7cea017da7e071c2" | gcloud secrets create internal-api-key --data-file=- --quiet 2>/dev/null || echo "internal-api-key secret already exists"
echo "sk_9eabcf21fe89240470d167aaedb421b54d4824959bf3c6f8" | gcloud secrets create elevenlabs-api-key --data-file=- --quiet 2>/dev/null || echo "elevenlabs-api-key secret already exists"

# Deploy to Cloud Run
echo "🌟 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --region $REGION \
  --platform managed \
  --memory 8Gi \
  --cpu 4 \
  --timeout 3600 \
  --concurrency 5 \
  --min-instances 0 \
  --max-instances 2 \
  --allow-unauthenticated \
  --set-env-vars="OLLAMA_MODEL=llama3.2:1b,ADVICE_ENABLED=true,STORE_TO_GCS=false,BUCKET_NAME=,CORS_ORIGIN=*" \
  --set-secrets="INTERNAL_API_KEY=internal-api-key:latest,ELEVENLABS_API_KEY=elevenlabs-api-key:latest"

if [ $? -eq 0 ]; then
    echo "✅ Deployment complete!"
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')
    echo "🌐 Service URL: $SERVICE_URL"
    echo ""
    echo "🔧 Next steps:"
    echo "1. Update your frontend .env.local to use: $SERVICE_URL"
    echo "2. Test the /advice/status endpoint: $SERVICE_URL/advice/status"
    echo "3. Deploy your frontend to Vercel"
else
    echo "❌ Deployment failed!"
    exit 1
fi

#!/bin/bash
# Google Cloud Run Deployment Script for Chore API

echo "🚀 Deploying Chore API to Google Cloud Run"
echo "==========================================="

# Configuration (update these if different)
PROJECT_ID="chore-469009"
SERVICE_NAME="chore-api"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "📋 Deployment Configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Service Name: $SERVICE_NAME"
echo "  Region: $REGION"
echo "  Image: $IMAGE_NAME"
echo ""

# Check if we're in the right directory
if [ ! -f "Dockerfile" ]; then
    echo "❌ Error: Dockerfile not found. Please run this script from fastapi-service directory."
    exit 1
fi

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI not found. Please install Google Cloud SDK first."
    echo "   Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Build the Docker image
echo "🔨 Building Docker image..."
gcloud builds submit --tag $IMAGE_NAME

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi

echo "✅ Docker image built successfully"

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10 \
  --set-env-vars="CORS_ORIGIN=*" \
  --set-env-vars="ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY}" \
  --set-env-vars="INTERNAL_API_KEY=${INTERNAL_API_KEY}"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Deployment successful!"
    echo ""
    echo "📊 Your updated API now includes:"
    echo "  ✅ SQLite database system"
    echo "  ✅ 15 chores (5 original + 10 new)"
    echo "  ✅ Improved search functionality"
    echo "  ✅ Database management tools"
    echo ""
    echo "🔗 Service URL:"
    gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)"
    echo ""
    echo "💡 Next steps:"
    echo "  1. Test your production API endpoints"
    echo "  2. Update your frontend .env.local if needed"
    echo "  3. Verify all 15 chores are accessible"
else
    echo "❌ Deployment failed"
    exit 1
fi

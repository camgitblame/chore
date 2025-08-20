#!/bin/bash

# Deployment script f# Build and push the Docker image
echo "Building Docker image for linux/amd64..."
docker build --platform linux/amd64 -f Dockerfile.ollama -t $IMAGE_NAME .Chore App with RAG integration on GCP
# Usage: ./deploy-rag.sh

PROJECT_ID="chore-469009"
REGION="us-central1"
SERVICE_NAME="chore-api-rag"
REPOSITORY="chore-repo"
IMAGE_NAME="$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$SERVICE_NAME"

echo "Deploying Chore App with RAG to Google Cloud Run..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable secretmanager.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable artifactregistry.googleapis.com --quiet

# Configure Docker to authenticate with Artifact Registry
echo "Configuring Docker authentication..."
gcloud auth configure-docker $REGION-docker.pkg.dev --quiet

# Create Artifact Registry repository if it doesn't exist
echo "Setting up Artifact Registry..."
gcloud artifacts repositories create $REPOSITORY \
  --repository-format=docker \
  --location=$REGION \
  --description="Docker repository for chore app" \
  --quiet 2>/dev/null || echo "Repository already exists"

# Navigate to the FastAPI service directory
cd "$(dirname "$0")"

# Build and push the Docker image
echo "Building Docker image for linux/amd64..."
docker buildx build --platform linux/amd64 -f Dockerfile.ollama -t $IMAGE_NAME . --push

# Create secrets if they don't exist
echo "🔐 Setting up secrets..."
echo "dafd3a427c8ce3de0624ab7d72b45bac5c041e6a3810967a7cea017da7e071c2" | gcloud secrets create internal-api-key --data-file=- --quiet 2>/dev/null || echo "internal-api-key secret already exists"
echo "sk_9eabcf21fe89240470d167aaedb421b54d4824959bf3c6f8" | gcloud secrets create elevenlabs-api-key --data-file=- --quiet 2>/dev/null || echo "elevenlabs-api-key secret already exists"

# Grant Secret Manager access to the default compute service account
echo "🔑 Setting up secret permissions..."
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
SERVICE_ACCOUNT="$PROJECT_NUMBER-compute@developer.gserviceaccount.com"

gcloud secrets add-iam-policy-binding internal-api-key \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor" \
    --quiet

gcloud secrets add-iam-policy-binding elevenlabs-api-key \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor" \
    --quiet

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
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
  --port 8080 \
  --cpu-boost \
  --execution-environment gen2 \
  --set-env-vars="OLLAMA_BASE_URL=http://localhost:11434,OLLAMA_MODEL=llama3.2:1b,VECTOR_DB_PATH=/app/data/vector_store,ADVICE_ENABLED=true,STORE_TO_GCS=false,BUCKET_NAME=,CORS_ORIGIN=*" \
  --set-secrets="INTERNAL_API_KEY=internal-api-key:latest,ELEVENLABS_API_KEY=elevenlabs-api-key:latest"

if [ $? -eq 0 ]; then
    echo "Deployment complete!"
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)")
    echo "Service URL: $SERVICE_URL"
    echo ""
    echo "Next steps:"
    echo "1. Update your frontend .env.local to use: $SERVICE_URL"
    echo "2. Test the /advice/status endpoint: $SERVICE_URL/advice/status"
    echo "3. Deploy your frontend to Vercel"
else
    echo "Deployment failed!"
    exit 1
fi
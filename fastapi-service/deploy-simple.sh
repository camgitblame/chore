#!/bin/bash
set -e

# Simple deployment script for TTS-only service (no RAG)
echo "Deploying Simple Chore API with Edge TTS..."

PROJECT_ID="chore-469009"
REGION="us-central1"
SERVICE_NAME="chore-api-simple"

gcloud config set project $PROJECT_ID

echo "Configuring Docker authentication..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev

echo "Building Docker image..."
docker build -f Dockerfile.simple -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/chore-registry/${SERVICE_NAME}:latest .

echo "Pushing to Artifact Registry..."
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/chore-registry/${SERVICE_NAME}:latest

echo "Setting up secrets..."
echo "dafd3a427c8ce3de0624ab7d72b45bac5c041e6a3810967a7cea017da7e071c2" | gcloud secrets create internal-api-key --data-file=- --quiet 2>/dev/null || echo "internal-api-key secret already exists"

echo "Setting up secret permissions..."
gcloud secrets add-iam-policy-binding internal-api-key \
  --member="serviceAccount:611389647575-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/chore-registry/${SERVICE_NAME}:latest \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60 \
  --min-instances 0 \
  --max-instances 10 \
  --set-secrets="INTERNAL_API_KEY=internal-api-key:latest"

echo "Deployment complete!"
echo "Service URL: https://${SERVICE_NAME}-611389647575.${REGION}.run.app"
echo ""
echo "Next steps:"
echo "1. Update your frontend .env.local NEXT_PUBLIC_API_BASE to use the new URL"
echo "2. Test the /health endpoint"

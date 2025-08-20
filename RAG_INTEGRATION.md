# RAG Integration Guide

This guide explains how to integrate and deploy the LangChain + RAG + Ollama feature for the Chore App.

## Overview

The RAG (Retrieval-Augmented Generation) integration adds intelligent advice generation to the chore app using:

- **Ollama**: Local LLM hosting (llama3.1:8b model)
- **LangChain**: RAG orchestration framework
- **ChromaDB**: Vector database for knowledge storage
- **Sentence Transformers**: Text embeddings for semantic search

## Features

- **AI-powered advice**: Get contextual tips and suggestions for each chore
- **Retro UI integration**: "Get Advice" button matches existing arcade aesthetic
- **Fallback system**: Works even when RAG/Ollama is unavailable
- **GCP deployment ready**: Optimized for Cloud Run with proper resource allocation

## Local Development Setup

### Prerequisites

1. **Install Ollama** (macOS):
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Pull the required model**:
   ```bash
   ollama pull llama3.1:8b
   ```

3. **Install Python dependencies**:
   ```bash
   cd fastapi-service/app
   pip install -r requirements.txt
   ```

### Running Locally

1. **Start Ollama server**:
   ```bash
   ollama serve
   ```

2. **Configure environment** (`.env`):
   ```env
   INTERNAL_API_KEY=your_internal_api_key
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.1:8b
   ADVICE_ENABLED=true
   ```

3. **Start FastAPI backend**:
   ```bash
   cd fastapi-service/app
   uvicorn main:app --reload
   ```

4. **Start Next.js frontend**:
   ```bash
   cd chore
   npm run dev
   ```

## GCP Deployment

### Option 1: Using the Deployment Script

```bash
cd fastapi-service
./deploy-rag.sh YOUR_PROJECT_ID us-central1
```

### Option 2: Manual Deployment

1. **Build and push Docker image**:
   ```bash
   docker build -f Dockerfile.ollama -t gcr.io/YOUR_PROJECT_ID/chore-app-rag .
   docker push gcr.io/YOUR_PROJECT_ID/chore-app-rag
   ```

2. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy chore-app-rag \
     --image gcr.io/YOUR_PROJECT_ID/chore-app-rag \
     --region us-central1 \
     --memory 8Gi \
     --cpu 4 \
     --timeout 3600 \
     --allow-unauthenticated
   ```

### Resource Requirements

- **Memory**: 8GB (minimum for llama3.1:8b model)
- **CPU**: 4 cores (for reasonable inference speed)
- **Timeout**: 1 hour (for model loading and large requests)
- **Storage**: ~4GB for model files

## API Endpoints

### Get Advice
```http
POST /advice
Content-Type: application/json
X-API-Key: your_internal_api_key

{
  "chore_id": "chore_123",
  "user_context": "optional context"
}
```

Response:
```json
{
  "advice": "• Start by gathering all necessary items...",
  "chore_id": "chore_123", 
  "rag_available": true
}
```

### Check Status
```http
GET /advice/status
```

Response:
```json
{
  "advice_available": true,
  "ollama_available": true,
  "vector_store_available": true,
  "knowledge_count": 42
}
```

## Knowledge Base

The system includes curated advice in `knowledge/chore_tips.json` covering:

- **Kitchen cleaning**: Surface preparation, efficiency tips
- **Bathroom cleaning**: Product application, safety
- **Laundry**: Timing, organization, care instructions
- **General organization**: Decluttering, maintenance
- **ADHD-specific**: Time management, focus strategies
- **Autism-specific**: Sensory considerations, routines

### Adding New Knowledge

Edit `fastapi-service/app/knowledge/chore_tips.json`:

```json
{
  "new_category": [
    "Tip 1: Helpful advice here",
    "Tip 2: Another useful suggestion"
  ]
}
```

The vector store will automatically update on next startup.

## Frontend Integration

The "Get Advice" button appears next to the audio controls with matching retro styling:

```tsx
<button 
  className="flex items-center gap-2 px-4 py-2 rounded-none transition-all duration-200 border-2 font-mono tracking-wide bg-black border-purple-500 text-purple-400 hover:bg-purple-900 hover:bg-opacity-30"
  onClick={getAdvice}
  disabled={loadingAdvice}
>
  {loadingAdvice ? "ANALYZING..." : "★ GET ADVICE"}
</button>
```

## Performance Considerations

### Model Selection
- **llama3.1:8b**: Good balance of quality and speed
- **llama3.1:70b**: Higher quality but requires 32GB+ RAM
- **codellama**: Specialized for code/technical instructions

### Optimization Tips
- Enable model quantization for smaller memory footprint
- Use Cloud Run gen2 for better cold start performance
- Consider Cloud SQL for vector storage in production
- Implement request caching for frequent queries


### Debug Commands

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Test advice endpoint
curl -X POST http://localhost:8000/advice/status

# Check vector store
python -c "from rag.vector_store import VectorStore; vs = VectorStore(); print(vs.get_collection_count())"
```
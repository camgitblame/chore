# Chore Log

A Next.js web app that makes household chores easier with AI-powered advice, audio guidance, and step-by-step tracking, designed to support people with ADHD and people on the autism spectrum.

## Features
- **Chore search**: Browse and select from a curated list of common household tasks
- **Voice guidance**: Clear spoken instructions with ElevenLabs, auto-play on selection, mute control
- **Step tracking**: Check off steps and get a friendly completion cue
- **AI-Powered Advice**: Get contextual, personalized tips fo each chore using RAG with Ollama
- **Retro UI**: Neon-accented, dark theme in arcade style with fast chore search on desktop and mobile

## Tech Stack

### Frontend
- **Framework**: Next.js 15, React 19, TypeScript
- **Styling**: Tailwind CSS v4
- **Deployment**: Vercel

### Backend & AI
- **API**: FastAPI (deployed on Google Cloud Run)
- **Database**: SQLite with chore data
- **AI Model**: Ollama (llama3.2:1b) for advice generation
- **RAG Framework**: LangChain for retrieval-augmented generation
- **Vector Database**: ChromaDB for semantic search
- **Knowledge Base**: 56 curated chore tips across 8 categories
- **Voice AI**: ElevenLabs API for text-to-speech

### Infrastructure
- **Backend Hosting**: Google Cloud Run
- **Containerization**: Docker with multi-stage builds

## Project Structure

```
chore_app/
├── chore/                    # Next.js frontend application
│   ├── app/                  # Next.js app router
│   │   ├── api/              # API routes
│   │   │   ├── advice-proxy/ # RAG advice proxy endpoint
│   │   │   └── tts-proxy/    # Text-to-speech proxy endpoint
│   │   ├── globals.css       # Global styles
│   │   ├── layout.tsx        # Root layout
│   │   └── page.tsx          # Main chore interface with RAG integration
│   ├── .env.local            # Environment variables
│   └── package.json          # Frontend dependencies
├── fastapi-service/          # Python backend service
│   ├── app/                  # FastAPI application
│   │   ├── rag/              # RAG system components
│   │   │   ├── advice_generator.py    # Main RAG orchestrator
│   │   │   ├── ollama_client.py       # Ollama LLM client
│   │   │   └── vector_store.py        # ChromaDB vector operations
│   │   ├── data/             # Persistent data
│   │   │   └── vector_store/ # ChromaDB database
│   │   ├── knowledge/        # Knowledge base
│   │   │   └── chore_tips.json        # Chore tips
│   │   ├── database.py       # SQLite chore database
│   │   ├── main.py           # FastAPI app with RAG endpoints
│   │   └── requirements.txt  # Python dependencies
│   ├── Dockerfile.ollama     # Production container with Ollama
│   └── deploy-rag.sh         # Deployment script
└── README.md                 
```

## Getting Started

### Prerequisites

- Node.js 18+ 
- ElevenLabs API key 

### Installation

1. Clone the repository:
```bash
git clone https://github.com/camgitblame/chore.git
cd chore_app
```

2. Navigate to the frontend directory and install dependencies:
```bash
cd chore
npm install
```

3. Set up environment variables by creating `.env.local` in the `chore/` directory:
```bash
# RAG-enabled backend API endpoint 
NEXT_PUBLIC_API_BASE=https://chore-api-rag-611389647575.us-central1.run.app

# ElevenLabs API key for text-to-speech
ELEVENLABS_API_KEY=elevenlabs_api_key

# Internal API key for secure backend communication
INTERNAL_API_KEY=internal_api_key
```

4. Run the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) .

## Local RAG Development

To run the RAG system locally for development:

1. **Install Python dependencies**:
```bash
cd fastapi-service/app
pip install -r requirements.txt
```

2. **Install Ollama**:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.2:1b
```

3. **Set up environment variables**:
```bash
# In fastapi-service/app/.env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b
VECTOR_DB_PATH=./data/vector_store
ADVICE_ENABLED=true
ELEVENLABS_API_KEY=elevenlabs_api_key
INTERNAL_API_KEY=internal_api_key
```

4. **Run the backend**:
```bash
cd fastapi-service/app
python -m uvicorn main:app --reload
```

5. **Update frontend to use local backend**:
```bash
# In chore/.env.local
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

## Deployment

A demo of the app is deployed at [https://choreapp.vercel.app](https://choreapp.vercel.app/)


### Deployment Commands
```bash
# Deploy RAG backend to Google Cloud Run
cd fastapi-service
./deploy-rag.sh
```

## How It Works

1. **Search & Select**: Type chore keywords (e.g., "microwave", "desk", "kitchen") to find a chore
2. **View Steps**: Click on a chore to see the full step-by-step guide
3. **Get AI Advice**: Click "Get Advice" for personalized, contextual tips powered by RAG
4. **Audio Instructions**: Audio instructions automatically play when you select a chore
5. **Track Progress**: Check off each step as you complete it
6. **Completion**: A short completion sound plays when all steps are done

## RAG Features

The RAG system provides:

- **Contextual Advice**: Tips specific to each chore type (kitchen, bathroom, organization, etc.)
- **Personalized Recommendations**: Considers user context like ADHD, autism, motivation levels
- **Knowledge Base**: 56 curated tips from cleaning experts and accessibility specialists  
- **Smart Search**: Vector similarity search finds most relevant advice
- **AI Generation**: Ollama LLM creates coherent, helpful responses


---

Built with ❤️ for the neurodivergent community by [Cam Nguyen](https://github.com/camgitblame)


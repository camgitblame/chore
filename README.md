# Chore Log

A Next.js web app that makes household chores easier with AI-powered advice, audio guidance, and step-by-step tracking, designed to support people with ADHD and people on the autism spectrum.

## Features
- **Chore search**: Browse and select from a curated list of common household tasks
- **Voice guidance**: Clear spoken instructions with gTTS (Google Text-to-Speech), auto-play on selection, mute control
- **Step tracking**: Check off steps and get a congratulation message
- **AI-Powered Advice**: Get personalized tips for each chore using RAG with Groq's lightning-fast LLM
- **Retro UI**: Neon-accented, dark theme in arcade style with fast chore search on desktop and mobile

## Tech Stack

### Frontend
- **Framework**: Next.js, React, TypeScript
- **Styling**: Tailwind CSS 
- **Deployment**: Vercel

### Backend & AI
- **API**: FastAPI, Groq API
- **Database**: SQLite
- **AI Model**: Llama (llama-3.1-8b-instant via Groq)
- **Knowledge Base**: Curated tips across 8 categories (kitchen, bathroom, organization, etc.)
- **Voice AI**: gTTS (Google Text-to-Speech) 

### Infrastructure
- **Backend Hosting**: Google Cloud Run 
- **Containerization**: Docker 

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
│   │   ├── rag/              # Knowledge base
│   │   │   └── knowledge_base.json    # Curated chore tips
│   │   ├── groq_rag.py       # RAG with Groq API
│   │   ├── database.py       # SQLite chore database
│   │   ├── main.py           # FastAPI app with TTS and advice endpoints
│   │   ├── requirements-simple.txt    # Dependencies
│   │   └── .env              # Environment variables 
│   ├── Dockerfile.simple     # Lightweight production container
│   └── chores.db             # SQLite database 
└── README.md                 
```

## Getting Started

### Prerequisites

- Node.js 18+ 
- Groq API key (https://console.groq.com) 

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
# Backend API endpoint
NEXT_PUBLIC_API_BASE=https://your-backend-url.run.app

# Internal API key for secure backend communication
INTERNAL_API_KEY=your_secure_api_key
```

4. Run the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) .

## Local Development

To run the backend locally for development:

1. **Install Python dependencies**:
```bash
cd fastapi-service/app
pip install -r requirements-simple.txt
```

2. **Get a Groq API key**:
   - Visit https://console.groq.com/
   - Create an API key

3. **Set up environment variables**:
```bash
# In fastapi-service/app/.env
GROQ_API_KEY=your_groq_api_key_here
INTERNAL_API_KEY=your_internal_api_key
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


### Backend Deployment to Google Cloud Run

```bash
# Build and push Docker image
cd fastapi-service
docker buildx build --platform linux/amd64 \
  -f Dockerfile.simple \
  -t REGION-docker.pkg.dev/PROJECT-ID/REGISTRY-NAME/IMAGE-NAME:latest \
  --push .

# Deploy to Cloud Run with Groq API key
gcloud run deploy SERVICE-NAME \
  --image REGION-docker.pkg.dev/PROJECT-ID/REGISTRY-NAME/IMAGE-NAME:latest \
  --region REGION \
  --update-env-vars="GROQ_API_KEY=your_groq_api_key" \
  --quiet
```

### Frontend Deployment

The frontend is automatically deployed to Vercel on push to main branch.

## How It Works

1. **Search & Select**: Type chore keywords (e.g., "microwave", "desk", "kitchen") to find a chore
2. **View Steps**: Click on a chore to see the full step-by-step guide
3. **Get AI Advice**: Click "Get Advice" for personalized, contextual tips powered by RAG
4. **Audio Instructions**: Audio instructions automatically play when you select a chore
5. **Track Progress**: Check off each step as you complete it
6. **Completion**: A short completion sound plays when all steps are done

## RAG Features

The RAG system provides:

- **Contextual Tips**: Specific advice for each chore type (kitchen, bathroom, organization, etc.)
- **Personalized Recommendations**: Considers user context like ADHD, autism, energy levels, motivation
- **Knowledge Base**: Curated tips from cleaning experts and accessibility specialists


---

Built with 💛 for the neurodivergent community by [Cam Nguyen](https://github.com/camgitblame)


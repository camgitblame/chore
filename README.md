# Chore Log

A Next.js web app that makes household chores easier with AI-powered advice, audio guidance, and step-by-step tracking, designed to support people with ADHD and people on the autism spectrum.

## Features
- **Chore suggestions**: Select time (5/10/20 min) and location (Kitchen, Bedroom, Bathroom, Living Room, Office, Laundry Area) for personalized chore suggestions
- **Countdown Timer**: Built-in timer for each chore 
- **Voice Guidance**: Clear spoken instructions with gTTS, auto-play on selection, mute control
- **Step Tracking**: Check off steps and get a congratulation message with audio celebration
- **AI-Powered Advice**: Get personalized tips for each chore using RAG with Groq API

## Tech Stack

### Frontend
- **Framework**: Next.js, React, TypeScript
- **Styling**: Tailwind CSS 

### Backend & AI
- **API**: FastAPI, Groq API
- **Database**: SQLite
- **AI Model**: Llama (llama-3.1-8b-instant)
- **Knowledge Base**: Curated tips across 8 categories
- **Voice AI**: gTTS (Google Text-to-Speech) 

### Infrastructure
- **Backend Hosting**: GCP 
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
│   │   └── page.tsx          # Main UI 
│   ├── public/
│   │   └── icons/            # SVG icons 
│   ├── .env.local            # Environment variables (gitignored)
│   └── package.json          # Frontend dependencies
├── fastapi-service/          # Python backend service
│   ├── app/                  # FastAPI application
│   │   ├── rag/              # Knowledge base
│   │   │   └── knowledge_base.json    # Chore tips
│   │   ├── groq_rag.py       # RAG implementation with Groq API
│   │   ├── database.py       # SQLite queries
│   │   ├── main.py           # FastAPI app with TTS, advice, and chore endpoints
│   │   ├── requirements-simple.txt    # Dependencies
│   │   └── chores.db         # SQLite database 
│   ├── Dockerfile.simple     # Production container
│   └── venv/                 # Python virtual environment
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

# Internal API key for secure backend
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
# fastapi-service/app/.env
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
# chore/.env.local
NEXT_PUBLIC_API_BASE=http://localhost:8000
```


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

---

Built with 💛 for the neurodivergent community by [Cam Nguyen](https://github.com/camgitblame)


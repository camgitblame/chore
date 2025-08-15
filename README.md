# ADHD Chore Chart

A Next.js web application that helps people with ADHD complete household chores through guided audio instructions and step tracking.

## Features
- **Chore search**: Browse and select from a curated list of common household tasks.
- **Voice guidance**: Clear spoken instructions with ElevenLabs, auto-play on selection, mute control.
- **Step tracking**: Check off steps and get a friendly completion cue.
- **Retro UI**: Neon-accented, dark theme in arcade style with fast chore search on desktop and mobile.

## Tech Stack

- **Frontend**: Next.js 15, React 19, TypeScript
- **Styling**: Tailwind CSS v4
- **AI Voice**: ElevenLabs API
- **Backend**: FastAPI (deployed on Google Cloud Run)

## Project Structure

```
chore_app/
├── chore/              # Next.js frontend application
│   ├── app/            # Next.js app router
│   ├── .env.local      # Environment variables 
│   └── package.json    # Frontend dependencies
├── fastapi-service/    # Python backend service
│   ├── app/            # FastAPI application
│   └── Dockerfile      # Container configuration
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
# Backend API endpoint 
NEXT_PUBLIC_API_BASE=https://chore-api-611389647575.us-central1.run.app

# Add your ElevenLabs API key (NEVER commit this file to git)
ELEVENLABS_API_KEY= elevenlabs_api_key_here

# Internal API key for backend communication
INTERNAL_API_KEY= internal_api_key_here
```

4. Run the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## How It Works

1. Type chore keywords (e.g., "microwave", "desk", "kitchen") to find relevant chores
2. Click on a chore to see the full step-by-step guide
3. Audio instructions automatically play when you select a chore
4. Check off each step as you complete it
5. Get encouraging feedback when you finish all steps

## API Endpoints

### Frontend API Routes
- `POST /api/tts-proxy` - Proxy for generating chore instruction audio

### Backend API (FastAPI)
- Base URL: `https://chore-api-611389647575.us-central1.run.app`
- `GET /chores?q={query}` - Search for chores matching the query
- `POST /tts` - Generate audio for chore instructions

## Development

### Frontend Development
```bash
cd chore
npm run dev    # Start development server
npm run build  # Build for production
npm run start  # Start production server
```

### Backend Development
The FastAPI backend is deployed on Google Cloud Run. 

1. For local development:
```bash
cd fastapi-service
pip install -r app/requirements.txt
uvicorn app.main:app --reload
```

2. Install dependencies:
```bash
npm install
```


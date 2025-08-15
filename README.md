# ADHD Chore Chart

A Next.js web application that helps people with ADHD complete household chores through guided audio instructions and step tracking.

## Features

- **Chore Search**: Search through a curated catalog of common household chores
- **Audio Guidance**: AI-generated voice instructions using ElevenLabs
- **Step-by-Step Tracking**: Check off each step as you complete it
- **Auto-Play Instructions**: Automatic audio playback when selecting a chore
- **Completion Celebration**: Encouraging audio feedback when all steps are done
- **Mute/Unmute Control**: Toggle audio on/off as needed
- **Retro Gaming UI**: Neon-styled dark theme with retro arcade aesthetics
- **Responsive Design**: Works on desktop and mobile

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
│   ├── .env.local      # Environment variables (not in git)
│   └── package.json    # Frontend dependencies
├── fastapi-service/    # Python backend service
│   ├── app/            # FastAPI application
│   └── Dockerfile      # Container configuration
└── README.md           # This file
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

1. **Search**: Type chore keywords (e.g., "microwave", "desk", "kitchen") to find relevant chores
2. **Select**: Click on a chore to see the full step-by-step guide
3. **Listen**: Audio instructions automatically play when you select a chore
4. **Track**: Check off each step as you complete it
5. **Celebrate**: Get encouraging feedback when you finish all steps

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
The FastAPI backend is already deployed on Google Cloud Run. For local development:
```bash
cd fastapi-service
pip install -r app/requirements.txt
uvicorn app.main:app --reload
```

## Security Best Practices

- Never commit API keys or sensitive environment variables to version control
- Keep your `.env.local` file secure and don't share it publicly
- Regularly rotate your API keys




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
- ElevenLabs API key (keep this secure and never commit to version control)

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

# Add your ElevenLabs API key
ELEVENLABS_API_KEY= elevenlabs_api_key_here

# Internal API key for backend communication
INTERNAL_API_KEY=your_internal_api_key_here
```

4. Run the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## How It Works

1. **Search**: Type chore keywords (e.g., "microwave", "desk", "kitchen") to find relevant chores
2. **Select**: Click on a chore to see the full step-by-step guide
3. **Listen**: Audio instructions automatically play when you select a chore
4. **Track**: Check off each step as you complete it
5. **Celebrate**: Get encouraging feedback when you finish all steps

## API Endpoints

### Frontend API Routes
- `POST /api/tts-proxy` - Proxy for generating chore instruction audio (requires valid API key)

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

3. Set up environment variables:
```bash
cp .env.local.example .env.local
```

Add API configuration to `.env.local`:
```bash
# Replace with actual API endpoint
NEXT_PUBLIC_API_BASE=https://your-api-endpoint.com

# Add ElevenLabs API key 
ELEVENLABS_API_KEY= elevenlasb_api_key
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




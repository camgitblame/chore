# ADHD Chore Chart

A Next.js web application that helps people with ADHD complete household chores through guided audio instructions and step tracking.

## Features

- **Chore Search**: Search through a curated catalog of common household chores
- **Audio Guidance**: AI-generated voice instructions using ElevenLabs
- **Step-by-Step Tracking**: Check off each step as you complete it
- **Auto-Play Instructions**: Automatic audio playback when selecting a chore
- **Completion Celebration**: Encouraging audio feedback when all steps are done
- **Mute/Unmute Control**: Toggle audio on/off as needed
- **Dark Mode UI**: Easy-on-the-eyes dark theme
- **Responsive Design**: Works on desktop and mobile

## Tech Stack

- **Frontend**: Next.js 15, React 19, TypeScript
- **Styling**: Tailwind CSS v4
- **AI Voice**: ElevenLabs API
- **Backend**: FastAPI (deployed on Google Cloud Run)

## Getting Started

### Prerequisites

- Node.js 18+ 
- ElevenLabs API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-trailer
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.local.example .env.local
```

Add your API configuration to `.env.local`:
```
NEXT_PUBLIC_API_BASE=https://chore-api-611389647575.us-central1.run.app
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

- `POST /api/tts-proxy` - Generate chore instruction audio


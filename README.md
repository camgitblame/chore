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
- ElevenLabs API key (keep this secure and never commit to version control)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd chore-app
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
```bash
# Replace with your actual API endpoint
NEXT_PUBLIC_API_BASE=https://your-api-endpoint.com

# Add your ElevenLabs API key (NEVER commit this file to git)
ELEVENLABS_API_KEY=your_api_key_here
```

**⚠️ Security Note**: Never commit `.env.local` or any files containing API keys to version control. The `.env.local` file is already included in `.gitignore` for security.

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

- `POST /api/tts-proxy` - Generate chore instruction audio (requires valid API key)

## Security Best Practices

- Never commit API keys or sensitive environment variables to version control
- Keep your `.env.local` file secure and don't share it publicly
- Regularly rotate your API keys
- Use environment-specific endpoints (development, staging, production)


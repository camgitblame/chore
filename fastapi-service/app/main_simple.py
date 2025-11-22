from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os, uuid, requests
from database import init_database, get_all_chores, get_chore_by_id, search_chores

app = FastAPI(title="Chore Coach API - Simple TTS")

# Initialize the database on startup
init_database()

# --- simple env config ---
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY")
CORS_ORIGIN = os.getenv("CORS_ORIGIN", "*")

# Configure CORS
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://choreapp.vercel.app",
    "https://*.vercel.app",
]

if CORS_ORIGIN == "*":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )


# --- models ---
class TTSIn(BaseModel):
    chore_id: Optional[str] = None
    text: Optional[str] = None
    voice_id: str
    stability: float = 0.4
    similarity: float = 0.8


def require_api_key(x_api_key: str = Header(default=None)):
    received_key = x_api_key.strip() if x_api_key else None
    expected_key = INTERNAL_API_KEY.strip() if INTERNAL_API_KEY else None

    if expected_key and received_key != expected_key:
        raise HTTPException(401, "Unauthorized")
    return True


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "chore-api-simple",
        "chores_available": len(get_all_chores()),
    }


# --- helpers ---
def chore_script(chore: dict) -> str:
    items = ", ".join(chore.get("items") or [])
    steps = chore.get("steps") or []
    steps_txt = " ".join([f"Step {i+1}: {s}." for i, s in enumerate(steps)])
    items_txt = f"You'll need: {items}. " if items else ""
    return f'{chore["title"]}. Estimated time: {chore.get("time_min",0)} minutes. {items_txt}{steps_txt}'.strip()[
        :1500
    ]


async def edge_tts_generate(text: str, voice: str = "en-US-AriaNeural") -> bytes:
    """Generate TTS using Microsoft Edge TTS (completely free)"""
    import edge_tts
    import tempfile

    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        communicate = edge_tts.Communicate(text[:1500], voice)
        await communicate.save(tmp_path)

        with open(tmp_path, "rb") as f:
            audio_data = f.read()

        os.unlink(tmp_path)

        return audio_data
    except Exception as e:
        raise HTTPException(500, f"TTS generation failed: {str(e)}")


# --- routes ---
@app.get("/chores")
def list_chores(q: str = "", response: Response = None):
    if q:
        res = search_chores(q.lower())
    else:
        res = get_all_chores()

    if response:
        response.headers["Cache-Control"] = "public, max-age=300"
        response.headers["X-Cache-Status"] = "HIT"

    return {"chores": res}


@app.get("/chores/{chore_id}")
def get_chore(chore_id: str):
    chore = get_chore_by_id(chore_id)
    if chore:
        return chore
    raise HTTPException(404, "Chore not found")


@app.post("/tts")
async def tts(payload: TTSIn, _=Depends(require_api_key)):
    # Map voice_id to Edge TTS voices
    voice_map = {
        "21m00Tcm4TlvDq8ikWAM": "en-US-AriaNeural",
        "default": "en-US-AriaNeural",
        "male": "en-US-GuyNeural",
        "female": "en-US-JennyNeural",
        "british": "en-GB-SoniaNeural",
    }

    voice = voice_map.get(payload.voice_id, "en-US-AriaNeural")

    if payload.text:
        audio = await edge_tts_generate(payload.text, voice)
    else:
        if not payload.chore_id:
            raise HTTPException(400, "Provide chore_id or text")
        chore = get_chore_by_id(payload.chore_id)
        if not chore:
            raise HTTPException(404, "Chore not found")
        script = chore_script(chore)
        audio = await edge_tts_generate(script, voice)

    return Response(audio, media_type="audio/mpeg")

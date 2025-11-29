from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os, uuid, requests
from database import init_database, get_all_chores, get_chore_by_id, search_chores
from groq_rag import groq_rag

app = FastAPI(title="Chore Coach API - Simple TTS + Groq RAG")

# Initialize the database on startup
init_database()

# Preload chores into memory to make initial /chores responses faster
CHORES_CACHE = []


@app.on_event("startup")
def preload_chores():
    """Load chores into memory once at startup to serve quickly."""
    global CHORES_CACHE
    try:
        CHORES_CACHE = get_all_chores()
    except Exception:
        CHORES_CACHE = []


# --- env config ---
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


class AdviceRequest(BaseModel):
    chore_id: str
    user_context: Optional[str] = ""


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
    """Generate TTS using Google Translate TTS"""
    from gtts import gTTS
    import io

    try:
        # Map voice preferences to languages
        lang = "en"  # Default English
        tld = "com"  # Top-level domain for accent

        if "GB" in voice or "british" in voice.lower():
            tld = "co.uk"  # British accent
        elif "AU" in voice:
            tld = "com.au"  # Australian accent

        # Generate speech
        tts = gTTS(text=text[:1500], lang=lang, tld=tld, slow=False)

        # Save to bytes buffer
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        return audio_buffer.read()
    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        print(f"TTS Error: {str(e)}")
        print(f"Full traceback: {error_details}")
        raise HTTPException(500, f"TTS generation failed: {str(e)}")


# --- routes ---
@app.get("/chores")
def list_chores(q: str = "", response: Response = None):
    """Return chores. If query provided, perform search; otherwise return
    preloaded chores from memory.
    """
    if q:
        # For searches, fall back to DB search (lightweight)
        res = search_chores(q.lower())
        cache_status = "MISS"
    else:
        # Serve preloaded chores for fastest possible response
        res = CHORES_CACHE
        cache_status = "HIT"

    if response:
        # Small cache header for clients / CDNs
        response.headers["Cache-Control"] = "public, max-age=300"
        response.headers["X-Cache-Status"] = cache_status

    return {"chores": res}


@app.get("/chores/static")
def chores_static(response: Response = None):
    """Explicit endpoint that serves the in-memory chores cache."""
    if response:
        response.headers["Cache-Control"] = "public, max-age=3600"
        response.headers["X-Cache-Status"] = "HIT"

    return {"chores": CHORES_CACHE}


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


@app.post("/advice")
def get_advice(payload: AdviceRequest, _=Depends(require_api_key)):
    """Get AI-powered advice using Groq"""
    chore = get_chore_by_id(payload.chore_id)
    if not chore:
        raise HTTPException(404, "Chore not found")

    advice = groq_rag.get_advice(chore, payload.user_context)

    return {
        "advice": advice,
        "chore_id": payload.chore_id,
        "rag_available": groq_rag.is_available(),
    }


@app.get("/advice/status")
def advice_status():
    """Check if advice generation is available"""
    return {
        "advice_available": groq_rag.is_available(),
        "service": "groq",
        "model": "llama-3.1-8b-instant",
    }

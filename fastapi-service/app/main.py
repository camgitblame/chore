from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os, uuid, requests
from database import init_database, get_all_chores, get_chore_by_id, search_chores
from rag.advice_generator import advice_generator

app = FastAPI(title="Chore Coach API")

# Initialize the database on startup
init_database()

# --- simple env config ---
INTERNAL_API_KEY = os.getenv(
    "INTERNAL_API_KEY"
)  # your private key between Next.js and FastAPI
ELEVEN_KEY = os.getenv("ELEVENLABS_API_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME", "")
STORE_TO_GCS = os.getenv("STORE_TO_GCS", "true").lower() == "true"
CORS_ORIGIN = os.getenv("CORS_ORIGIN", "*")

# Configure CORS to allow Vercel domains and local development
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://choreapp.vercel.app",
    "https://*.vercel.app",
]

# If CORS_ORIGIN is set to "*", allow all origins, otherwise use specific origins
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
    # Either reference a chore…
    chore_id: Optional[str] = None
    # …or send a free-form text to speak (e.g., congrats)
    text: Optional[str] = None
    voice_id: str
    stability: float = 0.4
    similarity: float = 0.8


class AdviceRequest(BaseModel):
    chore_id: str
    user_context: Optional[str] = ""


def require_api_key(x_api_key: str = Header(default=None)):
    # Require a shared secret header from Next.js server route
    # Strip whitespace from both keys to handle any secret formatting issues
    received_key = x_api_key.strip() if x_api_key else None
    expected_key = INTERNAL_API_KEY.strip() if INTERNAL_API_KEY else None

    if expected_key and received_key != expected_key:
        raise HTTPException(401, "Unauthorized")
    return True


@app.get("/health")
async def health_check():
    """Health check endpoint to keep Cloud Run warm"""
    return {
        "status": "healthy",
        "service": "chore-api",
        "chores_available": len(get_all_chores())
    }

@app.get("/debug/env")
async def debug_env():
    return {
        "has_internal_api_key": bool(INTERNAL_API_KEY),
        "internal_api_key_length": len(INTERNAL_API_KEY) if INTERNAL_API_KEY else 0,
        "has_eleven_key": bool(ELEVEN_KEY),
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


def upload_to_gcs_and_sign(data: bytes, content_type: str = "audio/mpeg") -> str:
    from google.cloud import storage

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    key = f"audio/{uuid.uuid4()}.mp3"
    blob = bucket.blob(key)
    blob.upload_from_string(data, content_type=content_type)
    # 1-hour signed URL
    return blob.generate_signed_url(version="v4", expiration=3600)


def eleven_tts(text: str, voice_id: str, stability: float, similarity: float) -> bytes:
    if not ELEVEN_KEY:
        raise HTTPException(500, "Missing ELEVENLABS_API_KEY")

    # Strip whitespace from API key to handle any secret formatting issues
    api_key = ELEVEN_KEY.strip() if ELEVEN_KEY else ""
    if not api_key:
        raise HTTPException(500, "Invalid ELEVENLABS_API_KEY")

    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={
            "xi-api-key": api_key,
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
        },
        json={
            "text": text[:1500],
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {"stability": stability, "similarity_boost": similarity},
        },
        timeout=60,
    )
    if r.status_code != 200:
        raise HTTPException(r.status_code, r.text)
    return r.content


# --- routes ---
@app.get("/chores")
def list_chores(q: str = "", response: Response = None):
    if q:
        res = search_chores(q.lower())
    else:
        res = get_all_chores()
    
    # Add cache headers for client-side caching
    if response:
        response.headers["Cache-Control"] = "public, max-age=300"  # 5 minute cache
        response.headers["X-Cache-Status"] = "HIT"
    
    return {"chores": res}


@app.get("/chores/{chore_id}")
def get_chore(chore_id: str):
    chore = get_chore_by_id(chore_id)
    if chore:
        return chore
    raise HTTPException(404, "Chore not found")


@app.post("/tts")
def tts(payload: TTSIn, _=Depends(require_api_key)):
    # If caller passed text, speak it directly (used for “congrats”)
    if payload.text:
        audio = eleven_tts(
            payload.text, payload.voice_id, payload.stability, payload.similarity
        )
    else:
        # Else read a chore by id
        if not payload.chore_id:
            raise HTTPException(400, "Provide chore_id or text")
        chore = get_chore_by_id(payload.chore_id)
        if not chore:
            raise HTTPException(404, "Chore not found")
        script = chore_script(chore)
        audio = eleven_tts(
            script, payload.voice_id, payload.stability, payload.similarity
        )

    if STORE_TO_GCS:
        if not BUCKET_NAME:
            raise HTTPException(500, "Missing BUCKET_NAME")
        url = upload_to_gcs_and_sign(audio)
        return JSONResponse({"audio_url": url, "bytes": len(audio)})
    else:
        return Response(audio, media_type="audio/mpeg")


@app.post("/advice")
def get_advice(payload: AdviceRequest, _=Depends(require_api_key)):
    """Get AI-powered advice for a specific chore"""
    chore = get_chore_by_id(payload.chore_id)
    if not chore:
        raise HTTPException(404, "Chore not found")

    advice = advice_generator.get_chore_advice(chore, payload.user_context)

    return {
        "advice": advice,
        "chore_id": payload.chore_id,
        "rag_available": advice_generator.is_available(),
    }


@app.get("/advice/status")
def advice_status():
    """Check if advice generation is available"""
    return {
        "advice_available": advice_generator.is_available(),
        "ollama_available": advice_generator.ollama_client.is_available(),
        "vector_store_available": advice_generator.vector_store.is_available(),
        "knowledge_count": advice_generator.vector_store.get_collection_count(),
    }

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os, uuid, requests

app = FastAPI(title="Chore Coach API")

# --- simple env config ---
INTERNAL_API_KEY = os.getenv(
    "INTERNAL_API_KEY"
)  # your private key between Next.js and FastAPI
ELEVEN_KEY = os.getenv("ELEVENLABS_API_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME", "")
STORE_TO_GCS = os.getenv("STORE_TO_GCS", "true").lower() == "true"
CORS_ORIGIN = os.getenv("CORS_ORIGIN", "*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ORIGIN] if CORS_ORIGIN != "*" else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- tiny in-memory catalog (could load from JSON/file/db later) ---
CHORES = [
    {
        "id": "microwave",
        "title": "Clean the microwave",
        "items": ["Bowl", "Water", "Vinegar or lemon", "Cloth"],
        "steps": [
            "Fill a bowl with water and a splash of vinegar",
            "Microwave on high for 3 minutes",
            "Let sit 1 minute to steam",
            "Wipe walls, ceiling, and plate",
            "Dry with a cloth",
        ],
        "time_min": 8,
    },
    {
        "id": "desk",
        "title": "Organize your desk",
        "items": ["Trash bag", "Microfiber cloth"],
        "steps": [
            "Put trash in the bag",
            "Group pens, cables, and papers",
            "Wipe the surface",
            "Return only daily items to the desk",
            "Stash the rest in a drawer or box",
        ],
        "time_min": 10,
    },
]


# --- models ---
class TTSIn(BaseModel):
    # Either reference a chore…
    chore_id: Optional[str] = None
    # …or send a free-form text to speak (e.g., congrats)
    text: Optional[str] = None
    voice_id: str
    stability: float = 0.4
    similarity: float = 0.8


def require_api_key(x_api_key: str = Header(default=None)):
    # Optional: require a shared secret header from your Next.js server route
    if INTERNAL_API_KEY and x_api_key != INTERNAL_API_KEY:
        raise HTTPException(401, "Unauthorized")
    return True


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
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={
            "xi-api-key": ELEVEN_KEY,
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
def list_chores(q: str = ""):
    q = (q or "").lower()
    res = [c for c in CHORES if q in c["title"].lower()]
    return {"chores": res}


@app.get("/chores/{chore_id}")
def get_chore(chore_id: str):
    for c in CHORES:
        if c["id"] == chore_id:
            return c
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
        chore = next((c for c in CHORES if c["id"] == payload.chore_id), None)
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

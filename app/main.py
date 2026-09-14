from datetime import datetime, timezone
from pathlib import Path
import json
import uuid
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .config import settings
from .db import connection, init_db
from .schemas import GenerationRequest
from .engines.types import SynthesisOptions

app = FastAPI(title="VoiceForge", version="0.1.0")
CONSENT = "I confirm that this is my voice or I have explicit permission to clone it."
ALLOWED_AUDIO = {"audio/wav","audio/x-wav","audio/mpeg","audio/mp4","audio/ogg","audio/webm"}

@app.on_event("startup")
def startup():
    init_db()

@app.get("/api/health")
def health():
    return {"status":"ok","engine":settings.voice_engine}

@app.get("/api/voices")
def voices():
    with connection() as con:
        return [{"id":x["id"],"name":x["name"],"created_at":x["created_at"]} for x in con.execute("SELECT * FROM voices ORDER BY created_at DESC")]

@app.post("/api/voices")
async def create_voice(name: str=Form(...), consent: bool=Form(...), consent_phrase: str=Form(...), sample: UploadFile=File(...)):
    if not consent or consent_phrase.strip() != CONSENT:
        raise HTTPException(400, "Exact consent statement is required")
    if sample.content_type not in ALLOWED_AUDIO:
        raise HTTPException(415, "Upload WAV, MP3, M4A, OGG or WebM audio")
    voice_id = uuid.uuid4().hex
    suffix = Path(sample.filename or "sample.wav").suffix.lower()[:8] or ".wav"
    target = settings.data_dir / "uploads" / f"{voice_id}{suffix}"
    size = 0
    with target.open("wb") as out:
        while chunk := await sample.read(1024 * 1024):
            size += len(chunk)
            if size > settings.max_upload_mb * 1024 * 1024:
                out.close()
                target.unlink(missing_ok=True)
                raise HTTPException(413, "Audio file is too large")
            out.write(chunk)
    now = datetime.now(timezone.utc).isoformat()
    with connection() as con:
        con.execute("INSERT INTO voices VALUES (?,?,?,?,?)",(voice_id,name.strip()[:80],str(target),CONSENT,now))
    return {"id":voice_id,"name":name.strip(),"created_at":now}

@app.delete("/api/voices/{voice_id}")
def delete_voice(voice_id: str):
    with connection() as con:
        row = con.execute("SELECT sample_path FROM voices WHERE id=?",(voice_id,)).fetchone()
        if not row:
            raise HTTPException(404,"Voice not found")
        Path(row["sample_path"]).unlink(missing_ok=True)
        con.execute("DELETE FROM voices WHERE id=?",(voice_id,))
    return {"deleted":True}

@app.post("/api/generate")
def generate(req: GenerationRequest):
    with connection() as con:
        voice = con.execute("SELECT * FROM voices WHERE id=?",(req.voice_id,)).fetchone()
    if not voice:
        raise HTTPException(404,"Voice not found")
    generation_id = uuid.uuid4().hex
    output = settings.data_dir / "outputs" / f"{generation_id}.wav"
    options = SynthesisOptions(**req.model_dump(exclude={"voice_id","text"}))
    try:
        if settings.voice_engine == "mock":
            from .engines.mock import synthesize
        elif settings.voice_engine == "openvoice":
            from .engines.openvoice import synthesize
        else:
            raise RuntimeError("Unsupported VOICE_ENGINE")
        synthesize(Path(voice["sample_path"]), req.text, output, options)
    except Exception as exc:
        raise HTTPException(503, str(exc))
    now = datetime.now(timezone.utc).isoformat()
    output.with_suffix(".json").write_text(json.dumps({"synthetic":True,"voice_id":req.voice_id,"created_at":now,"settings":options.__dict__},indent=2))
    with connection() as con:
        con.execute("INSERT INTO generations VALUES (?,?,?,?,?,?,?)",(generation_id,req.voice_id,req.text[:100],req.emotion,req.language,str(output),now))
    return {"id":generation_id,"audio_url":f"/media/{output.name}","synthetic":True}

@app.get("/api/generations")
def generations():
    with connection() as con:
        return [dict(x) | {"audio_url":f"/media/{Path(x['output_path']).name}"} for x in con.execute("SELECT * FROM generations ORDER BY created_at DESC LIMIT 50")]

@app.get("/media/{filename}")
def media(filename: str):
    path = settings.data_dir / "outputs" / Path(filename).name
    if not path.exists() or path.suffix != ".wav":
        raise HTTPException(404,"Audio not found")
    return FileResponse(path,media_type="audio/wav",filename=f"synthetic-{path.name}")

app.mount("/", StaticFiles(directory=Path(__file__).parent/"static",html=True), name="static")

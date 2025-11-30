import os
import json
import asyncio
from typing import Optional, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .app import run_job, get_manifest, list_chunks, get_chunk_detail, reprocess_chunk


app = FastAPI(title="Localizer API", description="REST endpoints for video localization")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class StartJobRequest(BaseModel):
    input_path: str
    source: str
    target: str
    job_id: str
    course_id: str
    mode: str = "fast"
    voice: Optional[str] = None  # explicit voice or "male"/"female"


class FinalizeRequest(BaseModel):
    job_id: Optional[str] = None
    manifest_path: Optional[str] = None


class ResynthesizeRequest(BaseModel):
    job_id: Optional[str] = None
    manifest_path: Optional[str] = None
    out_dir: Optional[str] = None
    finalize: bool = False
    voice: Optional[str] = None


class FeedbackRequest(BaseModel):
    job_id: str
    chunk_index: Optional[int] = None
    corrected_text_translated: Optional[str] = None
    corrected_pronunciation: Optional[dict] = None
    rating: Optional[int] = None  # 1-5
    comment: Optional[str] = None


# -----------------
# Voice mapping utilities
# -----------------
VOICE_MAP_PATH = os.path.join(os.path.dirname(__file__), "sample_data", "voice_map.json")
try:
    import edge_tts
except Exception:
    edge_tts = None

# In-memory cache to avoid repeated edge-tts voice discovery
EDGE_VOICES_CACHE = None


def _load_voice_map() -> Dict[str, str]:
    if os.path.exists(VOICE_MAP_PATH):
        try:
            with open(VOICE_MAP_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_voice_map(vm: Dict[str, str]) -> None:
    os.makedirs(os.path.dirname(VOICE_MAP_PATH), exist_ok=True)
    with open(VOICE_MAP_PATH, "w", encoding="utf-8") as f:
        json.dump(vm, f, ensure_ascii=False, indent=2)


async def _resolve_gender_voice(lang: str, gender: str) -> Optional[str]:
    if edge_tts is None:
        return None
    try:
        global EDGE_VOICES_CACHE
        if EDGE_VOICES_CACHE is None:
            EDGE_VOICES_CACHE = await edge_tts.list_voices()
        voices = EDGE_VOICES_CACHE
        base = lang.split("-")[0].lower()
        gen = gender.lower()
        candidates = []
        for v in voices:
            locale = (v.get("Locale") or "").lower()
            short = v.get("ShortName")
            g = (v.get("Gender") or "").lower()
            if locale.startswith(base):
                score = 0
                if "neural" in (short or "").lower():
                    score += 2
                if g == gen:
                    score += 1
                candidates.append((score, short))
        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            return candidates[0][1]
    except Exception:
        return None
    return None


class VoiceSetRequest(BaseModel):
    voice: Optional[str] = None
    gender: Optional[str] = None


@app.get("/voices")
async def list_voices(lang: Optional[str] = None) -> Dict[str, Any]:
    if edge_tts is None:
        return {"voices": [], "error": "edge-tts not available"}
    try:
        global EDGE_VOICES_CACHE
        if EDGE_VOICES_CACHE is None:
            EDGE_VOICES_CACHE = await edge_tts.list_voices()
        voices = EDGE_VOICES_CACHE
        if lang:
            base = lang.split("-")[0].lower()
            voices = [v for v in voices if (v.get("Locale") or "").lower().startswith(base)]
        slim = [
            {
                "ShortName": v.get("ShortName"),
                "Locale": v.get("Locale"),
                "Gender": v.get("Gender"),
            }
            for v in voices
        ]
        return {"voices": slim}
    except Exception as e:
        return {"voices": [], "error": str(e)}


@app.get("/voice/{lang}")
async def get_voice_mapping(lang: str) -> Dict[str, Any]:
    vm = _load_voice_map()
    base = lang.split("-")[0]
    return {"lang": lang, "voice": vm.get(lang) or vm.get(base)}


@app.put("/voice/{lang}")
async def set_voice_mapping(lang: str, req: VoiceSetRequest) -> Dict[str, Any]:
    vm = _load_voice_map()
    chosen = req.voice
    if not chosen and req.gender:
        chosen = await _resolve_gender_voice(lang, req.gender)
    if not chosen:
        raise HTTPException(status_code=400, detail="Provide 'voice' or valid 'gender'")
    vm[lang] = chosen
    base = lang.split("-")[0]
    vm.setdefault(base, chosen)
    _save_voice_map(vm)
    return {"ok": True, "lang": lang, "voice": chosen}


async def _apply_voice_param(target: str, voice: Optional[str]) -> None:
    if not voice:
        return
    vm = _load_voice_map()
    if voice.lower() in ("male", "female"):
        chosen = await _resolve_gender_voice(target, voice)
        if chosen:
            vm[target] = chosen
            vm.setdefault(target.split("-")[0], chosen)
    else:
        vm[target] = voice
        vm.setdefault(target.split("-")[0], voice)
    _save_voice_map(vm)


# -----------------
# Job endpoints
# -----------------
@app.post("/jobs/start")
async def start_job(req: StartJobRequest) -> Dict[str, Any]:
    await _apply_voice_param(req.target, req.voice)
    manifest_path = run_job(
        input_path=req.input_path,
        source=req.source,
        target=req.target,
        job_id=req.job_id,
        course_id=req.course_id,
        mode=req.mode,
    )
    return {"manifest_path": manifest_path}


@app.get("/jobs/{job_id}/manifest")
async def get_job_manifest(job_id: str) -> Dict[str, Any]:
    return get_manifest(job_id)


@app.get("/jobs/{job_id}/chunks")
async def get_job_chunks(job_id: str) -> Dict[str, Any]:
    return {"chunks": list_chunks(job_id)}


@app.get("/jobs/{job_id}/chunks/{index}")
async def get_chunk(job_id: str, index: int) -> Dict[str, Any]:
    return get_chunk_detail(job_id, index)


@app.post("/jobs/resynthesize", response_model=None)
async def resynthesize(req: ResynthesizeRequest):
    manifest_path: Optional[str]
    if req.manifest_path:
        manifest_path = req.manifest_path
    elif req.job_id:
        base = os.path.join("localizer", "output", req.job_id)
        manifest_path = os.path.join(base, "manifest.json")
    else:
        raise HTTPException(status_code=400, detail="Provide job_id or manifest_path")

    await _apply_voice_param(get_manifest(os.path.basename(os.path.dirname(manifest_path))).get("target_lang", ""), req.voice)
    res = resynthesize_job(manifest_path, req.out_dir)
    if req.finalize:
        from .resynthesize import finalize_resynthesis
        final_out = finalize_resynthesis(manifest_path, res["manifest"])
        try:
            cleanup_job_artifacts(manifest_path)
        except Exception:
            pass
        return FileResponse(final_out, media_type="video/mp4", filename=os.path.basename(final_out))
    return res


@app.post("/jobs/finalize")
async def finalize(req: FinalizeRequest) -> FileResponse:
    manifest_path: Optional[str]
    if req.manifest_path:
        manifest_path = req.manifest_path
    elif req.job_id:
        base = os.path.join("localizer", "output", req.job_id)
        manifest_path = os.path.join(base, "manifest.json")
    else:
        raise HTTPException(status_code=400, detail="Provide job_id or manifest_path")

    # For standalone finalize, we can reuse finalize_resynthesis but we need manifest data
    # Or we can just rely on run_job if we want to re-run everything, but finalize implies just merge.
    # Let's load manifest and call finalize_resynthesis which handles the merge logic.
    from .resynthesize import finalize_resynthesis
    m = get_manifest(os.path.basename(os.path.dirname(manifest_path)))
    final_out = finalize_resynthesis(manifest_path, m)
    
    try:
        cleanup_job_artifacts(manifest_path)
    except Exception:
        pass
    return FileResponse(final_out, media_type="video/mp4", filename=os.path.basename(final_out))


# Feedback capture (MVP)
@app.post("/feedback")
async def submit_feedback(req: FeedbackRequest) -> Dict[str, Any]:
    base_out = os.path.join(os.path.dirname(__file__), "output", req.job_id)
    os.makedirs(base_out, exist_ok=True)
    fb_path = os.path.join(base_out, "feedback.json")
    payload = req.dict()
    try:
        existing = []
        if os.path.exists(fb_path):
            with open(fb_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        existing.append(payload)
        with open(fb_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        return {"ok": True, "count": len(existing)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Job stats
@app.get("/jobs/{job_id}/stats")
async def job_stats(job_id: str) -> Dict[str, Any]:
    return get_job_stats(job_id)


# Captions export: zip of SRT or VTT
@app.get("/captions/{job_id}")
async def export_captions(job_id: str, format: str = "srt") -> FileResponse:
    fmt = format.lower().strip()
    if fmt not in ("srt", "vtt"):
        raise HTTPException(status_code=400, detail="format must be 'srt' or 'vtt'")
    base_out = os.path.join(os.path.dirname(__file__), "output", job_id)
    tts_dir = os.path.join(base_out, "tts")
    if not os.path.isdir(tts_dir):
        raise HTTPException(status_code=404, detail="tts directory not found")

    import zipfile
    tmp_zip = os.path.join(base_out, f"captions_{fmt}.zip")
    # Convert SRT to VTT inline if needed
    def srt_to_vtt(srt_text: str) -> str:
        lines = srt_text.splitlines()
        out = ["WEBVTT"]
        for ln in lines:
            if "-->" in ln:
                out.append(ln.replace(",", "."))
            else:
                out.append(ln)
        return "\n".join(out)

    try:
        with zipfile.ZipFile(tmp_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for name in sorted(os.listdir(tts_dir)):
                if not name.lower().endswith(".srt"):
                    continue
                srt_path = os.path.join(tts_dir, name)
                with open(srt_path, "r", encoding="utf-8") as f:
                    srt_txt = f.read()
                if fmt == "srt":
                    zf.writestr(name, srt_txt)
                else:
                    vtt_name = name.replace(".srt", ".vtt")
                    zf.writestr(vtt_name, srt_to_vtt(srt_txt))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return FileResponse(tmp_zip, media_type="application/zip", filename=os.path.basename(tmp_zip))


# Seed Indian language voices via dynamic discovery
@app.post("/voice/seed/india")
async def seed_indian_voices(gender: str = "male") -> Dict[str, Any]:
    langs = [
        "hi-IN",
        "bn-IN",
        "ta-IN",
        "te-IN",
        "mr-IN",
        "gu-IN",
        "pa-IN",
        "kn-IN",
        "ml-IN",
        "or-IN",
    ]
    vm = _load_voice_map()
    applied = []
    for lang in langs:
        try:
            chosen = await _resolve_gender_voice(lang, gender)
            if chosen:
                vm[lang] = chosen
                vm.setdefault(lang.split("-")[0], chosen)
                applied.append({"lang": lang, "voice": chosen})
        except Exception:
            continue
    _save_voice_map(vm)
    return {"ok": True, "applied": applied}


@app.post("/jobs/upload")
async def upload_and_localize(
    file: UploadFile = File(...),
    source: str = Form("en"),
    target: str = Form("hi"),
    course_id: str = Form("general"),
    job_id: Optional[str] = Form(None),
    mode: str = Form("fast"),
    voice: Optional[str] = Form(None),
) -> Dict[str, Any]:
    # Apply voice preference if provided
    await _apply_voice_param(target, voice)

    uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    filename = file.filename or "upload.mp4"
    input_path = os.path.join(uploads_dir, filename)
    with open(input_path, "wb") as f:
        f.write(await file.read())

    job = job_id or os.path.splitext(filename)[0]
    
    # Run blocking job in threadpool to avoid blocking event loop
    # This also allows asyncio.run() in tts.py to work correctly (since it runs in a separate thread)
    from fastapi.concurrency import run_in_threadpool
    manifest_path = await run_in_threadpool(
        run_job,
        input_path=input_path,
        source=source,
        target=target,
        job_id=job,
        course_id=course_id,
        mode=mode,
    )
    
    # Reload manifest to get cloudinary URL
    with open(manifest_path, "r", encoding="utf-8") as f:
        m = json.load(f)
    
    cloudinary_url = m.get("cloudinary_url")
    if not cloudinary_url:
        raise HTTPException(status_code=500, detail="Cloudinary URL not found in manifest")
    
    return {
        "cloudinary_url": cloudinary_url,
        "job_id": job,
        "manifest_path": manifest_path,
        "status": "success"
    }


# Alias endpoint for convenience
@app.post("/upload")
async def upload_alias(
    file: UploadFile = File(...),
    source: str = Form("en"),
    target: str = Form("hi"),
    course_id: str = Form("general"),
    job_id: Optional[str] = Form(None),
    mode: str = Form("fast"),
    voice: Optional[str] = Form(None),
) -> Dict[str, Any]:
    return await upload_and_localize(file, source, target, course_id, job_id, mode, voice)

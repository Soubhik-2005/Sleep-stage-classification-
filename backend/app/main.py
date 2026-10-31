import uuid
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from . import config
from .database.store import store
from .services.model_service import model_service
from .services.analysis_service import run_analysis, STAGES
from .utils.file_validation import save_edf
from ml.src import config as C

app = FastAPI(title="SleepAI API", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=config.CORS_ORIGINS,
                   allow_methods=["*"], allow_headers=["*"])


def _rec_or_404(rec_id):
    rec = store.get("recordings", rec_id)
    if not rec:
        raise HTTPException(404, "Recording not found")
    return rec


def _public(rec):
    return {k: v for k, v in rec.items() if k != "filePath"}


@app.get("/api/health")
def health():
    return {"status": "ok", "database": store.kind, "modelAvailable": model_service.available,
            "classes": STAGES, "channels": C.CHANNELS}


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    rec_id = "rec_" + uuid.uuid4().hex[:10]
    dest = config.UPLOAD_DIR / f"{rec_id}.edf"
    size = await save_edf(file, dest)
    rec = {"_id": rec_id, "filename": Path(file.filename).name, "filePath": str(dest), "sizeBytes": size,
           "status": "uploaded", "progress": 0, "message": "Uploaded", "duration": None,
           "uploadedAt": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    store.put("recordings", rec)
    return {"status": "success", "recordingId": rec_id, "recording": _public(rec)}


@app.post("/api/analyze/{rec_id}", status_code=202)
def analyze(rec_id: str, background: BackgroundTasks):
    rec = _rec_or_404(rec_id)
    if rec["status"] == "processing":
        raise HTTPException(409, "Analysis already running")
    if not model_service.available:
        raise HTTPException(503, "No trained model found. Train one first: python -m ml.src.train --download 10")
    store.update("recordings", rec_id, {"status": "processing", "progress": 1, "message": "Queued"})
    background.add_task(run_analysis, rec_id)          # runs after the response is sent
    return {"status": "accepted", "recordingId": rec_id}


@app.get("/api/results/{rec_id}")
def results(rec_id: str):
    rec = _rec_or_404(rec_id)
    pred = store.get("predictions", f"pred_{rec_id}") if rec["status"] == "completed" else None
    if pred:
        pred = {k: v for k, v in pred.items() if k != "_id"}
    return {"status": "success", "recording": _public(rec), "prediction": pred, "classes": STAGES}


@app.get("/api/recordings/{rec_id}/signal")
def signal(rec_id: str, epoch: int = Query(0, ge=0), count: int = Query(1, ge=1, le=5)):
    rec = _rec_or_404(rec_id)
    f = config.PROCESSED_DIR / f"{rec_id}.npy"
    if rec["status"] != "completed" or not f.exists():
        raise HTTPException(409, "Signal not available until analysis completes")
    X = np.load(f, mmap_mode="r")
    if epoch >= len(X):
        raise HTTPException(404, "Epoch out of range")
    chunk = np.asarray(X[epoch:epoch + count], dtype=np.float32)       # (n, T, C)
    data = chunk.reshape(-1, chunk.shape[-1]).T                         # (C, n*T)
    return {"epoch": epoch, "count": len(chunk), "totalEpochs": len(X), "sfreq": rec["sfreq"],
            "startSec": epoch * C.EPOCH_SEC, "units": "uV", "channels": rec["channels"],
            "data": np.round(data, 2).tolist()}


@app.get("/api/history")
def history():
    out = []
    for rec in sorted(store.list("recordings"), key=lambda r: r["uploadedAt"], reverse=True):
        item = _public(rec)
        if rec["status"] == "completed":
            p = store.get("predictions", f"pred_{rec['_id']}")
            item["summary"] = p["stats"] if p else None
        out.append(item)
    return {"status": "success", "recordings": out}


@app.delete("/api/recordings/{rec_id}")
def delete(rec_id: str):
    rec = _rec_or_404(rec_id)
    Path(rec["filePath"]).unlink(missing_ok=True)
    (config.PROCESSED_DIR / f"{rec_id}.npy").unlink(missing_ok=True)
    store.delete("predictions", f"pred_{rec_id}")
    store.delete("recordings", rec_id)
    return {"status": "deleted", "recordingId": rec_id}

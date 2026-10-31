import traceback
from datetime import datetime, timezone
import numpy as np
import mne
from .. import config
from ..database.store import store
from .model_service import model_service
from ml.src import config as C
from ml.src.preprocessing import preprocess_raw, segment

STAGES = C.CLASS_NAMES
EPOCH_MIN = C.EPOCH_SEC / 60.0


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sleep_stats(stages):
    """Standard sleep-architecture summary from a list of stage indices (0=W..4=REM)."""
    s = np.asarray(stages)
    n = len(s)
    mins = {STAGES[i]: round(float((s == i).sum() * EPOCH_MIN), 1) for i in range(5)}
    pct = {k: round(100 * v / (n * EPOCH_MIN), 1) if n else 0 for k, v in mins.items()}
    asleep = np.where(s != 0)[0]
    tst = round(float(len(asleep) * EPOCH_MIN), 1)
    tib = round(n * EPOCH_MIN, 1)
    latency = round(float(asleep[0] * EPOCH_MIN), 1) if len(asleep) else None
    rem = np.where(s == 4)[0]
    rem_lat = round(float((rem[0] - asleep[0]) * EPOCH_MIN), 1) if len(rem) and len(asleep) else None
    waso = round(float((s[asleep[0]:] == 0).sum() * EPOCH_MIN), 1) if len(asleep) else 0
    return {"totalEpochs": n, "timeInBedMin": tib, "totalSleepMin": tst,
            "sleepEfficiency": round(100 * tst / tib, 1) if tib else 0,
            "sleepLatencyMin": latency, "remLatencyMin": rem_lat, "wasoMin": waso,
            "minutes": mins, "percent": pct,
            "lightSleepMin": round(mins["N1"] + mins["N2"], 1),
            "deepSleepMin": mins["N3"], "remMin": mins["REM"], "wakeMin": mins["Wake"]}


def _progress(rec_id, pct, msg):
    store.update("recordings", rec_id, {"progress": pct, "message": msg})


def run_analysis(rec_id):
    """Background job: EDF -> preprocess -> epochs -> CNN -> stats. Never raises."""
    try:
        rec = store.get("recordings", rec_id)
        store.update("recordings", rec_id, {"status": "processing", "progress": 5,
                                            "message": "Loading model", "error": None})
        cfg = model_service.load()

        _progress(rec_id, 15, "Reading EDF file")
        raw = mne.io.read_raw_edf(rec["filePath"], preload=True, verbose="ERROR")
        _progress(rec_id, 35, "Filtering and resampling")
        raw = preprocess_raw(raw, tuple(cfg["bandpass"]), cfg["sfreq"])
        X = segment(raw.get_data() * 1e6)                       # (N, 3000, C) in uV
        if len(X) == 0:
            raise ValueError("Recording is shorter than one 30-second epoch.")
        np.save(config.PROCESSED_DIR / f"{rec_id}.npy", X.astype(np.float16))

        _progress(rec_id, 60, f"Classifying {len(X)} epochs")
        probs = model_service.predict(X)
        stages = probs.argmax(1)

        stats = sleep_stats(stages)
        store.put("predictions", {
            "_id": f"pred_{rec_id}", "recordingId": rec_id, "modelVersion": cfg["model_version"],
            "syntheticModel": cfg.get("synthetic", False), "createdAt": now(),
            "totalEpochs": len(stages), "stageDistribution": stats["minutes"], "stats": stats,
            "stages": stages.tolist(),
            "confidence": np.round(probs.max(1), 4).tolist(),
            "probabilities": np.round(probs, 4).tolist(),
        })
        store.update("recordings", rec_id, {
            "status": "completed", "progress": 100, "message": "Done",
            "duration": int(len(X) * C.EPOCH_SEC), "sfreq": cfg["sfreq"],
            "channels": cfg["channels"], "completedAt": now()})
    except Exception as e:                                       # surface failures to the UI
        traceback.print_exc()
        store.update("recordings", rec_id, {"status": "failed", "message": "Analysis failed", "error": str(e)})

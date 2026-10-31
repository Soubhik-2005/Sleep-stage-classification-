"""Shared constants. Training and inference MUST use the same values."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / "ml" / "saved_models"
PROCESSED_DIR = ROOT / "dataset" / "processed"
RAW_DIR = ROOT / "dataset" / "raw"

SFREQ = 100.0                      # Hz, Sleep-EDF EEG/EOG rate
EPOCH_SEC = 30
SAMPLES = int(SFREQ * EPOCH_SEC)   # 3000
CHANNELS = ["EEG Fpz-Cz", "EEG Pz-Oz", "EOG horizontal"]
BANDPASS = (0.3, 35.0)
CLASS_NAMES = ["Wake", "N1", "N2", "N3", "REM"]
MODEL_VERSION = "cnn_v1"

# MNE annotation text -> unique event id -> class index (stage 3 and 4 merged into N3)
ANN_EVENT_ID = {
    "Sleep stage W": 1, "Sleep stage 1": 2, "Sleep stage 2": 3,
    "Sleep stage 3": 4, "Sleep stage 4": 5, "Sleep stage R": 6,
}
EVENT_TO_LABEL = {1: 0, 2: 1, 3: 2, 4: 3, 5: 3, 6: 4}
# "Sleep stage ?" and "Movement time" are intentionally absent -> excluded.

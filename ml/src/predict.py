"""Standalone inference: python -m ml.src.predict recording.edf"""
import json, sys
import numpy as np
import mne
from . import config as C
from .preprocessing import preprocess_raw, segment, normalize


def load_model_and_config():
    import tensorflow as tf
    cfg = json.loads((C.MODEL_DIR / "preprocessing_config.json").read_text())
    return tf.keras.models.load_model(C.MODEL_DIR / "sleep_stage_model.keras"), cfg


def edf_to_epochs(path, cfg):
    raw = mne.io.read_raw_edf(str(path), preload=True, verbose="ERROR")
    raw = preprocess_raw(raw, tuple(cfg["bandpass"]), cfg["sfreq"])
    return segment(raw.get_data() * 1e6)          # (N, 3000, C) in microvolts


def predict_probs(model, cfg, X_uv):
    return model.predict(normalize(X_uv, cfg["mean"], cfg["std"]), batch_size=64, verbose=0)


if __name__ == "__main__":
    model, cfg = load_model_and_config()
    X = edf_to_epochs(sys.argv[1], cfg)
    stages = predict_probs(model, cfg, X).argmax(1)
    print(" ".join(C.CLASS_NAMES[s][0] if s != 4 else "R" for s in stages))

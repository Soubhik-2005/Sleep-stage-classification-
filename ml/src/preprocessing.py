"""Signal preprocessing shared by training and the web backend."""
import numpy as np
from . import config as C


def pick_channels(raw, wanted=None):
    wanted = wanted or C.CHANNELS
    lookup = {n.lower().strip(): n for n in raw.ch_names}
    picked, missing = [], []
    for w in wanted:
        if w.lower() in lookup:
            picked.append(lookup[w.lower()])
        else:
            missing.append(w)
    if missing:
        raise ValueError(f"Recording is missing required channel(s) {missing}. "
                         f"Available: {raw.ch_names}")
    raw.pick(picked)
    raw.reorder_channels(picked)
    return raw


def preprocess_raw(raw, bandpass=None, sfreq=None):
    """Select channels, band-pass filter, resample. Returns the (modified) Raw."""
    bandpass = bandpass or C.BANDPASS
    sfreq = sfreq or C.SFREQ
    pick_channels(raw)
    raw.filter(bandpass[0], bandpass[1], verbose="ERROR")
    if abs(raw.info["sfreq"] - sfreq) > 1e-6:
        raw.resample(sfreq, verbose="ERROR")
    return raw


def segment(data_uv, samples=None):
    """(C, T) -> (N, samples, C), dropping the incomplete tail."""
    samples = samples or C.SAMPLES
    n_ch, total = data_uv.shape
    n = total // samples
    x = data_uv[:, : n * samples].reshape(n_ch, n, samples)
    return np.ascontiguousarray(x.transpose(1, 2, 0), dtype=np.float32)


def normalize(X, mean, std):
    return ((X - np.asarray(mean, np.float32)) / (np.asarray(std, np.float32) + 1e-8)).astype(np.float32)

"""Load Sleep-EDF PSG + hypnogram pairs into (X, y) arrays."""
from pathlib import Path
import numpy as np
import mne
from . import config as C
from .preprocessing import preprocess_raw


def find_pairs(data_dir):
    """Match SC4001E0-PSG.edf with SC4001EC-Hypnogram.edf by their first 6 characters."""
    data_dir = Path(data_dir)
    hyps = {p.name[:6]: p for p in data_dir.rglob("*-Hypnogram.edf")}
    pairs = [(p, hyps[p.name[:6]]) for p in sorted(data_dir.rglob("*-PSG.edf")) if p.name[:6] in hyps]
    if not pairs:
        raise FileNotFoundError(f"No PSG/Hypnogram pairs found under {data_dir}")
    return pairs


def subject_id(psg_path):
    return Path(psg_path).name[:5]  # e.g. SC400 -> subject 00 (both nights share it)


def load_labelled(psg_path, hyp_path, trim_wake_epochs=60):
    """Return X (N, 3000, C) in microvolts and y (N,) in {0..4} for one recording."""
    raw = mne.io.read_raw_edf(str(psg_path), preload=True, verbose="ERROR")
    raw.set_annotations(mne.read_annotations(str(hyp_path)), emit_warning=False)
    raw = preprocess_raw(raw)
    events, _ = mne.events_from_annotations(
        raw, event_id=C.ANN_EVENT_ID, chunk_duration=float(C.EPOCH_SEC), verbose="ERROR")
    epochs = mne.Epochs(raw, events, event_id=C.ANN_EVENT_ID, tmin=0.0,
                        tmax=C.EPOCH_SEC - 1.0 / raw.info["sfreq"], baseline=None,
                        preload=True, on_missing="ignore", verbose="ERROR")
    X = (epochs.get_data() * 1e6).transpose(0, 2, 1).astype(np.float32)   # V -> uV, (N, T, C)
    y = np.array([C.EVENT_TO_LABEL[e] for e in epochs.events[:, 2]], dtype=np.int64)
    # Long wake periods before/after sleep dominate the class balance -> keep +-30 min around sleep.
    asleep = np.where(y != 0)[0]
    if len(asleep) and trim_wake_epochs is not None:
        lo, hi = max(0, asleep[0] - trim_wake_epochs), min(len(y), asleep[-1] + trim_wake_epochs + 1)
        X, y = X[lo:hi], y[lo:hi]
    return X, y


def load_cached(psg_path, hyp_path, cache_dir=None):
    cache_dir = Path(cache_dir or C.PROCESSED_DIR)
    cache_dir.mkdir(parents=True, exist_ok=True)
    f = cache_dir / (Path(psg_path).name[:6] + ".npz")
    if f.exists():
        d = np.load(f)
        return d["X"], d["y"]
    X, y = load_labelled(psg_path, hyp_path)
    np.savez_compressed(f, X=X, y=y)
    return X, y


def download_sleep_edf(n_subjects=10, path=None):
    """Download the Sleep-EDF (SC, 'age') recordings via MNE. Run on a machine with internet access."""
    from mne.datasets.sleep_physionet.age import fetch_data
    files = fetch_data(subjects=list(range(n_subjects)), recording=[1], path=str(path or C.RAW_DIR))
    return [(Path(p), Path(h)) for p, h in files]

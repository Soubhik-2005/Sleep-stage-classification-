"""Synthetic PSG generator for smoke-testing the pipeline WITHOUT the real dataset.
Models trained on this are NOT meaningful - use Sleep-EDF for real results."""
import numpy as np
from . import config as C

T = np.arange(C.SAMPLES) / C.SFREQ
_TRANS = np.array([  # rough Markov chain over W,N1,N2,N3,REM
    [.80, .15, .03, .00, .02], [.10, .50, .38, .00, .02], [.02, .05, .80, .10, .03],
    [.01, .00, .15, .84, .00], [.05, .05, .05, .00, .85]])


def _sine(f, amp, rng):
    return amp * np.sin(2 * np.pi * f * T + rng.uniform(0, 6.28))


def make_epoch(stage, rng):
    eeg = lambda: rng.normal(0, 4, C.SAMPLES)
    ch = [eeg(), eeg(), rng.normal(0, 3, C.SAMPLES)]
    for k in range(2):
        if stage == 0:   ch[k] += _sine(10, 14, rng) + _sine(20, 5, rng)
        elif stage == 1: ch[k] += _sine(6, 10, rng)
        elif stage == 2:
            ch[k] += _sine(3, 12, rng); s = rng.integers(500, 2000)
            ch[k][s:s + 100] += _sine(13, 25, rng)[:100]
        elif stage == 3: ch[k] += _sine(1.5, 70, rng) + _sine(0.8, 30, rng)
        else:            ch[k] += _sine(8, 6, rng) + _sine(11, 5, rng)
    if stage == 0:   ch[2] += _sine(0.5, 40, rng) * (rng.random() > .5)
    elif stage == 4: ch[2] += _sine(3, 40, rng) * (rng.random(C.SAMPLES) > .7)
    return np.stack(ch, axis=1)


def make_hypnogram(n_epochs, rng):
    y = [0]
    for _ in range(n_epochs - 1):
        y.append(rng.choice(5, p=_TRANS[y[-1]]))
    return np.array(y)


def make_recording(n_epochs=300, seed=0):
    rng = np.random.default_rng(seed)
    y = make_hypnogram(n_epochs, rng)
    X = np.stack([make_epoch(s, rng) for s in y]).astype(np.float32)
    return X, y


def make_dataset(n_subjects=6, n_epochs=300):
    Xs, ys, subj = [], [], []
    for s in range(n_subjects):
        X, y = make_recording(n_epochs, seed=s)
        Xs.append(X); ys.append(y); subj += [f"SYN{s:02d}"] * len(y)
    return np.concatenate(Xs), np.concatenate(ys), np.array(subj)


def write_demo_edf(path, X, y=None):
    """Write X (N,T,C) as an EDF. If y is given, also embed Sleep-EDF style annotations."""
    import mne
    from mne.export import export_raw
    data = X.reshape(-1, X.shape[2]).T * 1e-6  # uV -> V
    info = mne.create_info(C.CHANNELS, C.SFREQ, ch_types="eeg")
    raw = mne.io.RawArray(data, info, verbose="ERROR")
    if y is not None:
        names = ["Sleep stage W", "Sleep stage 1", "Sleep stage 2", "Sleep stage 3", "Sleep stage R"]
        names = [names[i] for i in y]
        raw.set_annotations(mne.Annotations(np.arange(len(y)) * C.EPOCH_SEC, C.EPOCH_SEC, names))
    export_raw(str(path), raw, fmt="edf", overwrite=True, verbose="ERROR")

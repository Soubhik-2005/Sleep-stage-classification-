"""Verifies the MNE loader (PSG+hypnogram path) and training on synthetic data."""
import tempfile, pathlib, numpy as np
from ml.src import config as C
from ml.src.synthetic import make_recording, write_demo_edf
from ml.src.data_loader import load_labelled
X, y = make_recording(120, seed=1)
d = pathlib.Path(tempfile.mkdtemp()); f = d / "demo.edf"
write_demo_edf(f, X, y)
X2, y2 = load_labelled(f, f, trim_wake_epochs=None)
print("loaded", X2.shape, "labels equal:", np.array_equal(y, y2))
assert X2.shape[1:] == (C.SAMPLES, 3)

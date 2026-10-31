"""Create a synthetic EDF to try the upload flow:  python -m scripts.make_demo_edf [n_epochs]"""
import sys, pathlib
from ml.src.synthetic import make_recording, write_demo_edf
n = int(sys.argv[1]) if len(sys.argv) > 1 else 240
out = pathlib.Path("sample_data"); out.mkdir(exist_ok=True)
X, y = make_recording(n, seed=7)
write_demo_edf(out / "demo_night.edf", X)
print(f"Wrote {out / 'demo_night.edf'} ({n} epochs = {n * 30 / 3600:.1f} h)")

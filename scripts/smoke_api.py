"""End-to-end API test with a synthetic EDF (needs a trained model; see README)."""
import tempfile, time, pathlib
from fastapi.testclient import TestClient
from backend.app.main import app
from ml.src.synthetic import make_recording, write_demo_edf

X, y = make_recording(90, seed=99)
f = pathlib.Path(tempfile.mkdtemp()) / "demo_night.edf"
write_demo_edf(f, X)                      # signals only - no labels, like a real upload
c = TestClient(app)
print(c.get("/api/health").json())
bad = c.post("/api/upload", files={"file": ("x.txt", b"hello")}); print("bad upload ->", bad.status_code)
rid = c.post("/api/upload", files={"file": (f.name, f.read_bytes())}).json()["recordingId"]
print("analyze ->", c.post(f"/api/analyze/{rid}").status_code)
for _ in range(120):
    r = c.get(f"/api/results/{rid}").json()
    if r["recording"]["status"] in ("completed", "failed"): break
    time.sleep(1)
print(r["recording"]["status"], r["recording"].get("error"))
p = r["prediction"]; print("epochs", p["totalEpochs"], "stats", {k: p["stats"][k] for k in ("totalSleepMin", "sleepEfficiency", "sleepLatencyMin")})
print("accuracy vs truth (synthetic):", round(float((__import__('numpy').array(p["stages"]) == y).mean()), 3))
s = c.get(f"/api/recordings/{rid}/signal?epoch=3").json(); print("signal", len(s["data"]), len(s["data"][0]))
print("history", len(c.get("/api/history").json()["recordings"]))
print("delete", c.delete(f"/api/recordings/{rid}").json()["status"], c.get(f"/api/results/{rid}").status_code)

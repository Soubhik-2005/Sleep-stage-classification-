import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import FileUpload from "../components/FileUpload";
import { api, errMsg } from "../services/api";

export default function Upload() {
  const nav = useNavigate();
  const [file, setFile] = useState(null);
  const [phase, setPhase] = useState("idle");        // idle | uploading | analyzing | failed
  const [upPct, setUpPct] = useState(0);
  const [job, setJob] = useState({ progress: 0, message: "" });
  const [error, setError] = useState("");
  const [health, setHealth] = useState(null);
  const timer = useRef();

  useEffect(() => { api.health().then(setHealth).catch(() => setHealth({ status: "down" })); return () => clearInterval(timer.current); }, []);

  const start = async () => {
    setError(""); setPhase("uploading");
    try {
      const { recordingId } = await api.upload(file, setUpPct);
      await api.analyze(recordingId);
      setPhase("analyzing");
      timer.current = setInterval(async () => {
        try {
          const { recording } = await api.results(recordingId);
          setJob({ progress: recording.progress, message: recording.message });
          if (recording.status === "completed") { clearInterval(timer.current); nav(`/results/${recordingId}`); }
          if (recording.status === "failed") { clearInterval(timer.current); setError(recording.error || "Analysis failed"); setPhase("failed"); }
        } catch (e) { clearInterval(timer.current); setError(errMsg(e)); setPhase("failed"); }
      }, 1500);
    } catch (e) { setError(errMsg(e)); setPhase("failed"); }
  };

  const busy = phase === "uploading" || phase === "analyzing";
  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="text-2xl font-bold">Analyze sleep</h1>
      <p className="mb-6 mt-1 text-sm text-muted">Upload an EDF polysomnography recording to classify every 30-second epoch.</p>
      {health?.status === "down" && <p className="mb-4 rounded-xl border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-300">Backend unreachable. Start it with <code>uvicorn backend.app.main:app --reload</code>.</p>}
      {health && health.status === "ok" && !health.modelAvailable && <p className="mb-4 rounded-xl border border-amber-500/40 bg-amber-500/10 p-3 text-sm text-amber-200">No trained model found. Run <code>python -m ml.src.train --download 10</code> first.</p>}
      <FileUpload file={file} onFile={(f) => { setFile(f); setPhase("idle"); setError(""); }} disabled={busy} />
      {phase === "uploading" && <Bar label={`Uploading… ${upPct}%`} pct={upPct} />}
      {phase === "analyzing" && <Bar label={job.message || "Starting…"} pct={job.progress} />}
      {error && <p className="mt-4 rounded-xl border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-300">{error}</p>}
      <button className="btn mt-6 w-full" disabled={!file || busy || health?.modelAvailable === false} onClick={start}>
        {busy ? "Working…" : "Start analysis"}
      </button>
    </div>
  );
}

const Bar = ({ label, pct }) => (
  <div className="mt-5"><div className="mb-1 flex justify-between text-sm"><span>{label}</span><span className="text-muted">{pct}%</span></div>
    <div className="h-2 overflow-hidden rounded-full bg-panel2"><div className="h-full rounded-full bg-gradient-to-r from-accent to-accent2 transition-all" style={{ width: `${pct}%` }} /></div></div>
);

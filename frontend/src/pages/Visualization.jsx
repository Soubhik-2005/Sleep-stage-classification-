import { useEffect, useState } from "react";
import { useParams, useSearchParams, Link } from "react-router-dom";
import EEGChart from "../components/EEGChart";
import { api, errMsg } from "../services/api";
import { STAGES, COLORS, fmtClock } from "../utils/stages";

const CH_COLORS = ["#38bdf8", "#7c5cff", "#f472b6"];

export default function Visualization() {
  const { id: paramId } = useParams();
  const [qs, setQs] = useSearchParams();
  const [id, setId] = useState(paramId || null);
  const [epoch, setEpoch] = useState(+(qs.get("epoch") || 0));
  const [sig, setSig] = useState(null); const [pred, setPred] = useState(null); const [err, setErr] = useState("");

  useEffect(() => {
    if (id) return;
    api.history().then((r) => { const l = r.find((x) => x.status === "completed"); l ? setId(l._id) : setErr("No completed analyses yet. Upload a recording first."); }).catch((e) => setErr(errMsg(e)));
  }, [id]);
  useEffect(() => { if (id) api.results(id).then((r) => setPred(r.prediction)).catch((e) => setErr(errMsg(e))); }, [id]);
  useEffect(() => {
    if (!id) return;
    setQs({ epoch }, { replace: true });
    api.signal(id, epoch).then(setSig).catch((e) => setErr(errMsg(e)));
  }, [id, epoch]);

  if (err) return <p className="text-red-300">{err} <Link to="/upload" className="underline">Analyze sleep</Link></p>;
  const total = pred?.totalEpochs ?? sig?.totalEpochs ?? 1;
  const stage = pred ? STAGES[pred.stages[epoch]] : null;
  return (
    <div>
      <h1 className="text-2xl font-bold">EEG visualization</h1>
      <p className="mb-6 text-sm text-muted">Preprocessed (0.3–35 Hz) signals for the selected 30-second epoch.</p>
      <div className="card">
        <div className="mb-4 flex flex-wrap items-center gap-4">
          <button className="btn-ghost" disabled={epoch === 0} onClick={() => setEpoch(epoch - 1)}>‹ Prev</button>
          <input type="range" min={0} max={total - 1} value={epoch} onChange={(e) => setEpoch(+e.target.value)} className="min-w-40 flex-1" />
          <button className="btn-ghost" disabled={epoch >= total - 1} onClick={() => setEpoch(epoch + 1)}>Next ›</button>
        </div>
        <div className="mb-4 flex flex-wrap gap-x-6 gap-y-1 text-sm text-muted">
          <span>Epoch <b className="text-white">{epoch + 1}</b> / {total}</span>
          <span>Time <b className="text-white">{fmtClock(epoch * 30)}</b></span>
          {sig && <span>Sampling <b className="text-white">{sig.sfreq} Hz</b></span>}
          {stage && <span>Predicted <b style={{ color: COLORS[stage] }}>{stage}</b> ({(pred.confidence[epoch] * 100).toFixed(0)}%)</span>}
        </div>
        {!sig ? <p className="text-muted">Loading signal…</p> : (
          <div className="space-y-4">{sig.channels.map((ch, i) => (
            <EEGChart key={ch} label={ch} values={sig.data[i]} sfreq={sig.sfreq} startSec={sig.startSec} color={CH_COLORS[i % 3]} />))}</div>)}
      </div>
    </div>
  );
}

import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import Summary from "../components/Summary";
import ProbabilityChart from "../components/ProbabilityChart";
import { api, errMsg } from "../services/api";
import { STAGES, COLORS, fmtClock } from "../utils/stages";

const PAGE = 15;

export default function Results() {
  const { id } = useParams();
  const [data, setData] = useState(null); const [err, setErr] = useState("");
  const [sel, setSel] = useState(0); const [page, setPage] = useState(0);

  useEffect(() => { api.results(id).then(setData).catch((e) => setErr(errMsg(e))); }, [id]);
  useEffect(() => setPage(Math.floor(sel / PAGE)), [sel]);

  if (err) return <p className="text-red-300">{err}</p>;
  if (!data) return <p className="text-muted">Loading…</p>;
  const { recording: rec, prediction: p } = data;
  if (!p) return <p className="text-muted">No results yet (status: {rec.status}). {rec.error}</p>;

  const rows = p.stages.slice(page * PAGE, page * PAGE + PAGE).map((s, k) => ({ i: page * PAGE + k, s }));
  return (
    <div>
      <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
        <div><h1 className="text-2xl font-bold">Prediction results</h1>
          <p className="text-sm text-muted">{rec.filename} · model {p.modelVersion} · {p.totalEpochs} epochs</p></div>
        <Link to={`/visualize/${id}?epoch=${sel}`} className="btn-ghost">View signal for epoch {sel + 1} →</Link>
      </div>
      <Summary prediction={p} selected={sel} onSelect={setSel} />
      <div className="mt-4 grid gap-4 lg:grid-cols-3">
        <div className="card">
          <h3 className="font-semibold">Epoch {sel + 1} <span className="text-sm font-normal text-muted">· {fmtClock(sel * 30)}</span></h3>
          <p className="mb-2 text-sm">Predicted <b style={{ color: COLORS[STAGES[p.stages[sel]]] }}>{STAGES[p.stages[sel]]}</b> · confidence {(p.confidence[sel] * 100).toFixed(1)}%</p>
          <ProbabilityChart probs={p.probabilities[sel]} />
          <input type="range" min={0} max={p.totalEpochs - 1} value={sel} onChange={(e) => setSel(+e.target.value)} className="mt-2 w-full" />
        </div>
        <div className="card lg:col-span-2">
          <div className="mb-2 flex items-center justify-between"><h3 className="font-semibold">Epoch predictions</h3>
            <div className="flex items-center gap-2 text-sm text-muted">
              <button className="btn-ghost !px-3 !py-1" disabled={page === 0} onClick={() => setPage(page - 1)}>‹</button>
              {page + 1} / {Math.ceil(p.totalEpochs / PAGE)}
              <button className="btn-ghost !px-3 !py-1" disabled={(page + 1) * PAGE >= p.totalEpochs} onClick={() => setPage(page + 1)}>›</button></div></div>
          <table className="w-full text-sm"><thead className="text-left text-xs uppercase text-muted"><tr><th className="py-1">#</th><th>Time</th><th>Stage</th><th>Confidence</th></tr></thead>
            <tbody>{rows.map(({ i, s }) => (
              <tr key={i} onClick={() => setSel(i)} className={`cursor-pointer border-t border-line hover:bg-panel2 ${i === sel ? "bg-panel2" : ""}`}>
                <td className="py-1.5">{i + 1}</td><td>{fmtClock(i * 30)}</td>
                <td><span className="rounded-md px-2 py-0.5 text-xs font-semibold text-black" style={{ background: COLORS[STAGES[s]] }}>{STAGES[s]}</span></td>
                <td>{(p.confidence[i] * 100).toFixed(1)}%</td></tr>))}</tbody></table>
        </div>
      </div>
    </div>
  );
}

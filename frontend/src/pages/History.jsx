import { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import { api, errMsg } from "../services/api";
import { fmtMin } from "../utils/stages";

const BADGE = { completed: "bg-emerald-500/20 text-emerald-300", processing: "bg-amber-500/20 text-amber-200",
  failed: "bg-red-500/20 text-red-300", uploaded: "bg-slate-500/20 text-slate-300" };

export default function History() {
  const [recs, setRecs] = useState(null); const [err, setErr] = useState("");
  const load = useCallback(() => api.history().then(setRecs).catch((e) => setErr(errMsg(e))), []);
  useEffect(() => { load(); }, [load]);

  const del = async (r) => { if (confirm(`Delete ${r.filename} and its results?`)) { await api.remove(r._id); load(); } };
  if (err) return <p className="text-red-300">{err}</p>;
  if (!recs) return <p className="text-muted">Loading…</p>;
  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold">History</h1>
      {recs.length === 0 ? <div className="card text-center text-muted">Nothing here yet. <Link to="/upload" className="text-accent underline">Analyze a recording</Link></div> : (
        <div className="card overflow-x-auto !p-0"><table className="w-full text-sm">
          <thead className="text-left text-xs uppercase text-muted"><tr>{["File", "Uploaded", "Status", "Sleep", "Efficiency", ""].map((h) => <th key={h} className="px-4 py-3">{h}</th>)}</tr></thead>
          <tbody>{recs.map((r) => (
            <tr key={r._id} className="border-t border-line">
              <td className="px-4 py-3 font-medium">{r.filename}</td>
              <td className="px-4">{new Date(r.uploadedAt).toLocaleString()}</td>
              <td className="px-4"><span className={`rounded-md px-2 py-0.5 text-xs ${BADGE[r.status]}`}>{r.status}</span></td>
              <td className="px-4">{r.summary ? fmtMin(r.summary.totalSleepMin) : "—"}</td>
              <td className="px-4">{r.summary ? `${r.summary.sleepEfficiency}%` : "—"}</td>
              <td className="space-x-2 whitespace-nowrap px-4 text-right">
                {r.status === "completed" && <><Link to={`/results/${r._id}`} className="text-accent2 hover:underline">View</Link>
                  <Link to={`/visualize/${r._id}`} className="text-accent2 hover:underline">Signal</Link></>}
                <button onClick={() => del(r)} className="text-red-400 hover:underline">Delete</button></td>
            </tr>))}</tbody></table></div>)}
    </div>
  );
}

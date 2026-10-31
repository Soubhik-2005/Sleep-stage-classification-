import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Summary from "../components/Summary";
import { api, errMsg } from "../services/api";

export default function Dashboard() {
  const [state, setState] = useState({ loading: true });
  useEffect(() => {
    (async () => {
      try {
        const recs = await api.history();
        const latest = recs.find((r) => r.status === "completed");
        if (!latest) return setState({ empty: true, count: recs.length });
        const { prediction } = await api.results(latest._id);
        setState({ rec: latest, prediction, count: recs.length });
      } catch (e) { setState({ error: errMsg(e) }); }
    })();
  }, []);

  if (state.loading) return <p className="text-muted">Loading…</p>;
  if (state.error) return <p className="text-red-300">{state.error}</p>;
  if (state.empty) return (
    <div className="card mx-auto mt-10 max-w-lg text-center"><p className="text-lg font-semibold">No analyses yet</p>
      <p className="mb-4 mt-1 text-sm text-muted">Upload a recording to see your sleep summary here.</p><Link to="/upload" className="btn">Analyze sleep</Link></div>);
  return (
    <div>
      <div className="mb-6 flex items-end justify-between"><div><h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-sm text-muted">Latest analysis: {state.rec.filename} · {state.count} recording(s) total</p></div>
        <Link to={`/results/${state.rec._id}`} className="btn-ghost">Full results →</Link></div>
      <Summary prediction={state.prediction} />
    </div>
  );
}

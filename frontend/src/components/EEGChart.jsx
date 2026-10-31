import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from "recharts";

export default function EEGChart({ label, values, sfreq, startSec, color = "#38bdf8" }) {
  const data = values.map((v, i) => ({ t: +(startSec + i / sfreq).toFixed(2), v }));
  return (
    <div>
      <p className="mb-1 text-xs text-muted">{label} <span className="opacity-60">(µV)</span></p>
      <ResponsiveContainer width="100%" height={130}>
        <LineChart data={data} margin={{ left: 0, right: 12, top: 4, bottom: 0 }}>
          <CartesianGrid stroke="#232e5c" strokeDasharray="3 3" />
          <XAxis dataKey="t" type="number" domain={["dataMin", "dataMax"]} tick={{ fill: "#8b95c4", fontSize: 10 }} tickCount={7} />
          <YAxis width={44} tick={{ fill: "#8b95c4", fontSize: 10 }} />
          <Line type="monotone" dataKey="v" stroke={color} strokeWidth={1} dot={false} isAnimationActive={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

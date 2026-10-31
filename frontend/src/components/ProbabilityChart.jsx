import { BarChart, Bar, XAxis, YAxis, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { STAGES, COLORS } from "../utils/stages";

export default function ProbabilityChart({ probs }) {
  const data = STAGES.map((s, i) => ({ name: s, p: +(probs[i] * 100).toFixed(1) }));
  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data} layout="vertical" margin={{ left: 8, right: 24 }}>
        <XAxis type="number" domain={[0, 100]} tick={{ fill: "#8b95c4", fontSize: 11 }} unit="%" />
        <YAxis type="category" dataKey="name" width={44} tick={{ fill: "#e6e9ff", fontSize: 12 }} />
        <Tooltip contentStyle={{ background: "#111936", border: "1px solid #232e5c", borderRadius: 12 }} formatter={(v) => `${v}%`} />
        <Bar dataKey="p" radius={6} isAnimationActive={false}>
          {data.map((d) => <Cell key={d.name} fill={COLORS[d.name]} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { STAGES, COLORS, fmtMin } from "../utils/stages";

export default function SleepStageChart({ minutes }) {
  const data = STAGES.map((s) => ({ name: s, value: minutes[s] || 0 }));
  return (
    <ResponsiveContainer width="100%" height={240}>
      <PieChart>
        <Pie data={data} dataKey="value" innerRadius={55} outerRadius={90} paddingAngle={2} stroke="none">
          {data.map((d) => <Cell key={d.name} fill={COLORS[d.name]} />)}
        </Pie>
        <Tooltip contentStyle={{ background: "#111936", border: "1px solid #232e5c", borderRadius: 12 }}
          formatter={(v) => fmtMin(v)} />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}

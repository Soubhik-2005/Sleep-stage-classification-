import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";
import { STAGES, LEVEL, LEVEL_LABEL } from "../utils/stages";

export default function Hypnogram({ stages, selected, onSelect, height = 240 }) {
  const data = stages.map((s, i) => ({ i, hours: +(i * 30 / 3600).toFixed(3), level: LEVEL[s], stage: STAGES[s] }));
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ left: 8, right: 16, top: 8 }}
        onClick={(e) => e?.activePayload && onSelect?.(e.activePayload[0].payload.i)}>
        <CartesianGrid stroke="#232e5c" strokeDasharray="3 3" />
        <XAxis dataKey="hours" type="number" domain={[0, "dataMax"]} tick={{ fill: "#8b95c4", fontSize: 11 }}
          tickFormatter={(v) => `${v.toFixed(1)}h`} />
        <YAxis domain={[0, 4]} ticks={[0, 1, 2, 3, 4]} width={44} tick={{ fill: "#8b95c4", fontSize: 11 }}
          tickFormatter={(v) => LEVEL_LABEL[v]} />
        <Tooltip contentStyle={{ background: "#111936", border: "1px solid #232e5c", borderRadius: 12 }}
          formatter={(_, __, p) => [p.payload.stage, "Stage"]} labelFormatter={(h) => `${(+h).toFixed(2)} h`} />
        <Line type="stepAfter" dataKey="level" stroke="#7c5cff" strokeWidth={2} dot={false} isAnimationActive={false} />
        {selected != null && <ReferenceLine x={data[selected]?.hours} stroke="#38bdf8" strokeWidth={2} />}
      </LineChart>
    </ResponsiveContainer>
  );
}

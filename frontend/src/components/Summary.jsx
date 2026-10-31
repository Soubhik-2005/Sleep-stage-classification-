import StatCard from "./StatCard";
import Hypnogram from "./Hypnogram";
import SleepStageChart from "./SleepStageChart";
import { COLORS, fmtMin } from "../utils/stages";

/** Stat cards + hypnogram + distribution; shared by Dashboard and Results. */
export default function Summary({ prediction, selected, onSelect }) {
  const s = prediction.stats;
  return (
    <>
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Total recording" value={fmtMin(s.timeInBedMin)} sub={`${s.totalEpochs} epochs × 30 s`} />
        <StatCard label="Total sleep" value={fmtMin(s.totalSleepMin)} sub={`Efficiency ${s.sleepEfficiency}%`} />
        <StatCard label="Wake" value={fmtMin(s.wakeMin)} sub={`${s.percent.Wake}%`} color={COLORS.Wake} />
        <StatCard label="Light sleep (N1+N2)" value={fmtMin(s.lightSleepMin)} sub={`${(s.percent.N1 + s.percent.N2).toFixed(1)}%`} color={COLORS.N2} />
        <StatCard label="Deep sleep (N3)" value={fmtMin(s.deepSleepMin)} sub={`${s.percent.N3}%`} color={COLORS.N3} />
        <StatCard label="REM sleep" value={fmtMin(s.remMin)} sub={`${s.percent.REM}%`} color={COLORS.REM} />
        <StatCard label="Sleep latency" value={fmtMin(s.sleepLatencyMin)} sub="to first non-wake epoch" />
        <StatCard label="REM latency" value={fmtMin(s.remLatencyMin)} sub={`WASO ${fmtMin(s.wasoMin)}`} />
      </div>
      <div className="mt-4 grid gap-4 lg:grid-cols-3">
        <div className="card lg:col-span-2">
          <h3 className="mb-2 font-semibold">Hypnogram</h3>
          <Hypnogram stages={prediction.stages} selected={selected} onSelect={onSelect} />
        </div>
        <div className="card">
          <h3 className="mb-2 font-semibold">Stage distribution</h3>
          <SleepStageChart minutes={s.minutes} />
        </div>
      </div>
      {prediction.syntheticModel && (
        <p className="mt-4 rounded-xl border border-amber-500/40 bg-amber-500/10 p-3 text-sm text-amber-200">
          This result came from a model trained on <b>synthetic</b> data (pipeline test). Train on Sleep-EDF for meaningful predictions.
        </p>
      )}
    </>
  );
}

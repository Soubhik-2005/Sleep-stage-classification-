import { Link } from "react-router-dom";

const steps = [
  ["1 · Upload", "Drop a whole-night polysomnography recording in EDF format."],
  ["2 · Preprocess", "EEG + EOG channels are filtered (0.3–35 Hz), resampled to 100 Hz and cut into 30-second epochs."],
  ["3 · Classify", "A 1D convolutional neural network assigns Wake, N1, N2, N3 or REM with class probabilities."],
  ["4 · Explore", "Review the hypnogram, time in each stage, and the raw waveforms behind every epoch."],
];

export default function Home() {
  return (
    <div>
      <section className="rounded-3xl border border-line bg-gradient-to-br from-accent/30 via-panel to-accent2/10 p-10 md:p-14">
        <p className="text-sm font-medium text-accent2">Deep-learning sleep analysis</p>
        <h1 className="mt-2 max-w-2xl text-4xl font-bold leading-tight md:text-5xl">Automatic sleep stage classification from EEG & EOG</h1>
        <p className="mt-4 max-w-xl text-muted">Upload a sleep recording and get a hypnogram, stage statistics and per-epoch confidence in minutes.</p>
        <div className="mt-8 flex gap-3"><Link to="/upload" className="btn">Get Started</Link><Link to="/dashboard" className="btn-ghost">View dashboard</Link></div>
      </section>
      <section className="mt-8 grid gap-4 md:grid-cols-2">
        <div className="card"><h2 className="mb-2 text-lg font-semibold">What is sleep staging?</h2>
          <p className="text-sm leading-relaxed text-muted">Sleep is scored in 30-second epochs as Wake, light sleep (N1, N2), deep slow-wave sleep (N3) or REM. The sequence over the night — the hypnogram — describes sleep architecture. Experts score it by hand; this app automates it.</p></div>
        <div className="card"><h2 className="mb-2 text-lg font-semibold">Supported input</h2>
          <p className="text-sm leading-relaxed text-muted">EDF / EDF+ files containing channels named <code className="text-accent2">EEG Fpz-Cz</code>, <code className="text-accent2">EEG Pz-Oz</code> and <code className="text-accent2">EOG horizontal</code> (the Sleep-EDF layout).</p></div>
      </section>
      <h2 className="mb-3 mt-8 text-lg font-semibold">How it works</h2>
      <div className="grid gap-4 md:grid-cols-4">
        {steps.map(([t, d]) => <div key={t} className="card"><p className="font-semibold text-accent">{t}</p><p className="mt-2 text-sm text-muted">{d}</p></div>)}
      </div>
      <p className="mt-8 text-xs text-muted">Educational and research use only — not a clinically validated diagnosis or a replacement for expert polysomnography interpretation.</p>
    </div>
  );
}

import { useRef, useState } from "react";

export default function FileUpload({ file, onFile, disabled, maxMB = 500 }) {
  const input = useRef(); const [over, setOver] = useState(false); const [err, setErr] = useState("");
  const pick = (f) => {
    if (!f) return;
    if (!f.name.toLowerCase().endsWith(".edf")) return setErr("Only .edf files are supported.");
    if (f.size > maxMB * 1024 * 1024) return setErr(`File is larger than ${maxMB} MB.`);
    setErr(""); onFile(f);
  };
  return (
    <div>
      <div onClick={() => !disabled && input.current.click()}
        onDragOver={(e) => { e.preventDefault(); setOver(true); }} onDragLeave={() => setOver(false)}
        onDrop={(e) => { e.preventDefault(); setOver(false); !disabled && pick(e.dataTransfer.files[0]); }}
        className={`cursor-pointer rounded-2xl border-2 border-dashed p-12 text-center transition ${over ? "border-accent bg-accent/10" : "border-line hover:border-accent/60"}`}>
        <div className="text-4xl">⇪</div>
        <p className="mt-3 font-medium">{file ? file.name : "Drag & drop an EDF recording here"}</p>
        <p className="mt-1 text-sm text-muted">{file ? `${(file.size / 1048576).toFixed(1)} MB` : "or click to browse · .edf up to " + maxMB + " MB"}</p>
        <input ref={input} type="file" accept=".edf" hidden onChange={(e) => pick(e.target.files[0])} />
      </div>
      {err && <p className="mt-2 text-sm text-red-400">{err}</p>}
    </div>
  );
}

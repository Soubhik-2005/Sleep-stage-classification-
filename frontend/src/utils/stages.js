export const STAGES = ["Wake", "N1", "N2", "N3", "REM"];
export const COLORS = { Wake: "#fbbf24", N1: "#38bdf8", N2: "#6366f1", N3: "#a855f7", REM: "#f472b6" };
// Hypnogram y-level (top = Wake, bottom = N3), the clinical convention.
export const LEVEL = [4, 2, 1, 0, 3];
export const LEVEL_LABEL = { 4: "Wake", 3: "REM", 2: "N1", 1: "N2", 0: "N3" };
export const fmtMin = (m) => (m == null ? "—" : m >= 60 ? `${Math.floor(m / 60)}h ${Math.round(m % 60)}m` : `${Math.round(m)}m`);
export const fmtClock = (sec) => {
  const h = Math.floor(sec / 3600), m = Math.floor((sec % 3600) / 60), s = Math.floor(sec % 60);
  return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
};

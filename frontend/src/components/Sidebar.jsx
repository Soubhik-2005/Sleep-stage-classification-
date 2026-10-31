import { NavLink } from "react-router-dom";

const items = [
  ["/", "Home", "⌂"], ["/dashboard", "Dashboard", "▦"], ["/upload", "Analyze Sleep", "⇪"],
  ["/visualize", "EEG Visualization", "∿"], ["/history", "History", "☰"],
];

export default function Sidebar() {
  return (
    <aside className="sticky top-0 flex h-screen w-60 shrink-0 flex-col border-r border-line bg-panel/60 p-4 max-md:hidden">
      <div className="mb-8 flex items-center gap-2 px-2 text-xl font-bold">
        <span className="grid h-8 w-8 place-items-center rounded-lg bg-accent">☾</span> SleepAI
      </div>
      <nav className="flex flex-col gap-1">
        {items.map(([to, label, icon]) => (
          <NavLink key={to} to={to} end={to === "/"}
            className={({ isActive }) => `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition ${isActive ? "bg-accent/20 text-white" : "text-muted hover:bg-panel2 hover:text-white"}`}>
            <span className="w-5 text-center">{icon}</span>{label}
          </NavLink>
        ))}
      </nav>
      <p className="mt-auto px-2 text-xs leading-relaxed text-muted">
        Educational / research tool. Not a clinically validated diagnostic device.
      </p>
    </aside>
  );
}

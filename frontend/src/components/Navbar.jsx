import { Link } from "react-router-dom";
export default function Navbar() {
  return (
    <header className="flex items-center justify-between border-b border-line px-6 py-3 md:hidden">
      <span className="font-bold">☾ SleepAI</span>
      <nav className="flex gap-3 text-sm text-muted">
        <Link to="/dashboard">Dashboard</Link><Link to="/upload">Analyze</Link><Link to="/history">History</Link>
      </nav>
    </header>
  );
}

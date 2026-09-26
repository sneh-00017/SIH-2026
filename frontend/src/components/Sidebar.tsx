import { Link, NavLink } from "react-router-dom";

export default function Sidebar() {
  return (
    <aside className="side-panel">
      <Link className="brand" to="/dashboard">
        <span className="brand-mark">SI</span>
        <span><strong>SafeSight</strong><small>Risk intelligence</small></span>
      </Link>
      <nav className="main-nav" aria-label="Main navigation">
        <NavLink to="/dashboard"><span>⌂</span>Dashboard</NavLink>
        <NavLink to="/analysis"><span>◉</span>Image analysis</NavLink>
        <NavLink to="/video"><span>▶</span>Video detection</NavLink>
        <NavLink to="/history"><span>↺</span>History</NavLink>
        <NavLink to="/team"><span>◎</span>About team</NavLink>
      </nav>
      <div className="side-footer"><span className="live-dot" />AI monitoring active</div>
    </aside>
  );
}

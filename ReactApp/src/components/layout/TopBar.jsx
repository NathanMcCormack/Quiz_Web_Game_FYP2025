import "./TopBar.css";
import { NavLink } from "react-router-dom";

const navItems = [
  { to: "/", label: "Classic", end: true },
  { to: "/daily", label: "Daily" },
  { to: "/legacy", label: "Legacy" },
];

export default function TopBar() {
  return (
    <header className="topbar">
      <div className="topbar__inner">
        <div className="topbar__brand">Ranger</div>

        <nav className="topbar__nav" aria-label="Primary navigation">
          {navItems.map(({ to, label, end = false }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                isActive ? "topbar__link topbar__link--active" : "topbar__link"
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  );
}
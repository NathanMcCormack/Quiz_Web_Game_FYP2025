import "./TopBar.css";
import { NavLink } from "react-router-dom";

export default function TopBar() {
  return (
    <header className="topbar">
      <div className="topbar__inner">
        <nav className="topbar__nav">
          <NavLink to="/" end className={({ isActive }) => isActive ? "topbar__link topbar__link--active" : "topbar__link"}>
            Classic
          </NavLink>
          <NavLink to="/daily" className={({ isActive }) => isActive ? "topbar__link topbar__link--active" : "topbar__link"}>
            Daily
          </NavLink>
          <NavLink to="/legacy" className={({ isActive }) => isActive ? "topbar__link topbar__link--active" : "topbar__link"}>
            Legacy
          </NavLink>
        </nav>
      </div>
    </header>
  );
}
import "./TopBar.css";

export default function TopBar({title}) {
  return (
    <header className="topbar" role="banner">
      <div className="topbar__inner">
        <h1 className="topbar__title">{title}</h1>
      </div>
    </header>
  );
}

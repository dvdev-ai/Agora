import { useEffect, useState } from "react";
import { Link, NavLink, useLocation } from "react-router-dom";
import { BOT_HANDLE, BOT_URL, NAV } from "@/data/content";
import { Button } from "@/components/Button";
import { cn } from "@/lib/utils";

export function Header() {
  const [open, setOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    setOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    document.body.classList.toggle("nav-open", open);
    return () => document.body.classList.remove("nav-open");
  }, [open]);

  return (
    <header className="site-header">
      <div className="container site-header__inner">
        <Link className="brand-link" to="/">
          Агора
        </Link>

        <nav className="nav-desktop" aria-label="Основная навигация">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => cn(isActive && "is-active")}
              end={item.to === "/"}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="header-actions">
          <Button href={BOT_URL} variant="ghost" className="header-cta">
            Telegram
          </Button>
          <button
            className="burger"
            type="button"
            aria-label={open ? "Закрыть меню" : "Открыть меню"}
            aria-expanded={open}
            onClick={() => setOpen((v) => !v)}
          >
            <span />
          </button>
        </div>
      </div>

      {open ? (
        <nav className="container nav-mobile" aria-label="Мобильная навигация">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => cn(isActive && "is-active")}
              end={item.to === "/"}
            >
              {item.label}
            </NavLink>
          ))}
          <a href={BOT_URL} target="_blank" rel="noopener noreferrer">
            {BOT_HANDLE}
          </a>
        </nav>
      ) : null}
    </header>
  );
}

export function Footer() {
  return (
    <footer className="site-footer">
      <div className="container site-footer__inner">
        <span>Агора · {BOT_HANDLE}</span>
        <nav aria-label="Подвал">
          <Link to="/privacy">Приватность</Link>
          <Link to="/tools">Инструменты</Link>
          <a href={BOT_URL} target="_blank" rel="noopener noreferrer">
            Открыть бота
          </a>
        </nav>
        <span>Не замена живому психологу</span>
      </div>
    </footer>
  );
}

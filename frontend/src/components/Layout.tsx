import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";
import { MeshBackground } from "./MeshBackground";

const NAV_LINKS = [
  { to: "/",         label: "Dashboard" },
  { to: "/crawl",    label: "New Crawl" },
  { to: "/articles", label: "Articles" },
];

export function Layout() {
  const loc = useLocation();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col relative">
      <MeshBackground />

      <header className="sticky top-0 z-50 border-b backdrop-blur-md"
        style={{ background: "rgba(0,0,0,0.7)", borderColor: "var(--mesh-border)" }}
      >
        <div className="max-w-7xl mx-auto px-6 md:px-10 h-16 flex items-center gap-8">
          <Link to="/" className="font-display font-medium text-base shrink-0 tracking-tight" style={{ color: "var(--mesh-text)" }}>
            Clean<span style={{ color: "var(--mesh-muted)" }}>Crawl</span>
          </Link>

          <nav className="flex items-center gap-1 flex-1">
            {NAV_LINKS.map(({ to, label }) => {
              const active = loc.pathname === to || (to !== "/" && loc.pathname.startsWith(to));
              return (
                <Link
                  key={to}
                  to={to}
                  className="relative px-3 py-1.5 text-sm font-medium rounded-full transition-colors"
                  style={{ color: active ? "var(--mesh-text)" : "var(--mesh-muted)" }}
                >
                  {label}
                </Link>
              );
            })}
          </nav>

          <button
            onClick={() => navigate("/crawl")}
            className="mesh-btn-primary shrink-0 text-xs !px-4 !py-2"
          >
            New Crawl
          </button>
        </div>
      </header>

      <main className="flex-1 relative z-10">
        <Outlet />
      </main>

      <footer
        className="relative z-10 border-t py-6 text-center mesh-label"
        style={{ borderColor: "var(--mesh-border)" }}
      >
        Respectful crawling · Explainable quality · Live observability
      </footer>
    </div>
  );
}

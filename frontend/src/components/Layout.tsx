import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";

const NAV_LINKS = [
  { to: "/",         label: "Dashboard" },
  { to: "/crawl",    label: "New Crawl" },
  { to: "/articles", label: "Articles" },
];

export function Layout() {
  const loc = useLocation();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Top navbar */}
      <header className="sticky top-0 z-50 bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-8 h-14 flex items-center gap-8">
          {/* Wordmark */}
          <Link to="/" className="font-bold text-gray-900 text-base shrink-0">
            Clean<span className="text-indigo-600">Crawl</span>
          </Link>

          {/* Nav links */}
          <nav className="flex items-center gap-1 flex-1">
            {NAV_LINKS.map(({ to, label }) => {
              const active = loc.pathname === to || (to !== "/" && loc.pathname.startsWith(to));
              return (
                <Link
                  key={to}
                  to={to}
                  className={`relative px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                    active
                      ? "text-indigo-600"
                      : "text-gray-500 hover:text-gray-900 hover:bg-gray-50"
                  }`}
                >
                  {label}
                  {active && (
                    <span className="absolute bottom-0 left-3 right-3 h-0.5 bg-indigo-600 rounded-full" />
                  )}
                </Link>
              );
            })}
          </nav>

          {/* CTA */}
          <button
            onClick={() => navigate("/crawl")}
            className="shrink-0 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium px-4 py-1.5 rounded-lg transition-colors"
          >
            New Crawl
          </button>
        </div>
      </header>

      {/* Page content */}
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
}

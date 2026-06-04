import { Outlet, Link, useLocation, useNavigate } from "react-router-dom";
import { Sprout, Menu, X } from "lucide-react";
import { useState } from "react";
import { useAuthStore } from "@/store/authStore";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export default function PublicLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigate = useNavigate();
  const isAuth = useAuthStore((s) => s.isAuthenticated);
  const location = useLocation();

  const links = [
    { to: "/mapa-regional", label: "Mapa regional" },
    { to: "/metodologia", label: "Metodología" },
    { to: "/precios", label: "Precios" },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top nav sticky */}
      <header
        className={cn(
          "sticky top-0 z-50 w-full transition-all duration-200",
          location.pathname !== "/"
            ? "bg-white shadow-sm"
            : "bg-transparent"
        )}
      >
        <div className="container-app flex h-16 sm:h-[72px] items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <Sprout className="h-7 w-7 sm:h-8 sm:w-8 text-sembriaia-primary" />
            <span className="font-bold text-lg sm:text-xl text-sembriaia-primary">
              SembrarIA
            </span>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-8">
            {links.map((l) => (
              <Link
                key={l.to}
                to={l.to}
                className={cn(
                  "text-sm font-medium transition-colors hover:text-sembriaia-action",
                  location.pathname !== "/"
                    ? "text-foreground"
                    : location.pathname === l.to
                    ? "text-sembriaia-primary"
                    : "text-foreground/80"
                )}
              >
                {l.label}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-2 sm:gap-3">
            {isAuth ? (
              <Button onClick={() => navigate("/dashboard")} size="default">
                Ir al dashboard
              </Button>
            ) : (
              <>
                <Button
                  variant="ghost"
                  onClick={() => navigate("/login")}
                  className="hidden sm:inline-flex"
                >
                  Ingresar
                </Button>
                <Button onClick={() => navigate("/register")} size="default">
                  Registrarse
                </Button>
              </>
            )}

            {/* Mobile hamburger */}
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="md:hidden p-2"
              aria-label="Menu"
            >
              {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>

        {/* Mobile drawer */}
        {mobileOpen && (
          <div className="md:hidden bg-white border-t">
            <div className="container-app py-4 flex flex-col gap-2">
              {links.map((l) => (
                <Link
                  key={l.to}
                  to={l.to}
                  onClick={() => setMobileOpen(false)}
                  className="py-2 text-sm font-medium"
                >
                  {l.label}
                </Link>
              ))}
            </div>
          </div>
        )}
      </header>

      <Outlet />

      {/* Footer */}
      <footer className="bg-sembriaia-primary text-white mt-auto">
        <div className="container-app py-12 sm:py-16 px-4 sm:px-8">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Sprout className="h-6 w-6" />
                <span className="font-bold text-lg">SembrarIA</span>
              </div>
              <p className="text-sm text-white/70">Del pasto al plato</p>
            </div>
            <div>
              <h4 className="font-semibold mb-3 text-sm">Plataforma</h4>
              <ul className="space-y-2 text-sm text-white/70">
                <li><Link to="/mapa-regional">Mapa regional</Link></li>
                <li><Link to="/precios">Precios</Link></li>
                <li><Link to="/metodologia">Metodología</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-3 text-sm">Legal</h4>
              <ul className="space-y-2 text-sm text-white/70">
                <li>Términos</li>
                <li>Privacidad</li>
                <li>EUDR / Ley 261/2024</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-3 text-sm">Contacto</h4>
              <ul className="space-y-2 text-sm text-white/70">
                <li>Universidad de la Amazonía</li>
                <li>Florencia, Caquetá</li>
                <li>contacto@sembriaia.udla.edu.co</li>
              </ul>
            </div>
          </div>
          <div className="mt-12 pt-6 border-t border-white/20 text-xs text-white/40 text-center">
            © 2026 SembrarIA · Universidad de la Amazonía · CopernicusLAC Hackathon
          </div>
        </div>
      </footer>
    </div>
  );
}

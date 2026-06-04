import { Outlet, Link, useLocation, useNavigate } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import { useState } from "react";
import {
  Home, MapPin, BarChart3, Bell, FileText, DollarSign,
  Users, Settings, LogOut, Menu, X, Sprout
} from "lucide-react";
import { cn } from "@/lib/utils";
import { COLORS } from "@/config";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: Home },
  { to: "/analizar", label: "Mis fincas", icon: MapPin },
  { to: "/alertas", label: "Alertas", icon: Bell, badge: true },
  { to: "/reportes", label: "Reportes", icon: FileText },
  { to: "/precios", label: "Precios", icon: DollarSign },
  { to: "/cooperativa", label: "Cooperativa", icon: Users, role: ["cooperativa", "extensionista", "gobierno"] },
  { to: "/configuracion", label: "Configuración", icon: Settings },
];

export default function AppLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [mobileOpen, setMobileOpen] = useState(false);

  const filteredNav = navItems.filter(
    (item) => !item.role || item.role.includes(user?.role)
  );

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <div className="min-h-screen flex bg-[#F5F5F5]">
      {/* Sidebar (desktop) */}
      <aside className="hidden lg:flex lg:flex-col w-64 bg-sembriaia-primary text-white sticky top-0 h-screen">
        <div className="p-6">
          <Link to="/dashboard" className="flex items-center gap-2">
            <Sprout className="h-8 w-8" />
            <span className="font-bold text-xl">SembrarIA</span>
          </Link>
        </div>

        <nav className="flex-1 px-4 space-y-1">
          {filteredNav.map((item) => {
            const Icon = item.icon;
            const active = location.pathname === item.to;
            return (
              <Link
                key={item.to}
                to={item.to}
                className={cn(
                  "flex items-center gap-3 px-4 h-11 rounded-lg text-sm font-medium transition-colors",
                  active
                    ? "bg-white/15 text-white"
                    : "text-white/70 hover:bg-white/10 hover:text-white"
                )}
              >
                <Icon className="h-5 w-5" />
                {item.label}
                {item.badge && (
                  <span className="ml-auto bg-sembriaia-alert text-white text-xs px-2 py-0.5 rounded-full">
                    2
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* User card */}
        <div className="p-4 border-t border-white/20">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-full bg-sembriaia-action flex items-center justify-center text-white font-semibold">
              {user?.full_name?.charAt(0) || "U"}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user?.full_name}</p>
              <p className="text-xs text-white/60 truncate">{user?.organization || user?.role}</p>
            </div>
            <button
              onClick={handleLogout}
              className="p-2 hover:bg-white/10 rounded-lg"
              title="Cerrar sesión"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Mobile top bar */}
      <div className="lg:hidden fixed top-0 left-0 right-0 h-16 bg-white shadow-sm z-40 flex items-center justify-between px-4">
        <Link to="/dashboard" className="flex items-center gap-2 text-sembriaia-primary">
          <Sprout className="h-6 w-6" />
          <span className="font-bold">SembrarIA</span>
        </Link>
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="p-2"
          aria-label="Menu"
        >
          {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div
          className="lg:hidden fixed inset-0 z-50 bg-black/50"
          onClick={() => setMobileOpen(false)}
        >
          <aside
            className="w-72 h-full bg-sembriaia-primary text-white p-4 animate-slide-up"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center gap-2 mb-8 mt-2">
              <Sprout className="h-7 w-7" />
              <span className="font-bold text-lg">SembrarIA</span>
            </div>
            <nav className="space-y-1">
              {filteredNav.map((item) => {
                const Icon = item.icon;
                const active = location.pathname === item.to;
                return (
                  <Link
                    key={item.to}
                    to={item.to}
                    onClick={() => setMobileOpen(false)}
                    className={cn(
                      "flex items-center gap-3 px-4 h-11 rounded-lg text-sm font-medium",
                      active ? "bg-white/15" : "text-white/70 hover:bg-white/10"
                    )}
                  >
                    <Icon className="h-5 w-5" />
                    {item.label}
                  </Link>
                );
              })}
              <button
                onClick={handleLogout}
                className="flex items-center gap-3 px-4 h-11 rounded-lg text-sm font-medium text-white/70 hover:bg-white/10 w-full"
              >
                <LogOut className="h-5 w-5" />
                Cerrar sesión
              </button>
            </nav>
          </aside>
        </div>
      )}

      {/* Main */}
      <main className="flex-1 min-w-0 pt-16 lg:pt-0">
        <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

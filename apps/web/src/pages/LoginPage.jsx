import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Sprout, Eye, EyeOff, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuthStore } from "@/store/authStore";

export default function LoginPage() {
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [show, setShow] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "No fue posible iniciar sesión. Intenta de nuevo.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-72px)] grid lg:grid-cols-2">
      {/* Left: green panel with testimonial */}
      <div className="hidden lg:flex bg-sembriaia-primary text-white items-center justify-center p-12 relative overflow-hidden">
        <div
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage:
              "repeating-linear-gradient(45deg, transparent 0 20px, white 20px 21px)",
          }}
        />
        <div className="relative max-w-md">
          <ShieldCheck className="h-10 w-10 mb-6 opacity-80" />
          <blockquote className="text-2xl italic font-normal leading-relaxed mb-6">
            “Ahora mis nietos comen plátano de mi finca, no de Bogotá.”
          </blockquote>
          <p className="font-medium text-white/90 mb-1">Don José</p>
          <p className="text-sm text-white/70 mb-4">Vereda El Rosal, Caquetá</p>
          <div className="flex items-center gap-2 text-xs text-white/60">
            <span className="text-yellow-300">★★★★★</span>
            <span>Productor desde 2024</span>
          </div>
        </div>
      </div>

      {/* Right: form */}
      <div className="flex items-center justify-center p-6 sm:p-12 bg-white">
        <div className="w-full max-w-md animate-fade-in">
          <Link to="/" className="flex items-center gap-2 mb-8">
            <Sprout className="h-7 w-7 text-sembriaia-primary" />
            <span className="font-bold text-2xl text-sembriaia-primary">SembrarIA</span>
          </Link>
          <h1 className="text-3xl font-bold text-foreground mb-2">Ingresar</h1>
          <p className="text-sm text-muted-foreground mb-8">
            Para productores, cooperativas y extensionistas de Caquetá
          </p>

          {error && (
            <div className="mb-4 p-3 rounded-lg bg-sembriaia-alert/10 border border-sembriaia-alert/20 flex gap-2 text-sm text-sembriaia-alert">
              <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="email" className="mb-1.5 block">Correo electrónico</Label>
              <Input
                id="email"
                type="email"
                placeholder="tu@correo.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </div>
            <div>
              <Label htmlFor="password" className="mb-1.5 block">Contraseña</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={show ? "text" : "password"}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                  className="pr-12"
                />
                <button
                  type="button"
                  onClick={() => setShow(!show)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  aria-label={show ? "Ocultar contraseña" : "Mostrar contraseña"}
                >
                  {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>
            <Button type="submit" size="lg" className="w-full" disabled={loading}>
              {loading ? "Ingresando..." : "Ingresar"}
            </Button>
          </form>

          <div className="my-6 flex items-center gap-3 text-xs text-muted-foreground">
            <div className="flex-1 h-px bg-border" />
            <span>o</span>
            <div className="flex-1 h-px bg-border" />
          </div>

          <p className="text-center text-sm text-muted-foreground">
            ¿No tienes cuenta?{" "}
            <Link to="/register" className="text-sembriaia-water font-medium hover:underline">
              Regístrate gratis
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

function ShieldCheck(props) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z" />
      <path d="m9 12 2 2 4-4" />
    </svg>
  );
}

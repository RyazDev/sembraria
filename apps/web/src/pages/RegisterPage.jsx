import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Sprout, Eye, EyeOff, AlertCircle, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuthStore } from "@/store/authStore";

const roles = [
  { id: "productor", label: "Productor" },
  { id: "cooperativa", label: "Cooperativa" },
  { id: "extensionista", label: "Extensionista" },
  { id: "gobierno", label: "Entidad gubernamental" },
];

export default function RegisterPage() {
  const navigate = useNavigate();
  const register = useAuthStore((s) => s.register);
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    phone: "",
    password: "",
    role: "productor",
    organization: "",
  });
  const [accept, setAccept] = useState(false);
  const [show, setShow] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const update = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (!accept) {
      setError("Debes aceptar los términos y el uso de datos para trazabilidad EUDR.");
      return;
    }
    setLoading(true);
    try {
      await register(form);
      navigate("/dashboard");
    } catch (err) {
      setError(
        err.response?.data?.detail || "No fue posible crear la cuenta. Intenta de nuevo."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-72px)] grid lg:grid-cols-2">
      {/* Left: green panel */}
      <div className="hidden lg:flex bg-sembriaia-primary text-white items-center justify-center p-12 relative overflow-hidden">
        <div
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage:
              "repeating-linear-gradient(45deg, transparent 0 20px, white 20px 21px)",
          }}
        />
        <div className="relative max-w-md">
          <Sprout className="h-12 w-12 mb-6" />
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
          <h1 className="text-3xl font-bold text-foreground mb-2">Crear cuenta</h1>
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
              <Label htmlFor="full_name" className="mb-1.5 block">Nombre completo</Label>
              <Input
                id="full_name"
                placeholder="Brayan Cuellar"
                value={form.full_name}
                onChange={update("full_name")}
                required
                autoComplete="name"
              />
            </div>

            <div>
              <Label htmlFor="email" className="mb-1.5 block">Correo electrónico o teléfono</Label>
              <Input
                id="email"
                type="text"
                placeholder="tu@correo.com o +57 3XX XXXXXXX"
                value={form.email}
                onChange={update("email")}
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
                  placeholder="Mínimo 8 caracteres"
                  value={form.password}
                  onChange={update("password")}
                  required
                  minLength={8}
                  autoComplete="new-password"
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

            <div>
              <Label className="mb-2 block">Soy:</Label>
              <div className="grid grid-cols-2 gap-2">
                {roles.map((r) => (
                  <label
                    key={r.id}
                    className={`flex items-center gap-2 p-3 rounded-lg border cursor-pointer transition-colors ${
                      form.role === r.id
                        ? "border-sembriaia-action bg-sembriaia-action/5"
                        : "border-border hover:border-sembriaia-action/50"
                    }`}
                  >
                    <input
                      type="radio"
                      name="role"
                      value={r.id}
                      checked={form.role === r.id}
                      onChange={update("role")}
                      className="sr-only"
                    />
                    <span
                      className={`h-4 w-4 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                        form.role === r.id
                          ? "border-sembriaia-action"
                          : "border-muted-foreground/40"
                      }`}
                    >
                      {form.role === r.id && (
                        <span className="h-2 w-2 rounded-full bg-sembriaia-action" />
                      )}
                    </span>
                    <span className="text-sm font-medium">{r.label}</span>
                  </label>
                ))}
              </div>
            </div>

            <label className="flex items-start gap-2 text-sm text-muted-foreground cursor-pointer pt-2">
              <span
                onClick={() => setAccept(!accept)}
                className={`h-5 w-5 rounded border-2 flex items-center justify-center flex-shrink-0 mt-0.5 ${
                  accept ? "bg-sembriaia-action border-sembriaia-action" : "border-input"
                }`}
              >
                {accept && <Check className="h-3 w-3 text-white" />}
              </span>
              <span>
                Acepto los{" "}
                <a href="#" className="text-sembriaia-water hover:underline">términos</a> y el uso de
                datos para trazabilidad EUDR y Ley 261/2024.
              </span>
            </label>

            <Button type="submit" size="lg" className="w-full" disabled={loading}>
              {loading ? "Creando cuenta..." : "Crear cuenta gratis"}
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-muted-foreground">
            ¿Ya tienes cuenta?{" "}
            <Link to="/login" className="text-sembriaia-water font-medium hover:underline">
              Ingresar
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

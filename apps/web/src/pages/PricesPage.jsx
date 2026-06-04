import { useState, useEffect } from "react";
import { TrendingUp, TrendingDown, Minus, Newspaper } from "lucide-react";
import api from "@/api/axios";
import { useAuthStore } from "@/store/authStore";

const ranges = ["Hoy", "7 días", "30 días", "2026"];

const news = [
  { cat: "EUDR", title: "UE ratifica Reglamento de Deforestación para 2026", date: "20 mayo 2026" },
  { cat: "Clima", title: "Lluvias irregulares en Caquetá, IDEAM recomienda diversificar", date: "15 mayo 2026" },
  { cat: "Mercado", title: "FEDECACAO anuncia precio mínimo nacional de $12,500/kg", date: "8 mayo 2026" },
];

function MiniChart({ data, color, height = 80 }) {
  if (!data || data.length === 0) return null;
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  const w = 100 / (data.length - 1);
  const points = data
    .map((v, i) => `${i * w},${height - ((v - min) / range) * (height - 10) - 5}`)
    .join(" ");
  return (
    <svg viewBox={`0 0 100 ${height}`} preserveAspectRatio="none" className="w-full" style={{ height }}>
      <polyline points={points} fill="none" stroke={color} strokeWidth="2" />
      <polyline points={`0,${height} ${points} 100,${height}`} fill={color} opacity="0.1" />
    </svg>
  );
}

function PriceCard({ price }) {
  const change = price.cambio_porcentual ?? 0;
  const Trend = change > 0 ? TrendingUp : change < 0 ? TrendingDown : Minus;
  const trendColor =
    change > 0 ? "text-sembriaia-action" : change < 0 ? "text-sembriaia-alert" : "text-muted-foreground";
  const color = price.color || "#1565C0";
  const history = price.history || Array.from({ length: 30 }, () => price.precio_cop_kg);

  return (
    <div
      className="bg-white rounded-xl border border-border/40 overflow-hidden"
      style={{ borderTop: `4px solid ${color}` }}
    >
      <div className="p-5 sm:p-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-foreground">{price.producto}</h3>
          <span
            className="h-8 w-8 rounded-full flex items-center justify-center text-lg"
            style={{ backgroundColor: `${color}22` }}
          >
            {price.producto.charAt(0)}
          </span>
        </div>
        <div className="text-3xl sm:text-4xl font-bold text-foreground mb-2">
          ${price.precio_cop_kg.toLocaleString("es-CO")}
          <span className="text-base font-normal text-muted-foreground ml-1">COP/{price.unidad}</span>
        </div>
        <div className={`flex items-center gap-1 text-sm font-semibold ${trendColor} mb-3`}>
          <Trend className="h-4 w-4" />
          {change > 0 ? "+" : ""}
          {change.toFixed(1)}%
          <span className="text-xs font-normal text-muted-foreground ml-1">vs. mes anterior</span>
        </div>
        <MiniChart data={history} color={color} />
        <p className="text-[11px] text-muted-foreground mt-2">
          {price.fuente} {price.municipio ? `· ${price.municipio}` : "· Nacional"}
        </p>
      </div>
    </div>
  );
}

export default function PricesPage() {
  const isAuth = useAuthStore((s) => s.isAuthenticated);
  const [range, setRange] = useState("30 días");
  const [prices, setPrices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuth) {
      setLoading(false);
      return;
    }
    let cancelled = false;
    const load = async () => {
      try {
        const res = await api.get("/prices/market-prices");
        if (cancelled) return;
        const colorByProduct = {
          Cacao: "#5D4037",
          Plátano: "#FFEB3B",
          Yuca: "#FF9800",
          Panela: "#795548",
          Leche: "#87CEEB",
          Maíz: "#FFD700",
        };
        const withColor = await Promise.all(
          res.data.map(async (p) => {
            try {
              const h = await api.get(`/prices/market-prices/history/${p.producto}`, {
                params: { days: 30 },
              });
              return {
                ...p,
                color: colorByProduct[p.producto] || "#1565C0",
                history: h.data.map((d) => d.precio_cop_kg),
              };
            } catch {
              return { ...p, color: colorByProduct[p.producto] || "#1565C0" };
            }
          })
        );
        if (!cancelled) setPrices(withColor);
      } catch (e) {
        console.error(e);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => { cancelled = true; };
  }, [isAuth]);

  return (
    <div className="bg-background py-8 sm:py-12">
      <div className="container-app max-w-6xl">
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-foreground mb-2">
            Precios de mercado
          </h1>
          <p className="text-sm text-muted-foreground">
            Actualizado diariamente · Fuentes: FEDECACAO, MinAgricultura
          </p>
        </div>

        {/* Range pills */}
        <div className="flex gap-2 mb-8 overflow-x-auto pb-2">
          {ranges.map((r) => (
            <button
              key={r}
              onClick={() => setRange(r)}
              className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
                range === r
                  ? "bg-sembriaia-action text-white"
                  : "bg-white border border-border text-muted-foreground hover:border-sembriaia-action/40"
              }`}
            >
              {r}
            </button>
          ))}
        </div>

        {/* Prices grid */}
        {!isAuth ? (
          <div className="bg-white rounded-2xl border border-border/40 p-8 text-center">
            <p className="text-muted-foreground mb-4">
              Ingresa para ver los precios actualizados de tu municipio.
            </p>
            <a href="/login" className="text-sembriaia-water font-medium hover:underline">
              Ingresar
            </a>
          </div>
        ) : loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-white rounded-xl border border-border/40 p-6 h-64 animate-pulse" />
            ))}
          </div>
        ) : prices.length === 0 ? (
          <div className="bg-white rounded-2xl border border-border/40 p-8 text-center text-muted-foreground">
            Aún no hay precios registrados.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {prices.map((p) => <PriceCard key={p.producto} price={p} />)}
          </div>
        )}

        {/* News */}
        <div className="mt-16">
          <h2 className="text-xl sm:text-2xl font-semibold text-foreground mb-6 flex items-center gap-2">
            <Newspaper className="h-5 w-5" />
            Noticias que afectan tus cultivos
          </h2>
          <div className="flex gap-4 overflow-x-auto pb-2 -mx-4 px-4">
            {news.map((n, i) => (
              <article
                key={i}
                className="min-w-[280px] max-w-[300px] bg-white rounded-xl border border-border/40 overflow-hidden flex-shrink-0"
              >
                <div
                  className="h-28 bg-gradient-to-br from-sembriaia-primary/20 to-sembriaia-action/20"
                  style={{
                    backgroundImage:
                      "url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=400&q=80')",
                    backgroundSize: "cover",
                    backgroundPosition: "center",
                  }}
                />
                <div className="p-4">
                  <span
                    className={`inline-block text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full mb-2 ${
                      n.cat === "EUDR"
                        ? "bg-sembriaia-primary/10 text-sembriaia-primary"
                        : n.cat === "Clima"
                        ? "bg-sembriaia-water/10 text-sembriaia-water"
                        : "bg-sembriaia-warning/10 text-sembriaia-warning"
                    }`}
                  >
                    {n.cat}
                  </span>
                  <h3 className="text-sm font-semibold text-foreground leading-snug mb-2">
                    {n.title}
                  </h3>
                  <p className="text-xs text-muted-foreground">{n.date}</p>
                </div>
              </article>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

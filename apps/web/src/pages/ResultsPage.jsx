import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import {
  Download, Share2, Trophy, Calendar, CheckCircle2, XCircle, Sprout,
  MapPin, ChevronRight, ArrowLeft, Loader2
} from "lucide-react";
import FarmMap from "@/components/map/FarmMap";
import api from "@/api/axios";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CROPS, COLORS } from "@/config";
import { cn } from "@/lib/utils";

const mockCriteria = [
  { ok: true, text: "Suelo productivo — creció bien 3 años" },
  { ok: true, text: "Pendiente suave (0-5°)" },
  { ok: true, text: "Drenaje adecuado" },
  { ok: true, text: "Precipitación 1,800 mm/año" },
  { ok: true, text: "Cobertura mejorable a cacao" },
  { ok: true, text: "NDVI histórico estable" },
  { ok: false, text: "pH requiere cal (4.8 → 6.5)" },
  { ok: true, text: "Acceso vial a menos de 5 km" },
];

const slopeBreakdown = [
  { label: "0-5°", pct: 55, color: "#00C853" },
  { label: "5-8°", pct: 25, color: "#8BC34A" },
  { label: "8-12°", pct: 15, color: "#FFC107" },
  { label: "12-15°", pct: 5, color: "#FF9800" },
];

const nextSteps = [
  { n: 1, color: COLORS.water, title: "Visita técnica de campo", desc: "Verificar pH y drenaje", action: "Agendar", actionColor: COLORS.water },
  { n: 2, color: COLORS.action, title: "Solicitar crédito agrícola", desc: "Banco Agrario, FEDECACAO", action: "Ver opciones", actionColor: COLORS.action },
  { n: 3, color: COLORS.warning, title: "Comprar semilla certificada", desc: "Proveedores locales", action: "Buscar", actionColor: COLORS.warning },
];

export default function ResultsPage() {
  const { analysisId } = useParams();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState(null);
  const [result, setResult] = useState(null);
  const [cultivo, setCultivo] = useState("cacao");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!analysisId) return;
    let cancelled = false;
    const load = async () => {
      try {
        const [a, r] = await Promise.all([
          api.get(`/analysis/${analysisId}`),
          api.get(`/results/${analysisId}`).catch(() => ({ data: null })),
        ]);
        if (cancelled) return;
        setAnalysis(a.data);
        setCultivo(a.data.cultivo);
        setResult(r.data);
      } catch (e) {
        if (!cancelled) setError("No se pudo cargar el análisis.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => { cancelled = true; };
  }, [analysisId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-sembriaia-action" />
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="text-center py-20">
        <p className="text-muted-foreground mb-4">{error || "Análisis no encontrado"}</p>
        <Button asChild variant="outline">
          <Link to="/dashboard"><ArrowLeft className="h-4 w-4" />Volver al dashboard</Link>
        </Button>
      </div>
    );
  }

  const crop = CROPS[cultivo] || CROPS.cacao;
  const aptas = analysis.hectares_aptas || 0;
  const totales = analysis.hectares_totales || 1;
  const pct = Math.min(100, (aptas / totales) * 100);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
        <div>
          <Button asChild variant="ghost" size="sm" className="mb-2 -ml-2">
            <Link to="/dashboard"><ArrowLeft className="h-4 w-4" />Dashboard</Link>
          </Button>
          <h1 className="text-2xl sm:text-3xl font-bold text-foreground">
            {analysis.farm?.name || "Resultado del análisis"}
          </h1>
          <p className="text-sm text-muted-foreground flex items-center gap-1 mt-1">
            <MapPin className="h-3 w-3" />
            {analysis.farm?.municipio || "Caquetá"} · {totales.toFixed(1)} hectáreas
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={async () => {
              try {
                const res = await api.get(`/reports/${analysisId}/download`, { responseType: "blob" });
                const url = window.URL.createObjectURL(new Blob([res.data]));
                const a = document.createElement("a");
                a.href = url;
                a.download = `sembraria_${analysisId}.pdf`;
                a.click();
              } catch {
                alert("No fue posible generar el PDF.");
              }
            }}
          >
            <Download className="h-4 w-4" />Descargar PDF
          </Button>
          <Button variant="outline"><Share2 className="h-4 w-4" />Compartir</Button>
        </div>
      </div>

      {/* Crop tabs */}
      <div className="border-b border-border overflow-x-auto">
        <div className="flex gap-1 min-w-max">
          {Object.values(CROPS).map((c) => (
            <button
              key={c.id}
              onClick={() => setCultivo(c.id)}
              className={cn(
                "px-5 py-3 text-sm font-medium border-b-2 transition-colors",
                cultivo === c.id
                  ? "border-sembriaia-action text-foreground"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              )}
            >
              {c.label}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4 sm:gap-6">
        {/* Map */}
        <Card className="lg:col-span-3 overflow-hidden p-0">
          {result?.png_url ? (
            <div className="relative">
              <img src={result.png_url} alt="Mapa de aptitud" className="w-full h-[500px] object-cover" />
              <div className="absolute bottom-3 left-3 bg-white/95 rounded-lg p-3 text-xs space-y-1">
                <div className="flex items-center gap-2"><span className="h-3 w-3 rounded-sm bg-sembriaia-action" />Oportunidad</div>
                <div className="flex items-center gap-2"><span className="h-3 w-3 rounded-sm" style={{ backgroundColor: COLORS.pasture }} />Pasto</div>
                <div className="flex items-center gap-2"><span className="h-3 w-3 rounded-sm" style={{ backgroundColor: COLORS.primary }} />Bosque</div>
                <div className="flex items-center gap-2"><span className="h-3 w-3 rounded-sm" style={{ backgroundColor: COLORS.alert }} />Excluido</div>
              </div>
            </div>
          ) : (
            <div className="h-[500px]">
              <FarmMap
                polygons={analysis.farm?.geom?.coordinates?.[0]
                  ? [{ coordinates: analysis.farm.geom.coordinates[0], color: crop.color, properties: {} }]
                  : []}
                height="100%"
              />
            </div>
          )}
        </Card>

        {/* Right column */}
        <div className="lg:col-span-2 space-y-3">
          {/* Summary */}
          <Card className="border-l-4" style={{ borderLeftColor: COLORS.action }}>
            <CardContent className="p-5">
              <p className="text-4xl font-bold text-sembriaia-action">
                {aptas.toFixed(1)} ha
              </p>
              <p className="text-sm text-muted-foreground">aptas para cultivo de {crop.label}</p>
              <p className="text-xs text-muted-foreground/70 mt-1">De {totales.toFixed(1)} ha totales</p>
              {/* Stacked bar */}
              <div className="mt-3 h-3 rounded-full overflow-hidden bg-muted flex">
                <div className="h-full" style={{ width: `${100 - pct}%`, backgroundColor: COLORS.pasture }} />
                <div className="h-full" style={{ width: `${pct}%`, backgroundColor: COLORS.action }} />
              </div>
            </CardContent>
          </Card>

          {/* Economic potential */}
          <Card style={{ backgroundColor: "#F0FFF4" }} className="border-sembriaia-action/20">
            <CardContent className="p-5">
              <p className="text-xs text-muted-foreground font-medium">Potencial de ingreso anual</p>
              <p className="text-3xl font-bold text-sembriaia-action mt-1">
                ${(aptas * 4.2).toFixed(1)}M COP
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                con {crop.label} · Precio FEDECACAO 2026
              </p>
              {/* Mini chart */}
              <div className="mt-3 flex items-end gap-1 h-12">
                {[3, 4, 5, 6, 7].map((y) => (
                  <div
                    key={y}
                    className="flex-1 rounded-t bg-sembriaia-action/40"
                    style={{ height: `${30 + y * 8}%` }}
                  />
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Ranking */}
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <Trophy className="h-5 w-5 text-sembriaia-water flex-shrink-0" />
              <div>
                <p className="text-sm font-semibold">Top 12% de productividad en Caquetá</p>
                <p className="text-xs text-muted-foreground">Basado en NDVI histórico 2022-2024</p>
              </div>
            </CardContent>
          </Card>

          {/* Criteria checklist */}
          <Card>
            <CardContent className="p-5">
              <h3 className="text-sm font-semibold mb-3">¿Por qué esta zona es apta?</h3>
              <ul className="space-y-2">
                {mockCriteria.map((c, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    {c.ok ? (
                      <CheckCircle2 className="h-4 w-4 text-sembriaia-action flex-shrink-0 mt-0.5" />
                    ) : (
                      <XCircle className="h-4 w-4 text-sembriaia-alert flex-shrink-0 mt-0.5" />
                    )}
                    <span className={cn(c.ok ? "text-foreground" : "text-sembriaia-alert")}>
                      {c.text}
                    </span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Slope breakdown */}
          <Card>
            <CardContent className="p-5">
              <h3 className="text-sm font-semibold mb-3">Distribución por pendiente</h3>
              <div className="h-3 rounded-full overflow-hidden bg-muted flex mb-2">
                {slopeBreakdown.map((s) => (
                  <div key={s.label} className="h-full" style={{ width: `${s.pct}%`, backgroundColor: s.color }} />
                ))}
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                {slopeBreakdown.map((s) => (
                  <div key={s.label} className="flex items-center gap-2">
                    <span className="h-2 w-2 rounded-sm" style={{ backgroundColor: s.color }} />
                    {s.label} · {s.pct}%
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Next steps */}
          <Card>
            <CardContent className="p-5">
              <h3 className="text-sm font-semibold mb-3">Próximos pasos</h3>
              <ul className="space-y-3">
                {nextSteps.map((step) => (
                  <li key={step.n} className="flex items-start gap-3">
                    <span
                      className="h-7 w-7 rounded-full flex items-center justify-center text-white text-xs font-semibold flex-shrink-0"
                      style={{ backgroundColor: step.color }}
                    >
                      {step.n}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">{step.title}</p>
                      <p className="text-xs text-muted-foreground">{step.desc}</p>
                      <a href="#" className="text-xs font-medium hover:underline" style={{ color: step.actionColor }}>
                        {step.action}
                      </a>
                    </div>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

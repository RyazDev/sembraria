import { useEffect, useState } from "react";
import { FileText, Shield, Users, BarChart3, Check, Download, Mail, Share2, ChevronRight, Sprout, MapPin } from "lucide-react";
import api from "@/api/axios";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const reportTypes = [
  { id: "tecnico", title: "Reporte técnico completo", desc: "Para bancos y gobierno. Mapa, series temporales, criterios, metodología.", icon: FileText, color: "#1565C0", sections: ["Mapa", "Series temporales", "Criterios", "Metodología"] },
  { id: "eudr", title: "Declaración EUDR / Ley 261", desc: "Para compradores europeos. Trazabilidad, deforestación, cadena de custodia.", icon: Shield, color: "#1B5E20", sections: ["Trazabilidad", "Deforestación", "Cadena de custodia"] },
  { id: "cooperativa", title: "Resumen para cooperativa", desc: "Para cooperativas locales. Área apta, cultivos recomendados, próximos pasos.", icon: Users, color: "#795548", sections: ["Área apta", "Cultivos", "Próximos pasos"] },
  { id: "comparativo", title: "Análisis comparativo", desc: "Compara múltiples años. Evolución NDVI, cambios de cobertura.", icon: BarChart3, color: "#FF9800", sections: ["Comparativa anual", "NDVI", "Cobertura"] },
];

export default function ReportsPage() {
  const [step, setStep] = useState(1);
  const [farms, setFarms] = useState([]);
  const [selectedFarm, setSelectedFarm] = useState(null);
  const [selectedType, setSelectedType] = useState(null);
  const [analyses, setAnalyses] = useState([]);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);

  useEffect(() => {
    api.get("/farms").then((r) => setFarms(r.data)).catch(() => {});
  }, []);

  useEffect(() => {
    if (!selectedFarm) {
      setAnalyses([]);
      setSelectedAnalysis(null);
      return;
    }
    api.get(`/analysis?farm_id=${selectedFarm}`).then((r) => {
      setAnalyses(r.data);
      if (r.data.length > 0) setSelectedAnalysis(r.data[0].id);
    }).catch(() => setAnalyses([]));
  }, [selectedFarm]);

  const handleDownload = async () => {
    if (!selectedAnalysis) return;
    try {
      const res = await api.get(`/reports/${selectedAnalysis}/download`, { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement("a");
      a.href = url;
      a.download = `sembraria_${selectedAnalysis}.pdf`;
      a.click();
    } catch (e) {
      alert("No fue posible generar el PDF. Verifica que haya un análisis completado.");
    }
  };

  const steps = [
    { n: 1, l: "Seleccionar finca" },
    { n: 2, l: "Tipo de reporte" },
    { n: 3, l: "Descargar" },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-foreground">Generar reporte</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Para trazabilidad, crédito y cumplimiento
        </p>
      </div>

      {/* Stepper */}
      <div className="flex items-center">
        {steps.map((s, i) => (
          <div key={s.n} className="flex items-center flex-1 last:flex-initial">
            <div className="flex items-center gap-2">
              <div
                className={cn(
                  "h-9 w-9 rounded-full flex items-center justify-center text-sm font-semibold",
                  step >= s.n ? "bg-sembriaia-action text-white" : "bg-muted text-muted-foreground"
                )}
              >
                {step > s.n ? <Check className="h-4 w-4" /> : s.n}
              </div>
              <span className={cn("text-xs sm:text-sm font-medium", step >= s.n ? "text-foreground" : "text-muted-foreground")}>
                {s.l}
              </span>
            </div>
            {i < steps.length - 1 && (
              <div className={cn("flex-1 h-0.5 mx-2 sm:mx-4", step > s.n ? "bg-sembriaia-action" : "bg-border")} />
            )}
          </div>
        ))}
      </div>

      {/* Step 1: Farm selection */}
      {step === 1 && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Selecciona una finca</h2>
          {farms.length === 0 ? (
            <Card className="p-8 text-center">
              <Sprout className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
              <p className="text-muted-foreground mb-4">Aún no tienes fincas registradas</p>
              <Button onClick={() => (window.location.href = "/analizar")}>Crear primera finca</Button>
            </Card>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {farms.map((f) => (
                <button
                  key={f.id}
                  onClick={() => { setSelectedFarm(f.id); setStep(2); }}
                  className={cn(
                    "text-left bg-white rounded-xl border-2 p-4 hover:border-sembriaia-action transition-colors",
                    selectedFarm === f.id ? "border-sembriaia-action" : "border-border/40"
                  )}
                >
                  <div className="h-24 rounded-lg bg-gradient-to-br from-sembriaia-action/20 to-sembriaia-primary/20 mb-3" />
                  <p className="font-semibold text-foreground">{f.name}</p>
                  <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                    <MapPin className="h-3 w-3" />
                    {f.municipio}
                  </p>
                  <p className="text-xs text-sembriaia-action mt-1">
                    {f.area_ha?.toFixed(1)} ha registradas
                  </p>
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Step 2: Report type */}
      {step === 2 && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Tipo de reporte</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {reportTypes.map((r) => {
              const Icon = r.icon;
              const selected = selectedType === r.id;
              return (
                <button
                  key={r.id}
                  onClick={() => { setSelectedType(r.id); setStep(3); }}
                  className={cn(
                    "text-left bg-white rounded-xl border-2 p-5 hover:border-sembriaia-action transition-colors",
                    selected ? "border-sembriaia-action" : "border-border/40"
                  )}
                >
                  <div className="flex items-start gap-3">
                    <div
                      className="h-10 w-10 rounded-lg flex items-center justify-center flex-shrink-0"
                      style={{ backgroundColor: `${r.color}15` }}
                    >
                      <Icon className="h-5 w-5" style={{ color: r.color }} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-foreground mb-1">{r.title}</p>
                      <p className="text-xs text-muted-foreground mb-2">{r.desc}</p>
                      <div className="flex flex-wrap gap-1">
                        {r.sections.map((s) => (
                          <Badge key={s} variant="secondary" className="text-[10px]">{s}</Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
          <Button variant="ghost" onClick={() => setStep(1)}>← Atrás</Button>
        </div>
      )}

      {/* Step 3: Download */}
      {step === 3 && (
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
          {/* Preview */}
          <Card className="lg:col-span-3 p-6">
            <h3 className="font-semibold mb-4">Vista previa del reporte</h3>
            <div className="space-y-3">
              {analyses.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  Esta finca no tiene análisis completados. Genera uno antes de descargar.
                </p>
              ) : (
                <>
                  <p className="text-sm text-muted-foreground mb-3">
                    Análisis disponibles ({analyses.length}):
                  </p>
                  {analyses.map((a) => (
                    <label key={a.id} className="flex items-center gap-3 p-3 rounded-lg border border-border/40 cursor-pointer hover:bg-muted">
                      <input
                        type="radio"
                        name="analysis"
                        checked={selectedAnalysis === a.id}
                        onChange={() => setSelectedAnalysis(a.id)}
                        className="text-sembriaia-action"
                      />
                      <div className="flex-1">
                        <p className="text-sm font-medium">
                          Análisis de {a.cultivo} · {a.hectares_aptas?.toFixed(1) || 0} ha aptas
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(a.created_at).toLocaleString("es-CO")}
                        </p>
                      </div>
                    </label>
                  ))}
                  <div className="mt-4 aspect-[3/4] rounded-lg border border-border bg-muted/30 flex items-center justify-center text-sm text-muted-foreground">
                    Vista previa del PDF (4 páginas)
                  </div>
                </>
              )}
            </div>
          </Card>

          {/* Actions */}
          <Card className="lg:col-span-2 p-6 space-y-3">
            <h3 className="font-semibold">Acciones</h3>
            <Button onClick={handleDownload} disabled={!selectedAnalysis} className="w-full" size="lg">
              <Download className="h-4 w-4" /> Descargar PDF
            </Button>
            <Button variant="outline" className="w-full" size="lg">
              <Mail className="h-4 w-4" /> Enviar por correo
            </Button>
            <Button variant="outline" className="w-full" size="lg">
              <Share2 className="h-4 w-4" /> Compartir enlace
            </Button>
            <div className="pt-3 border-t border-border/40 text-xs text-muted-foreground space-y-1">
              <p>4 páginas · 2.4 MB</p>
              <p>Generado el {new Date().toLocaleDateString("es-CO")}</p>
              <p>Datos Copernicus verificables</p>
            </div>
            <Button variant="ghost" onClick={() => setStep(2)} className="w-full">← Atrás</Button>
          </Card>
        </div>
      )}
    </div>
  );
}

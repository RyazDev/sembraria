import { Satellite, Database, Cpu, FileCheck, MapPinned, MessageSquare, Filter, Send, Sprout, AlertTriangle, ExternalLink } from "lucide-react";
import { Link } from "react-router-dom";
import { COLORS } from "@/config";

const sources = [
  { name: "Sentinel-2", desc: "Imágenes ópticas 10m, 13 bandas. Cloud Score+ para filtrar nubes.", spec: "Resolución: 10m · Revisita: 5 días · Fuente: ESA/Copernicus" },
  { name: "Sentinel-1 SAR", desc: "Radar de apertura sintética, penetra nubes. Coherencia y backscatter.", spec: "Resolución: 10m · Revisita: 6 días · Banda C" },
  { name: "ERA5-Land", desc: "Variables climáticas horarias reanalizadas. Precipitación, temperatura.", spec: "Resolución: 9km · 1950-presente · ECMWF/Copernicus" },
  { name: "MODIS LST", desc: "Temperatura superficial diaria. Variable regional.", spec: "Resolución: 1km · Diaria · NASA" },
  { name: "SRTM", desc: "Modelo de elevación. Pendiente, orientación, drenaje.", spec: "Resolución: 30m · NASA/USGS" },
  { name: "ESA WorldCover", desc: "Cobertura del suelo 2021. Validación vs realidad local.", spec: "Resolución: 10m · ESA" },
];

const pipeline = [
  { color: COLORS.water, title: "Carga de datos", desc: "5 fuentes satelitales sincronizadas para Caquetá." },
  { color: COLORS.water, title: "Preprocesamiento", desc: "Cloud Score+, medianas, índices espectrales." },
  { color: COLORS.action, title: "Fenología", desc: "Amplitud e integral NDVI 2022-2024 (Ismaili et al., 2024)." },
  { color: COLORS.action, title: "Clasificación", desc: "Random Forest + Gradient Boosted Trees, 30 features." },
  { color: COLORS.action, title: "Validación", desc: "K-Fold K=5 + test set 30%. Accuracy y Kappa reportados." },
  { color: COLORS.warning, title: "Oportunidad", desc: "13 exclusiones + 8 inclusiones por cultivo específico." },
  { color: COLORS.warning, title: "Post-proceso", desc: "Filtro moda 3x3, sin forzar WorldCover (error 23%)." },
  { color: COLORS.primary, title: "Entrega", desc: "Mapa interactivo, alertas SMS, reporte PDF." },
];

export default function MethodologyPage() {
  return (
    <div className="bg-background">
      {/* Header */}
      <section className="bg-white border-b border-border/40 py-12 sm:py-16">
        <div className="container-app max-w-4xl text-center">
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-foreground mb-3">
            Metodología y fuentes de datos
          </h1>
          <p className="text-lg text-muted-foreground">
            Cómo funciona SembrarIA y por qué puedes confiar en los resultados
          </p>
        </div>
      </section>

      {/* Data sources */}
      <section className="py-12 sm:py-16">
        <div className="container-app max-w-6xl">
          <h2 className="text-2xl font-semibold text-foreground mb-8">Fuentes de datos</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sources.map((s) => (
              <div key={s.name} className="bg-white rounded-xl border border-border/40 p-6">
                <div className="flex items-center gap-3 mb-3">
                  <div className="h-10 w-10 rounded-lg bg-sembriaia-primary/10 flex items-center justify-center">
                    <Satellite className="h-5 w-5 text-sembriaia-primary" />
                  </div>
                  <h3 className="font-semibold text-foreground">{s.name}</h3>
                </div>
                <p className="text-sm text-muted-foreground mb-3">{s.desc}</p>
                <p className="text-xs text-muted-foreground/80">{s.spec}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pipeline */}
      <section className="bg-white py-12 sm:py-16">
        <div className="container-app max-w-4xl">
          <h2 className="text-2xl font-semibold text-foreground mb-8">Pipeline de análisis</h2>
          <div className="relative pl-8 border-l-2 border-border">
            {pipeline.map((p, i) => (
              <div key={i} className="relative mb-8 last:mb-0">
                <span
                  className="absolute -left-[37px] top-1 h-5 w-5 rounded-full border-4 border-white"
                  style={{ backgroundColor: p.color }}
                />
                <h3 className="text-base font-semibold text-foreground mb-1">{p.title}</h3>
                <p className="text-sm text-muted-foreground">{p.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Validation metrics */}
      <section className="py-12 sm:py-16">
        <div className="container-app max-w-5xl">
          <div className="bg-sembriaia-action/5 border border-sembriaia-action/20 rounded-2xl p-8">
            <h2 className="text-xl font-semibold text-foreground mb-6">Métricas de validación</h2>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-4">
              {[
                { v: "0.78", l: "Accuracy", s: "± 3%" },
                { v: "0.74", l: "Kappa", s: "± 3%" },
                { v: "0.76", l: "F1-Score", s: "± 3%" },
                { v: "K=5", l: "Validación", s: "K-Fold" },
              ].map((m) => (
                <div key={m.l} className="text-center">
                  <div className="text-3xl sm:text-4xl font-bold text-sembriaia-action mb-1">
                    {m.v}
                  </div>
                  <div className="text-sm text-muted-foreground">{m.l}</div>
                  <div className="text-xs text-muted-foreground/70">{m.s}</div>
                </div>
              ))}
            </div>
            <p className="text-xs text-muted-foreground">
              Valores exactos dependen de los puntos de entrenamiento generados por el usuario.
            </p>
          </div>
        </div>
      </section>

      {/* Limitations */}
      <section className="py-12 sm:py-16">
        <div className="container-app max-w-4xl">
          <div className="bg-white rounded-2xl border-l-4 border-sembriaia-warning p-6 sm:p-8">
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="h-5 w-5 text-sembriaia-warning" />
              <h2 className="text-lg font-semibold text-sembriaia-warning">Limitaciones conocidas</h2>
            </div>
            <ul className="space-y-3 text-sm text-foreground">
              <li className="flex gap-3">
                <span className="text-sembriaia-warning">•</span>
                WorldCover v200 clasifica palma aceitera como bosque. Usamos estrategia híbrida
                NDBI+SAR.
              </li>
              <li className="flex gap-3">
                <span className="text-sembriaia-warning">•</span>
                Suelos de Caquetá (Oxisoles pH 4.5-5.8) requieren enmienda para cacao. El mapa
                indica potencial biofísico; viabilidad edafológica final requiere campo.
              </li>
              <li className="flex gap-3">
                <span className="text-sembriaia-warning">•</span>
                MODIS LST a 1km se usa como variable regional, no de finca individual.
              </li>
            </ul>
            <a
              href="#"
              className="inline-flex items-center gap-1 mt-5 text-sm font-medium text-sembriaia-water hover:underline"
            >
              Ver documentación completa <ExternalLink className="h-3 w-3" />
            </a>
          </div>
        </div>
      </section>

      {/* Citations */}
      <section className="bg-white py-12 sm:py-16">
        <div className="container-app max-w-3xl">
          <h2 className="text-2xl font-semibold text-foreground mb-6">Referencias académicas</h2>
          <ol className="space-y-3 text-sm text-foreground/90 list-decimal pl-5">
            <li>
              Ismaili et al. (2024). <em>Phenological approach for agricultural suitability</em>.
              Heliyon.
            </li>
            <li>
              Silva-Olaya et al. (2021). <em>Soil characterization in Caquetá</em>. Agronomy.
            </li>
            <li>
              ESA WorldCover v200 Product Validation Report.
            </li>
          </ol>
        </div>
      </section>
    </div>
  );
}

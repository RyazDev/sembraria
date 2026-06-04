import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Layers, ArrowRight } from "lucide-react";
import FarmMap from "@/components/map/FarmMap";
import { Button } from "@/components/ui/button";
import { CROPS } from "@/config";

const municipios = [
  "Todos", "Florencia", "Belén de los Andaquíes", "El Doncello",
  "San Vicente del Caguán", "Cartagena del Chairá", "Albania", "Curillo", "Morelia"
];

export default function RegionalMapPage() {
  const navigate = useNavigate();
  const [cultivo, setCultivo] = useState("cacao");
  const [municipio, setMunicipio] = useState("Todos");
  return (
    <div className="relative h-[calc(100vh-72px)] w-full">
      <FarmMap height="100%" zoom={7} />

      {/* Left panel */}
      <div className="absolute top-4 sm:top-6 left-4 sm:left-6 w-[calc(100%-2rem)] sm:w-[400px] max-h-[calc(100%-3rem)] overflow-y-auto bg-white rounded-2xl shadow-lg p-5 sm:p-6 z-10 animate-fade-in">
        <h2 className="text-xl font-bold text-foreground mb-1">
          Oportunidad agrícola en Caquetá
        </h2>
        <p className="text-sm text-muted-foreground mb-5">
          Datos agregados de 500+ fincas analizadas
        </p>

        <div className="grid grid-cols-2 gap-4 mb-5">
          <div>
            <div className="text-2xl sm:text-3xl font-bold text-sembriaia-action">1,247 ha</div>
            <div className="text-xs text-muted-foreground">aptas para reconversión</div>
          </div>
          <div>
            <div className="text-2xl sm:text-3xl font-bold text-sembriaia-primary">3</div>
            <div className="text-xs text-muted-foreground">cultivos evaluados</div>
          </div>
        </div>

        {/* Municipio selector */}
        <div className="mb-4">
          <label className="text-xs font-medium text-muted-foreground mb-1.5 block">
            Municipio
          </label>
          <select
            value={municipio}
            onChange={(e) => setMunicipio(e.target.value)}
            className="w-full h-10 px-3 rounded-lg border border-input bg-white text-sm focus:outline-none focus:ring-2 focus:ring-sembriaia-action"
          >
            {municipios.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>

        {/* Cultivo selector */}
        <div className="mb-5">
          <label className="text-xs font-medium text-muted-foreground mb-1.5 block">Cultivo</label>
          <div className="grid grid-cols-3 gap-2">
            {Object.values(CROPS).map((c) => (
              <button
                key={c.id}
                onClick={() => setCultivo(c.id)}
                className={`py-2 px-3 rounded-lg text-sm font-medium border-2 transition-colors ${
                  cultivo === c.id
                    ? "border-sembriaia-action bg-sembriaia-action/10 text-sembriaia-action"
                    : "border-border text-muted-foreground hover:border-sembriaia-action/40"
                }`}
              >
                {c.label}
              </button>
            ))}
          </div>
        </div>

        {/* Legend */}
        <div className="mb-5 pb-5 border-b border-border">
          <div className="text-xs font-medium text-muted-foreground mb-2">Leyenda</div>
          <div className="space-y-1.5">
            {[
              { c: "#00C853", l: "Oportunidad alta" },
              { c: "#D4A574", l: "Pasto dominante" },
              { c: "#1B5E20", l: "Reserva forestal" },
              { c: "#1565C0", l: "Cuerpo de agua" },
            ].map((x) => (
              <div key={x.l} className="flex items-center gap-2 text-xs">
                <span className="h-3 w-3 rounded-sm" style={{ backgroundColor: x.c }} />
                <span>{x.l}</span>
              </div>
            ))}
          </div>
        </div>

        <p className="text-[11px] text-muted-foreground/80 mb-4">
          Datos: Sentinel-2, Sentinel-1, ERA5, MODIS, SRTM · Modelo v7.1
        </p>

        <Button className="w-full" size="lg" onClick={() => navigate("/register")}>
          Analizar mi finca <ArrowRight className="h-4 w-4" />
        </Button>
      </div>

      {/* Bottom-right impact card */}
      <div className="hidden sm:block absolute bottom-4 right-4 sm:bottom-6 sm:right-6 w-[300px] bg-white rounded-xl shadow-lg p-4 z-10 animate-fade-in">
        <div className="text-sm font-semibold text-foreground mb-3">Impacto estimado</div>
        <div className="mb-3">
          <div className="text-2xl font-bold text-sembriaia-action">~3,800 ton/año</div>
          <div className="text-xs text-muted-foreground">de alimentos locales</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-sembriaia-water">~$12,000M/año</div>
          <div className="text-xs text-muted-foreground">ahorro en importación</div>
        </div>
      </div>
    </div>
  );
}

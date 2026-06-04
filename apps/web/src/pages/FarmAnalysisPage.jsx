import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import maplibregl from "maplibre-gl";
import {
  MapPin, Square, Circle, Crosshair, Undo2, Trash2, AlertCircle,
  Sprout, Save, Loader2, CheckCircle2, ChevronRight
} from "lucide-react";
import FarmMap from "@/components/map/FarmMap";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import api from "@/api/axios";
import { useAuthStore } from "@/store/authStore";
import { config, COLORS, CROPS } from "@/config";

const municipios = [
  "Florencia", "Belén de los Andaquíes", "El Doncello", "San Vicente del Caguán",
  "Cartagena del Chairá", "Albania", "Curillo", "Morelia", "Valparaíso", "Solita", "Milán", "Puerto Rico",
];

function areaInHectares(coords) {
  if (!coords || coords.length < 3) return 0;
  const R = 6378137;
  const toRad = (d) => (d * Math.PI) / 180;
  let area = 0;
  for (let i = 0; i < coords.length - 1; i++) {
    const [lng1, lat1] = coords[i];
    const [lng2, lat2] = coords[i + 1];
    area +=
      toRad(lng2 - lng1) *
      (2 + Math.sin(toRad(lat1)) + Math.sin(toRad(lat2)));
  }
  return Math.abs((area * R * R) / 2) / 10000;
}

function pointInCaqueta([lng, lat]) {
  const [w, s, e, n] = config.map.caquetaBbox;
  return lng >= w && lng <= e && lat >= s && lat <= n;
}

export default function FarmAnalysisPage() {
  const navigate = useNavigate();
  const { farmId } = useParams();
  const user = useAuthStore((s) => s.user);
  const [polygon, setPolygon] = useState(null);
  const [name, setName] = useState("");
  const [municipio, setMunicipio] = useState(municipios[0]);
  const [area, setArea] = useState("");
  const [cultivo, setCultivo] = useState("cacao");
  const [phone, setPhone] = useState(user?.phone || "");
  const [accept, setAccept] = useState(false);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [drawingMode, setDrawingMode] = useState("polygon");
  const [points, setPoints] = useState([]);

  // Quick polygon demo: when user clicks the demo button, generate a polygon in Caquetá
  const loadDemoPolygon = () => {
    const center = config.map.defaultCenter;
    const size = 0.04; // ~4.4 km
    const demo = [
      [center[0] - size, center[1] - size * 0.7],
      [center[0] + size, center[1] - size * 0.7],
      [center[0] + size, center[1] + size * 0.7],
      [center[0] - size, center[1] + size * 0.7],
      [center[0] - size, center[1] - size * 0.7],
    ];
    setPolygon(demo);
    setPoints(demo);
    setArea(areaInHectares(demo).toFixed(2));
  };

  useEffect(() => {
    if (farmId) {
      api.get(`/farms/${farmId}`).then((r) => {
        const f = r.data;
        setName(f.name);
        setMunicipio(f.municipio);
        setArea(f.area_ha?.toString());
        if (f.geom?.coordinates?.[0]) {
          setPolygon(f.geom.coordinates[0]);
          setPoints(f.geom.coordinates[0]);
        }
      }).catch(() => {});
    }
  }, [farmId]);

  const polygons = polygon ? [{ coordinates: polygon, color: COLORS.action, properties: {} }] : [];

  const validForm = polygon && name && area && cultivo && accept;
  const outsideCaqueta = polygon && !polygon.slice(0, -1).every(pointInCaqueta);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validForm) {
      setError("Dibuja el polígono y completa todos los campos.");
      return;
    }
    if (outsideCaqueta) {
      setError("La finca está fuera del departamento de Caquetá.");
      return;
    }
    setError("");
    setSubmitting(true);
    try {
      let currentFarmId = farmId;
      if (!currentFarmId) {
        const farmRes = await api.post("/farms", {
          name,
          municipio,
          area_ha: parseFloat(area),
          geom: { type: "Polygon", coordinates: [polygon] },
          notes: "",
        });
        currentFarmId = farmRes.data.id;
      }
      const analysisRes = await api.post(`/analysis/farms/${currentFarmId}/analyze`, {
        cultivo,
      });
      navigate(`/resultados/${analysisRes.data.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || "No fue posible procesar el análisis.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-foreground">
            {farmId ? "Reanalizar finca" : "Analizar nueva finca"}
          </h1>
          <p className="text-sm text-muted-foreground mt-1">Paso 1 de 2 · Dibuja tu finca en el mapa</p>
        </div>
        <Button variant="outline" onClick={loadDemoPolygon} size="sm">
          <MapPin className="h-4 w-4" />
          Usar polígono demo (Florencia)
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 sm:gap-6">
        {/* Map */}
        <div className="lg:col-span-7 space-y-3">
          <div className="relative">
            <FarmMap polygons={polygons} height="500px" />
            {/* Drawing tools floating */}
            <div className="absolute top-3 left-3 bg-white rounded-lg shadow-md p-1 flex gap-1 z-10">
              {[
                { id: "polygon", icon: Square },
                { id: "rectangle", icon: Square },
                { id: "circle", icon: Circle },
                { id: "gps", icon: Crosshair },
              ].map((t) => {
                const Icon = t.icon;
                return (
                  <button
                    key={t.id}
                    onClick={() => setDrawingMode(t.id)}
                    className={`h-9 w-9 rounded flex items-center justify-center ${
                      drawingMode === t.id ? "bg-sembriaia-action text-white" : "hover:bg-muted"
                    }`}
                    title={t.id}
                  >
                    <Icon className="h-4 w-4" />
                  </button>
                );
              })}
              <div className="w-px bg-border my-1" />
              <button
                onClick={() => { setPolygon(null); setPoints([]); setArea(""); }}
                className="h-9 w-9 rounded flex items-center justify-center hover:bg-muted"
                title="Limpiar"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
            {/* Instructions overlay */}
            <div className="absolute top-3 left-1/2 -translate-x-1/2 bg-black/70 text-white text-xs px-3 py-1.5 rounded-full">
              Dibuja el límite de tu finca o usa el botón demo
            </div>
          </div>

          {outsideCaqueta && (
            <div className="flex items-start gap-2 p-3 rounded-lg bg-sembriaia-alert/10 border border-sembriaia-alert/30 text-sm text-sembriaia-alert">
              <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
              <span>Esta zona está fuera de Caquetá. SembrarIA solo opera en Caquetá.</span>
            </div>
          )}

          <div className="text-xs text-muted-foreground">
            Tip: usa el botón "Polígono demo" para ver el flujo completo sin necesidad de dibujar.
          </div>
        </div>

        {/* Form */}
        <Card className="lg:col-span-5">
          <CardContent className="p-5 sm:p-6 space-y-4">
            <div>
              <Label htmlFor="name" className="mb-1.5 block">Nombre de la finca</Label>
              <Input id="name" placeholder="Ej. Finca La Esperanza" value={name} onChange={(e) => setName(e.target.value)} required />
            </div>

            <div>
              <Label htmlFor="municipio" className="mb-1.5 block">Municipio</Label>
              <select
                id="municipio"
                value={municipio}
                onChange={(e) => setMunicipio(e.target.value)}
                className="w-full h-12 px-3 rounded-lg border border-input bg-white text-sm"
              >
                {municipios.map((m) => <option key={m} value={m}>{m}</option>)}
              </select>
            </div>

            <div>
              <Label htmlFor="area" className="mb-1.5 block">Hectáreas</Label>
              <Input
                id="area"
                type="number"
                step="0.1"
                min="0.1"
                max="1000"
                placeholder="0.0"
                value={area}
                onChange={(e) => setArea(e.target.value)}
                required
              />
              <p className="text-xs text-muted-foreground mt-1">
                {polygon ? `Calculado del polígono: ${areaInHectares(polygon).toFixed(2)} ha` : "Dibuja un polígono para autocalcular"}
              </p>
            </div>

            <div>
              <Label className="mb-2 block">Cultivo de interés</Label>
              <div className="grid grid-cols-3 gap-2">
                {Object.values(CROPS).map((c) => (
                  <button
                    key={c.id}
                    type="button"
                    onClick={() => setCultivo(c.id)}
                    className={`p-3 rounded-lg border-2 text-center transition-colors ${
                      cultivo === c.id
                        ? "border-sembriaia-action bg-sembriaia-action/5"
                        : "border-border hover:border-sembriaia-action/40"
                    }`}
                  >
                    <div
                      className="h-10 w-10 rounded-full mx-auto mb-2 flex items-center justify-center text-white"
                      style={{ backgroundColor: c.color }}
                    >
                      <Sprout className="h-5 w-5" />
                    </div>
                    <p className="text-sm font-semibold">{c.label}</p>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <Label htmlFor="phone" className="mb-1.5 block">Teléfono para alertas SMS</Label>
              <Input id="phone" type="tel" placeholder="+57 3XX XXXXXXX" value={phone} onChange={(e) => setPhone(e.target.value)} />
            </div>

            <label className="flex items-start gap-2 text-sm text-muted-foreground cursor-pointer">
              <span
                onClick={() => setAccept(!accept)}
                className={`h-5 w-5 rounded border-2 flex items-center justify-center flex-shrink-0 mt-0.5 ${
                  accept ? "bg-sembriaia-action border-sembriaia-action" : "border-input"
                }`}
              >
                {accept && <CheckCircle2 className="h-3 w-3 text-white" />}
              </span>
              <span>
                Acepto el uso de datos para trazabilidad EUDR y Ley 261/2024.
              </span>
            </label>

            {error && (
              <div className="p-3 rounded-lg bg-sembriaia-alert/10 border border-sembriaia-alert/20 text-sm text-sembriaia-alert flex gap-2">
                <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            <Button
              onClick={handleSubmit}
              disabled={!validForm || submitting}
              size="lg"
              className="w-full"
            >
              {submitting ? (
                <><Loader2 className="h-4 w-4 animate-spin" />Procesando análisis...</>
              ) : (
                <>{farmId ? "Reanalizar" : "Analizar finca"}<ChevronRight className="h-4 w-4" /></>
              )}
            </Button>
            <p className="text-xs text-muted-foreground text-center">
              Duración típica: 5-30 segundos
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

import { useEffect, useState } from "react";
import { Droplets, Trees, DollarSign, Sun, CheckCircle2, Filter } from "lucide-react";
import api from "@/api/axios";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { COLORS } from "@/config";

const filters = ["Todas", "Estrés hídrico", "Deforestación", "Precios", "Clima"];

const typeConfig = {
  hidrico: { color: COLORS.alert, icon: Droplets, label: "Estrés hídrico detectado" },
  deforestacion: { color: COLORS.warning, icon: Trees, label: "Cambio de uso de suelo cercano" },
  precio: { color: COLORS.water, icon: DollarSign, label: "Alza de precio" },
  clima: { color: COLORS.urban, icon: Sun, label: "Pronóstico climático" },
  ok: { color: COLORS.action, icon: CheckCircle2, label: "Todo normal" },
};

const days = ["L", "M", "X", "J", "V", "S", "D"];

function AlertCard({ alert }) {
  const cfg = typeConfig[alert.type] || typeConfig.clima;
  const Icon = cfg.icon;
  return (
    <div
      className="bg-white rounded-xl border border-border/40 p-5 shadow-sm border-l-4"
      style={{ borderLeftColor: cfg.color }}
    >
      <div className="flex items-start gap-3 mb-3">
        <div
          className="h-10 w-10 rounded-full flex items-center justify-center flex-shrink-0"
          style={{ backgroundColor: `${cfg.color}15` }}
        >
          <Icon className="h-5 w-5" style={{ color: cfg.color }} />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-sm sm:text-base" style={{ color: cfg.color }}>
            {cfg.label}
          </h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            {alert.farm_name || "Finca"} · {alert.message?.slice(0, 60) || ""}
          </p>
        </div>
        <span className="text-xs text-muted-foreground flex-shrink-0">
          {new Date(alert.created_at).toLocaleDateString("es-CO")}
        </span>
      </div>
      <p className="text-sm text-foreground/80 leading-relaxed mb-3">{alert.message}</p>
      <div className="flex flex-wrap gap-2">
        <Button size="sm" variant="outline">Ver en mapa</Button>
        <Button
          size="sm"
          onClick={async () => {
            try {
              await api.put(`/alerts/${alert.id}/read`, { is_read: true });
            } catch {}
          }}
        >
          Marcar como atendida
        </Button>
      </div>
    </div>
  );
}

export default function AlertsPage() {
  const [filter, setFilter] = useState("Todas");
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const res = await api.get("/alerts");
        if (!cancelled) setAlerts(res.data);
      } catch (e) {
        console.error(e);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => { cancelled = true; };
  }, []);

  // Mocks when DB has no alerts
  const displayAlerts = alerts.length > 0 ? alerts : [
    { id: "m1", type: "hidrico", created_at: new Date().toISOString(), message: "Riegue en las próximas 48 horas. Lluvia prevista para jueves según ERA5.", farm_name: "Finca La Esperanza" },
    { id: "m2", type: "deforestacion", created_at: new Date(Date.now() - 86400000).toISOString(), message: "2.1 ha deforestadas a 800m de su finca. Puede afectar certificación EUDR.", farm_name: "Finca El Porvenir" },
    { id: "m3", type: "precio", created_at: new Date(Date.now() - 2 * 86400000).toISOString(), message: "FEDECACAO: $12,500/kg. Buen momento para planificar cosecha.", farm_name: "Finca La Esperanza" },
    { id: "m4", type: "ok", created_at: new Date(Date.now() - 3 * 86400000).toISOString(), message: "NDVI estable. Sin anomalías detectadas en los últimos 30 días.", farm_name: "Finca El Porvenir" },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-foreground">Alertas y monitoreo</h1>
          <p className="text-sm text-muted-foreground mt-1">
            {displayAlerts.length} {displayAlerts.length === 1 ? "alerta" : "alertas"} en tu red
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="h-10 px-3 rounded-lg border border-input bg-white text-sm focus:outline-none focus:ring-2 focus:ring-sembriaia-action"
          >
            {filters.map((f) => <option key={f} value={f}>{f}</option>)}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4 sm:gap-6">
        {/* Feed */}
        <div className="lg:col-span-3 space-y-3">
          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-32 rounded-xl bg-muted animate-pulse" />
              ))}
            </div>
          ) : (
            displayAlerts.map((a) => <AlertCard key={a.id} alert={a} />)
          )}
        </div>

        {/* Right panel */}
        <div className="lg:col-span-2 space-y-4">
          {/* Calendar */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Calendario de monitoreo</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-7 gap-1 mb-3 text-center">
                {days.map((d) => (
                  <div key={d} className="text-xs font-medium text-muted-foreground">{d}</div>
                ))}
                {Array.from({ length: 30 }, (_, i) => i + 1).map((d) => {
                  const hasPass = [3, 8, 13, 18, 23, 28].includes(d);
                  return (
                    <div
                      key={d}
                      className={cn(
                        "aspect-square rounded text-xs flex items-center justify-center",
                        d === 15 ? "bg-sembriaia-primary text-white font-semibold" : "text-foreground",
                        hasPass && d !== 15 ? "relative" : ""
                      )}
                    >
                      {d}
                      {hasPass && d !== 15 && (
                        <span className="absolute bottom-0.5 h-1 w-1 rounded-full bg-sembriaia-action" />
                      )}
                    </div>
                  );
                })}
              </div>
              <p className="text-xs text-muted-foreground">Próxima imagen Sentinel-2: 30 mayo 2026</p>
              <p className="text-[11px] text-muted-foreground/80 mt-1">Sincronizado con 5 fuentes de datos</p>
            </CardContent>
          </Card>

          {/* Frequencies */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Frecuencia de alertas</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {[
                { l: "SMS", d: "Mensajes de texto" },
                { l: "Email", d: "Correo electrónico" },
                { l: "WhatsApp", d: "Mensajería instantánea" },
              ].map((c, i) => (
                <label key={c.l} className="flex items-center justify-between cursor-pointer">
                  <div>
                    <p className="text-sm font-medium">{c.l}</p>
                    <p className="text-xs text-muted-foreground">{c.d}</p>
                  </div>
                  <span className="relative inline-flex h-6 w-11 items-center rounded-full bg-sembriaia-action">
                    <span className="inline-block h-4 w-4 transform rounded-full bg-white translate-x-6" />
                  </span>
                </label>
              ))}
              <div className="pt-3 border-t border-border/40">
                <p className="text-xs font-medium text-muted-foreground mb-2">Frecuencia</p>
                <div className="space-y-1.5">
                  <p className="text-sm">Cada 5 días (Sentinel-2)</p>
                  <p className="text-sm">Inmediato (alertas críticas)</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* History */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Historial</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 max-h-[300px] overflow-y-auto">
              {displayAlerts.slice(0, 6).map((a) => (
                <div key={a.id} className="flex items-center gap-3 text-sm">
                  <span className="text-xs text-muted-foreground w-16 flex-shrink-0">
                    {new Date(a.created_at).toLocaleDateString("es-CO", { day: "2-digit", month: "short" })}
                  </span>
                  <Badge variant={a.is_read ? "secondary" : "destructive"} className="text-[10px]">
                    {a.is_read ? "Leída" : "Nueva"}
                  </Badge>
                  <span className="truncate flex-1">{a.farm_name}</span>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Satellite, CheckCircle2, AlertCircle, TrendingUp, MapPin, Search, Bell, Settings as SettingsIcon, ArrowRight, Sprout } from "lucide-react";
import FarmMap from "@/components/map/FarmMap";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import api from "@/api/axios";
import { useAuthStore } from "@/store/authStore";
import { COLORS } from "@/config";

const stats = [
  { key: "fincas", icon: Satellite, label: "fincas analizadas", value: 0, color: COLORS.water },
  { key: "aptas", icon: CheckCircle2, label: "ha aptas para cultivo", value: "0 ha", color: COLORS.action },
  { key: "alertas", icon: AlertCircle, label: "alertas activas", value: 0, color: COLORS.alert },
  { key: "ingreso", icon: TrendingUp, label: "potencial de ingreso", value: "$0", color: COLORS.urban },
];

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const [farms, setFarms] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [recent, setRecent] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const [farmsRes, alertsRes] = await Promise.all([
          api.get("/farms"),
          api.get("/alerts/unread-count").catch(() => ({ data: { unread: 0 } })),
        ]);
        if (cancelled) return;
        setFarms(farmsRes.data);
        setAlerts([{ id: 1, unread: alertsRes.data.unread }]);
        // Mock recent activity
        setRecent(
          farmsRes.data.slice(0, 5).map((f) => ({
            id: f.id,
            date: new Date(f.created_at).toLocaleDateString("es-CO"),
            farm: f.name,
            type: "Registro de finca",
            status: "Completado",
          }))
        );
      } catch (e) {
        console.error(e);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => { cancelled = true; };
  }, []);

  const totalAptas = farms.reduce((acc, f) => acc + (f.area_ha || 0), 0);
  const dynamicStats = [
    { ...stats[0], value: farms.length },
    stats[1],
    { ...stats[2], value: alerts[0]?.unread || 0 },
    { ...stats[3], value: `$${(totalAptas * 4.2).toFixed(1)}M` },
  ];

  const polygons = farms.map((f, i) => ({
    coordinates: f.geom?.coordinates,
    color: [COLORS.action, COLORS.water, COLORS.warning, COLORS.primary][i % 4],
    properties: f,
  }));

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-foreground">
            Hola, {user?.full_name?.split(" ")[0] || "Productor"}
          </h1>
          {alerts[0]?.unread > 0 ? (
            <p className="text-sm text-sembriaia-alert mt-1">
              Tienes {alerts[0].unread} {alerts[0].unread === 1 ? "alerta pendiente" : "alertas pendientes"}
            </p>
          ) : (
            <p className="text-sm text-muted-foreground mt-1">No tienes alertas pendientes</p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <div className="relative flex-1 sm:flex-initial sm:w-72">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="search"
              placeholder="Buscar finca, análisis..."
              className="w-full h-11 pl-10 pr-3 rounded-lg border border-input bg-white text-sm focus:outline-none focus:ring-2 focus:ring-sembriaia-action"
            />
          </div>
          <button className="h-11 w-11 rounded-lg border border-input bg-white flex items-center justify-center hover:bg-muted relative" aria-label="Notificaciones">
            <Bell className="h-4 w-4" />
            {alerts[0]?.unread > 0 && (
              <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-sembriaia-alert" />
            )}
          </button>
          <Link to="/configuracion" className="h-11 w-11 rounded-lg border border-input bg-white flex items-center justify-center hover:bg-muted" aria-label="Configuración">
            <SettingsIcon className="h-4 w-4" />
          </Link>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {dynamicStats.map((s) => {
          const Icon = s.icon;
          return (
            <Card key={s.key} className="p-4 sm:p-5">
              <div
                className="h-10 w-10 rounded-lg flex items-center justify-center mb-3"
                style={{ backgroundColor: `${s.color}15` }}
              >
                <Icon className="h-5 w-5" style={{ color: s.color }} />
              </div>
              <div className="text-2xl sm:text-3xl font-bold text-foreground mb-1">
                {loading ? "—" : s.value}
              </div>
              <div className="text-xs sm:text-sm text-muted-foreground">{s.label}</div>
            </Card>
          );
        })}
      </div>

      {/* Main grid */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4 sm:gap-6">
        {/* Map */}
        <Card className="lg:col-span-3 overflow-hidden p-0">
          <div className="p-4 sm:p-5 border-b border-border/40 flex items-center justify-between">
            <h2 className="font-semibold text-foreground">Mapa de tus fincas</h2>
            <Link to="/analizar">
              <Button size="sm" variant="ghost">
                Nueva <ArrowRight className="h-3 w-3" />
              </Button>
            </Link>
          </div>
          <div className="h-[400px] sm:h-[500px]">
            {farms.length === 0 && !loading ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-6">
                <MapPin className="h-12 w-12 text-muted-foreground mb-3" />
                <p className="text-sm text-muted-foreground mb-4">Aún no tienes fincas registradas</p>
                <Link to="/analizar"><Button size="sm"><Sprout className="h-4 w-4" />Crear primera finca</Button></Link>
              </div>
            ) : (
              <FarmMap polygons={polygons} height="100%" />
            )}
          </div>
        </Card>

        {/* Recent farms */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Fincas recientes</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {farms.slice(0, 5).map((f) => (
              <Link
                key={f.id}
                to={`/analizar/${f.id}`}
                className="flex items-center gap-3 p-3 rounded-lg hover:bg-muted transition-colors"
              >
                <div className="h-10 w-10 rounded-lg bg-sembriaia-action/10 flex items-center justify-center flex-shrink-0">
                  <Sprout className="h-5 w-5 text-sembriaia-action" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{f.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {f.municipio} · {f.area_ha?.toFixed(1)} ha
                  </p>
                </div>
                <span className="h-2 w-2 rounded-full bg-sembriaia-action" />
              </Link>
            ))}
            {farms.length === 0 && !loading && (
              <p className="text-sm text-muted-foreground text-center py-6">
                No hay fincas registradas
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Actividad reciente</CardTitle>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-muted-foreground border-b border-border/40">
                <th className="pb-3 font-medium">Fecha</th>
                <th className="pb-3 font-medium">Finca</th>
                <th className="pb-3 font-medium">Tipo</th>
                <th className="pb-3 font-medium">Estado</th>
              </tr>
            </thead>
            <tbody>
              {recent.length === 0 && !loading && (
                <tr>
                  <td colSpan={4} className="py-6 text-center text-muted-foreground">
                    Sin actividad reciente
                  </td>
                </tr>
              )}
              {recent.map((r) => (
                <tr key={r.id} className="border-b border-border/30 last:border-0">
                  <td className="py-3">{r.date}</td>
                  <td className="py-3 font-medium">{r.farm}</td>
                  <td className="py-3">{r.type}</td>
                  <td className="py-3">
                    <Badge variant="success">{r.status}</Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}

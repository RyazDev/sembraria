import { useState } from "react";
import { Users, MapPin, Sprout, FileText, Send, Download, Bell, AlertCircle, CheckCircle2, ChevronRight } from "lucide-react";
import FarmMap from "@/components/map/FarmMap";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAuthStore } from "@/store/authStore";
import { COLORS } from "@/config";

const stats = [
  { v: "8", l: "productores", c: COLORS.water },
  { v: "3", l: "fincas monitoreando", c: COLORS.action },
  { v: "124.5 ha", l: "totales", c: COLORS.urban },
  { v: "45.2 ha", l: "aptas", c: COLORS.action, bold: true },
];

const mockProducers = [
  { id: 1, name: "Brayan Cuellar", farm: "La Esperanza", muni: "Florencia", ha: 50, aptas: 15.3, crop: "Cacao", status: "ok" },
  { id: 2, name: "María Trujillo", farm: "El Porvenir", muni: "Belén", ha: 32, aptas: 18.7, crop: "Plátano", status: "warn" },
  { id: 3, name: "José Ramírez", farm: "Buena Vista", muni: "El Doncello", ha: 75, aptas: 22.5, crop: "Yuca", status: "ok" },
  { id: 4, name: "Lucía Pérez", farm: "San Pedro", muni: "Albania", ha: 28, aptas: 8.4, crop: "Cacao", status: "alert" },
  { id: 5, name: "Pedro Gómez", farm: "Las Palmas", muni: "Morelia", ha: 45, aptas: 12.1, crop: "Plátano", status: "ok" },
];

const statusMap = {
  ok: { label: "Estable", color: COLORS.action, dot: "bg-sembriaia-action" },
  warn: { label: "Atención", color: COLORS.warning, dot: "bg-sembriaia-warning" },
  alert: { label: "Crítico", color: COLORS.alert, dot: "bg-sembriaia-alert" },
};

export default function CooperativePage() {
  const user = useAuthStore((s) => s.user);
  const [page, setPage] = useState(1);
  const perPage = 5;
  const total = mockProducers.length;
  const start = (page - 1) * perPage;
  const producers = mockProducers.slice(start, start + perPage);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-foreground">Panel de cooperativa</h1>
          <p className="text-sm text-muted-foreground mt-1">
            {user?.organization || "Cooperativa Multiactiva El Doncello"} · {total} productores
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select className="h-10 px-3 rounded-lg border border-input bg-white text-sm">
            <option>Últimos 30 días</option>
            <option>Último año</option>
            <option>Todo</option>
          </select>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {stats.map((s) => (
          <Card key={s.l} className="p-4 sm:p-5">
            <div className="text-2xl sm:text-3xl font-bold mb-1" style={{ color: s.c }}>
              {s.v}
            </div>
            <div className="text-xs sm:text-sm text-muted-foreground">{s.l}</div>
          </Card>
        ))}
      </div>

      {/* Map */}
      <Card className="overflow-hidden p-0">
        <CardHeader className="border-b border-border/40">
          <CardTitle>Mapa consolidado de fincas</CardTitle>
        </CardHeader>
        <div className="h-[400px]">
          <FarmMap height="100%" zoom={7} />
        </div>
      </Card>

      {/* Table */}
      <Card>
        <CardHeader>
          <CardTitle>Productores</CardTitle>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-muted-foreground border-b border-border/40">
                <th className="pb-3 font-medium">Productor</th>
                <th className="pb-3 font-medium">Finca</th>
                <th className="pb-3 font-medium">Municipio</th>
                <th className="pb-3 font-medium">Hectáreas</th>
                <th className="pb-3 font-medium">Aptas</th>
                <th className="pb-3 font-medium">Cultivo</th>
                <th className="pb-3 font-medium">Estado</th>
                <th className="pb-3 font-medium">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {producers.map((p) => {
                const s = statusMap[p.status];
                return (
                  <tr key={p.id} className="border-b border-border/30 last:border-0 hover:bg-muted/30">
                    <td className="py-3">
                      <div className="flex items-center gap-2">
                        <div className="h-8 w-8 rounded-full bg-sembriaia-action/15 flex items-center justify-center text-xs font-semibold text-sembriaia-action">
                          {p.name.charAt(0)}
                        </div>
                        <span className="font-medium">{p.name}</span>
                      </div>
                    </td>
                    <td className="py-3">{p.farm}</td>
                    <td className="py-3 text-muted-foreground">{p.muni}</td>
                    <td className="py-3">{p.ha}</td>
                    <td className="py-3 text-sembriaia-action font-semibold">{p.aptas}</td>
                    <td className="py-3">
                      <Badge variant="secondary">{p.crop}</Badge>
                    </td>
                    <td className="py-3">
                      <span className="inline-flex items-center gap-1.5 text-xs">
                        <span className={`h-2 w-2 rounded-full ${s.dot}`} />
                        {s.label}
                      </span>
                    </td>
                    <td className="py-3">
                      <a href="#" className="text-sembriaia-water text-xs font-medium hover:underline">
                        Ver análisis
                      </a>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          <div className="flex items-center justify-between mt-4 pt-4 border-t border-border/40">
            <p className="text-xs text-muted-foreground">
              Mostrando {start + 1}-{Math.min(start + perPage, total)} de {total}
            </p>
            <div className="flex gap-1">
              <Button size="sm" variant="outline" disabled={page === 1} onClick={() => setPage(page - 1)}>←</Button>
              <Button size="sm" variant="outline" disabled={start + perPage >= total} onClick={() => setPage(page + 1)}>→</Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Alert summary */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="p-5 border-l-4" style={{ borderLeftColor: COLORS.alert }}>
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="h-4 w-4" style={{ color: COLORS.alert }} />
            <p className="text-sm font-semibold" style={{ color: COLORS.alert }}>2 alertas críticas</p>
          </div>
          <ul className="text-xs text-muted-foreground space-y-1">
            <li>· Finca San Pedro — deforestación</li>
            <li>· Finca Las Palmas — estrés hídrico</li>
          </ul>
        </Card>
        <Card className="p-5 border-l-4" style={{ borderLeftColor: COLORS.warning }}>
          <div className="flex items-center gap-2 mb-2">
            <Bell className="h-4 w-4" style={{ color: COLORS.warning }} />
            <p className="text-sm font-semibold" style={{ color: COLORS.warning }}>1 deforestación cercana</p>
          </div>
          <ul className="text-xs text-muted-foreground space-y-1">
            <li>· Finca El Porvenir</li>
          </ul>
        </Card>
        <Card className="p-5 border-l-4" style={{ borderLeftColor: COLORS.action }}>
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle2 className="h-4 w-4" style={{ color: COLORS.action }} />
            <p className="text-sm font-semibold" style={{ color: COLORS.action }}>5 fincas estables</p>
          </div>
          <p className="text-xs text-muted-foreground">Sin alertas en los últimos 30 días</p>
        </Card>
      </div>

      {/* Bulk actions */}
      <Card>
        <CardHeader>
          <CardTitle>Acciones masivas</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col sm:flex-row gap-3">
          <Button variant="primary" className="flex-1"><FileText className="h-4 w-4" />Reporte consolidado</Button>
          <Button variant="destructive" className="flex-1"><Send className="h-4 w-4" />Alerta masiva</Button>
          <Button variant="outline" className="flex-1"><Download className="h-4 w-4" />Exportar datos</Button>
        </CardContent>
      </Card>
    </div>
  );
}

import { useState } from "react";
import { User, MapPin, Bell, CreditCard, Shield, Save, Trash2, Plus, Sprout } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuthStore } from "@/store/authStore";
import { cn } from "@/lib/utils";

const tabs = [
  { id: "perfil", label: "Perfil", icon: User },
  { id: "fincas", label: "Fincas", icon: MapPin },
  { id: "alertas", label: "Alertas", icon: Bell },
  { id: "facturacion", label: "Facturación", icon: CreditCard },
  { id: "seguridad", label: "Seguridad", icon: Shield },
];

const roles = [
  { id: "productor", label: "Productor" },
  { id: "cooperativa", label: "Cooperativa" },
  { id: "extensionista", label: "Extensionista" },
  { id: "gobierno", label: "Entidad gubernamental" },
];

function Toggle({ checked, onChange, label, desc }) {
  return (
    <label className="flex items-center justify-between cursor-pointer py-2">
      <div>
        <p className="text-sm font-medium">{label}</p>
        {desc && <p className="text-xs text-muted-foreground">{desc}</p>}
      </div>
      <button
        type="button"
        onClick={() => onChange(!checked)}
        className={cn(
          "relative inline-flex h-6 w-11 items-center rounded-full transition-colors",
          checked ? "bg-sembriaia-action" : "bg-muted"
        )}
      >
        <span
          className={cn(
            "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
            checked ? "translate-x-6" : "translate-x-1"
          )}
        />
      </button>
    </label>
  );
}

export default function SettingsPage() {
  const user = useAuthStore((s) => s.user);
  const [tab, setTab] = useState("perfil");
  const [profile, setProfile] = useState({
    full_name: user?.full_name || "",
    email: user?.email || "",
    phone: user?.phone || "",
    organization: user?.organization || "",
    role: user?.role || "productor",
  });
  const [channels, setChannels] = useState({
    sms: true,
    email: true,
    whatsapp: false,
  });
  const [types, setTypes] = useState({
    hidrico: true,
    deforestacion: true,
    precios: true,
    clima: true,
    ok: false,
  });

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl">
      <h1 className="text-2xl sm:text-3xl font-bold text-foreground">Configuración de cuenta</h1>

      {/* Tabs */}
      <div className="border-b border-border overflow-x-auto">
        <div className="flex gap-1 min-w-max">
          {tabs.map((t) => {
            const Icon = t.icon;
            const active = tab === t.id;
            return (
              <button
                key={t.id}
                onClick={() => setTab(t.id)}
                className={cn(
                  "flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors",
                  active
                    ? "border-sembriaia-action text-foreground"
                    : "border-transparent text-muted-foreground hover:text-foreground"
                )}
              >
                <Icon className="h-4 w-4" />
                {t.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Perfil */}
      {tab === "perfil" && (
        <Card>
          <CardHeader>
            <CardTitle>Perfil</CardTitle>
          </CardHeader>
          <CardContent className="space-y-5">
            <div className="flex items-center gap-4">
              <div className="h-20 w-20 rounded-full bg-sembriaia-primary text-white text-2xl font-semibold flex items-center justify-center">
                {(profile.full_name || "U").charAt(0).toUpperCase()}
              </div>
              <div>
                <button className="text-sm text-sembriaia-water font-medium hover:underline">
                  Cambiar foto
                </button>
                <p className="text-xs text-muted-foreground mt-1">JPG o PNG. Máx 2MB.</p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="full_name" className="mb-1.5 block">Nombre completo</Label>
                <Input
                  id="full_name"
                  value={profile.full_name}
                  onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="email" className="mb-1.5 block">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={profile.email}
                  onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="phone" className="mb-1.5 block">Teléfono</Label>
                <Input
                  id="phone"
                  placeholder="+57 3XX XXXXXXX"
                  value={profile.phone}
                  onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="organization" className="mb-1.5 block">Organización</Label>
                <Input
                  id="organization"
                  value={profile.organization}
                  onChange={(e) => setProfile({ ...profile, organization: e.target.value })}
                />
              </div>
              <div className="sm:col-span-2">
                <Label className="mb-1.5 block">Rol</Label>
                <select
                  value={profile.role}
                  onChange={(e) => setProfile({ ...profile, role: e.target.value })}
                  className="w-full h-12 px-3 rounded-lg border border-input bg-white text-sm"
                >
                  {roles.map((r) => (
                    <option key={r.id} value={r.id}>{r.label}</option>
                  ))}
                </select>
              </div>
            </div>
            <Button><Save className="h-4 w-4" />Guardar cambios</Button>
          </CardContent>
        </Card>
      )}

      {/* Fincas */}
      {tab === "fincas" && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Mis fincas</CardTitle>
            <Button size="sm"><Plus className="h-4 w-4" />Agregar finca</Button>
          </CardHeader>
          <CardContent className="space-y-2">
            {[
              { id: 1, name: "Finca La Esperanza", muni: "Florencia", ha: 50, crop: "Cacao" },
              { id: 2, name: "Finca El Porvenir", muni: "Belén de los Andaquíes", ha: 32, crop: "Plátano" },
            ].map((f) => (
              <div key={f.id} className="flex items-center gap-3 p-3 rounded-lg border border-border/40">
                <div className="h-10 w-10 rounded-lg bg-sembriaia-action/10 flex items-center justify-center flex-shrink-0">
                  <Sprout className="h-5 w-5 text-sembriaia-action" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{f.name}</p>
                  <p className="text-xs text-muted-foreground">{f.muni} · {f.ha} ha · {f.crop}</p>
                </div>
                <button className="p-2 hover:bg-muted rounded text-sembriaia-alert" aria-label="Eliminar">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Alertas */}
      {tab === "alertas" && (
        <Card>
          <CardHeader>
            <CardTitle>Notificaciones</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1">
            <Toggle
              checked={channels.sms}
              onChange={(v) => setChannels({ ...channels, sms: v })}
              label="SMS"
              desc="Mensajes de texto a tu teléfono +57"
            />
            <Toggle
              checked={channels.email}
              onChange={(v) => setChannels({ ...channels, email: v })}
              label="Email"
              desc="Correo electrónico"
            />
            <Toggle
              checked={channels.whatsapp}
              onChange={(v) => setChannels({ ...channels, whatsapp: v })}
              label="WhatsApp"
              desc="Mensajería instantánea"
            />

            <div className="pt-4 mt-4 border-t border-border/40">
              <p className="text-sm font-semibold mb-3">Tipos de alerta</p>
              <Toggle
                checked={types.hidrico}
                onChange={(v) => setTypes({ ...types, hidrico: v })}
                label="Estrés hídrico"
              />
              <Toggle
                checked={types.deforestacion}
                onChange={(v) => setTypes({ ...types, deforestacion: v })}
                label="Deforestación"
              />
              <Toggle
                checked={types.precios}
                onChange={(v) => setTypes({ ...types, precios: v })}
                label="Precios de mercado"
              />
              <Toggle
                checked={types.clima}
                onChange={(v) => setTypes({ ...types, clima: v })}
                label="Pronóstico climático"
              />
              <Toggle
                checked={types.ok}
                onChange={(v) => setTypes({ ...types, ok: v })}
                label="Reportes de estado normal"
              />
            </div>

            <Button className="mt-6"><Save className="h-4 w-4" />Guardar preferencias</Button>
          </CardContent>
        </Card>
      )}

      {/* Facturación */}
      {tab === "facturacion" && (
        <Card>
          <CardHeader>
            <CardTitle>Plan y facturación</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="border-2 border-sembriaia-action rounded-xl p-5 mb-4">
              <Badge variant="success">Plan actual</Badge>
              <h3 className="text-lg font-semibold mt-2">Productor (Gratis)</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Análisis ilimitados · 5 fincas · Reportes PDF · Alertas SMS
              </p>
            </div>
            <p className="text-sm text-muted-foreground">
              SembrarIA es gratuito para productores de Caquetá. Patrocinado por Universidad de la Amazonía.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Seguridad */}
      {tab === "seguridad" && (
        <Card>
          <CardHeader>
            <CardTitle>Seguridad</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="current" className="mb-1.5 block">Contraseña actual</Label>
              <Input id="current" type="password" />
            </div>
            <div>
              <Label htmlFor="new" className="mb-1.5 block">Nueva contraseña</Label>
              <Input id="new" type="password" />
            </div>
            <div>
              <Label htmlFor="confirm" className="mb-1.5 block">Confirmar nueva contraseña</Label>
              <Input id="confirm" type="password" />
            </div>
            <Button><Save className="h-4 w-4" />Cambiar contraseña</Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

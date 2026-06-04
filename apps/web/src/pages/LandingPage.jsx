import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import {
  Sprout, Satellite, MapPin, Leaf, ShieldCheck, ArrowRight,
  TreeDeciduous, Truck, Mail, Phone, MapPinned
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/store/authStore";
import { COLORS } from "@/config";

const stats = [
  { value: "97%", label: "del suelo es pasto para ganadería extensiva", icon: Truck, color: COLORS.pasture, valueColor: COLORS.alert },
  { value: "25,263 ha", label: "de bosque convertidas a pasto en 2024", icon: TreeDeciduous, color: COLORS.primary, valueColor: COLORS.alert },
  { value: "400 km", label: "de distancia promedio para traer alimentos", icon: Truck, color: COLORS.water, valueColor: COLORS.urban },
];

const steps = [
  { n: "01", title: "Dibuja tu finca en el mapa", desc: "O usa tu ubicación GPS. No necesitas saber de satélites.", icon: MapPin, color: COLORS.primary },
  { n: "02", title: "Elige cacao, plátano o yuca", desc: "Nuestro modelo evalúa tu finca según el cultivo.", icon: Leaf, color: COLORS.action },
  { n: "03", title: "Recibe tu mapa de oportunidad", desc: "Saber exactamente dónde sembrar, con qué pendiente y por qué.", icon: Satellite, color: COLORS.water },
];

const sources = ["Sentinel-2", "Sentinel-1", "ERA5", "MODIS", "SRTM"];

export default function LandingPage() {
  const navigate = useNavigate();
  const isAuth = useAuthStore((s) => s.isAuthenticated);
  return (
    <>
      {/* HERO */}
      <section className="relative min-h-[700px] flex items-center overflow-hidden">
        <div
          className="absolute inset-0"
          style={{
            backgroundImage:
              "linear-gradient(to right, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.5) 50%, rgba(0,0,0,0.3) 100%), url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=2000&q=80')",
            backgroundSize: "cover",
            backgroundPosition: "center",
          }}
        />
        <div className="container-app relative z-10 py-20">
          <div className="max-w-[600px] text-white">
            <span className="inline-block bg-white/15 backdrop-blur rounded-full px-4 py-1.5 text-xs font-medium tracking-wide mb-6">
              CopernicusLAC Hackathon 2026 · Universidad de la Amazonía
            </span>
            <h1 className="text-4xl sm:text-5xl lg:text-[56px] font-bold leading-[1.1] mb-4">
              Convierte tu pasto en alimento
            </h1>
            <p className="text-lg sm:text-xl text-white/85 leading-relaxed max-w-[520px] mb-8">
              Datos satelitales de la Unión Europea para identificar qué hectáreas de tu finca en
              Caquetá pueden producir cacao, plátano o yuca.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 mb-6">
              <Button size="xl" className="w-full sm:w-auto" onClick={() => navigate(isAuth ? "/analizar" : "/register")}>
                Analizar mi finca gratis <ArrowRight className="h-5 w-5" />
              </Button>
              <Button size="xl" variant="secondary" className="w-full sm:w-auto" onClick={() => navigate("/mapa-regional")}>
                Ver demo del mapa
              </Button>
            </div>
            <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-white/70">
              <span>✓ Sin costo para productores</span>
              <span>✓ Basado en Sentinel-2 + IA</span>
              <span>✓ Validado por UDLA</span>
            </div>
          </div>
        </div>
      </section>

      {/* PROBLEM */}
      <section className="bg-background py-20 sm:py-24">
        <div className="container-app">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-foreground mb-3">La realidad de Caquetá</h2>
            <p className="text-lg text-muted-foreground">
              97% del suelo es pasto. 25,263 hectáreas de bosque perdidas en 2024. La comida viene de
              400 km.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {stats.map((s, i) => {
              const Icon = s.icon;
              return (
                <div key={i} className="bg-white rounded-2xl border border-border/40 p-8 text-center">
                  <div
                    className="mx-auto h-16 w-16 rounded-full flex items-center justify-center mb-4"
                    style={{ backgroundColor: `${s.color}22` }}
                  >
                    <Icon className="h-8 w-8" style={{ color: s.color }} />
                  </div>
                  <div className="text-4xl sm:text-5xl font-bold mb-2" style={{ color: s.valueColor }}>
                    {s.value}
                  </div>
                  <p className="text-sm text-muted-foreground">{s.label}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="bg-white py-20 sm:py-24">
        <div className="container-app">
          <div className="max-w-3xl mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-foreground mb-3">
              ¿Cómo funciona SembrarIA?
            </h2>
            <p className="text-lg text-muted-foreground">
              Tres pasos basados en inteligencia artificial y datos Copernicus
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
            <div className="hidden md:block absolute top-12 left-[16%] right-[16%] h-0.5 bg-border -z-0" />
            {steps.map((s) => {
              const Icon = s.icon;
              return (
                <div key={s.n} className="relative bg-white">
                  <div className="text-6xl lg:text-7xl font-bold text-border mb-2">{s.n}</div>
                  <Icon className="h-12 w-12 mb-3" style={{ color: s.color }} />
                  <h3 className="text-lg sm:text-xl font-semibold text-foreground mb-2">{s.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{s.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* DATA SOURCES */}
      <section className="bg-sembriaia-primary py-16 sm:py-20 text-white">
        <div className="container-app text-center">
          <h2 className="text-2xl sm:text-3xl font-bold mb-10">5 fuentes de datos satelitales</h2>
          <div className="flex flex-wrap justify-center items-center gap-8 sm:gap-12">
            {sources.map((s) => (
              <div key={s} className="flex flex-col items-center gap-2">
                <Satellite className="h-10 w-10 text-white/80" />
                <span className="text-sm font-medium text-white/80">{s}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA BANNER */}
      <section className="bg-sembriaia-action py-14 sm:py-16 text-white">
        <div className="container-app flex flex-col lg:flex-row items-center justify-between gap-6">
          <h2 className="text-2xl sm:text-3xl font-bold text-center lg:text-left">
            ¿Listo para reconverter tu finca?
          </h2>
          <Button
            size="xl"
            className="bg-white text-sembriaia-action hover:bg-white/90 w-full sm:w-auto"
            onClick={() => navigate(isAuth ? "/analizar" : "/register")}
          >
            Comenzar análisis gratuito <ArrowRight className="h-5 w-5" />
          </Button>
        </div>
      </section>
    </>
  );
}

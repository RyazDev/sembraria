/**
 * ====================================================================
 * SembrarIA — Sistema de Diseño (Foundation)
 * ====================================================================
 * REGLAS:
 *  1. SOLO verde oscuro + verde claro + neutros. NUNCA rojo/azul/amarillo
 *     para diferenciar. Si necesitas "negativo" o "alerta", usa opacidad
 *     sobre el verde oscuro.
 *  2. Verde oscuro (#1B5E20) = color principal, identidad, autoridad.
 *  3. Verde claro (#00C853) = color de ACCIÓN, CTA, énfasis positivo.
 *  4. Para diferenciar estados: combina verde oscuro + opacidad (5%, 10%,
 *     15%, 20%) para fondos suaves, o verde claro con saturación.
 *  5. El marrón "pasto" (#D4A574) está PERMITIDO SOLO en el mapa
 *     (leyenda visual) porque representa la realidad geográfica.
 * ====================================================================
 */

export const COLORS = {
  // === Verde oscuro (PRIMARY) — Identidad, autoridad, títulos ===
  primary: "#1B5E20",        // #1B5E20 — primary base
  primaryDark: "#0E3F13",    // #0E3F13 — hover/active
  primaryLight: "#2E7D32",   // #2E7D32 — variante media
  primaryLighter: "#4CAF50", // #4CAF50 — variante clara

  // === Verde claro (ACTION) — CTAs, énfasis positivo, acentos ===
  action: "#00C853",         // #00C853 — acción/CTA
  actionDark: "#00A040",     // #00A040 — hover/active
  actionLight: "#5EE079",    // #5EE079 — hover suave

  // === Neutros — texto, fondos, bordes ===
  background: "#FAFAFA",    // gris muy claro
  surface: "#FFFFFF",       // blanco puro
  surfaceAlt: "#F4F6F4",    // verde-gris muy claro (background sutil)
  border: "#E0E0E0",        // borde neutro
  borderStrong: "#BDBDBD",  // borde más fuerte
  text: "#1A1A1A",          // texto principal
  textSecondary: "#525252", // texto secundario
  textMuted: "#8A8A8A",     // texto deshabilitado
  textOnPrimary: "#FFFFFF", // texto sobre primary
  textOnAction: "#FFFFFF",  // texto sobre action

  // === Solo para el mapa (representa realidad geográfica) ===
  map: {
    pasture: "#D4A574",     // marrón pasto — SOLO en el mapa
    water: "#5BA8D6",       // azul agua — SOLO en el mapa
    forest: "#1B5E20",      // verde bosque = primary
    urban: "#8B7355",       // marrón urbano — SOLO en el mapa
    opportunity: "#00C853", // verde oportunidad = action
  },

  // === Estados SEMÁNTICOS (todos basados en verde oscuro/claro) ===
  // En vez de rojo para "error", usamos verde oscuro con opacidad.
  // En vez de amarillo para "warning", usamos verde medio.
  state: {
    success: "#00C853",      // verde acción
    successBg: "#E6F9EE",    // fondo verde claro
    info: "#2E7D32",         // verde primary-light
    infoBg: "#EDF5EE",       // fondo verde medio
    warn: "#4CAF50",         // verde medio (en vez de naranja)
    warnBg: "#F1F8E9",       // fondo verde muy claro
    error: "#0E3F13",        // verde muy oscuro (en vez de rojo)
    errorBg: "#E8EDE8",      // fondo gris verdoso
  },
};

export const CROPS = {
  cacao: { id: "cacao", label: "Cacao", icon: "🌱", tone: "primary" },
  platano: { id: "platano", label: "Plátano", icon: "🌿", tone: "action" },
  yuca: { id: "yuca", label: "Yuca", icon: "🌾", tone: "primaryLight" },
};

export const config = {
  apiUrl: import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1",
  appName: import.meta.env.VITE_APP_NAME || "SembrarIA",
  map: {
    tilesUrl:
      import.meta.env.VITE_MAP_TILES_URL ||
      "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
    defaultCenter: [
      parseFloat(import.meta.env.VITE_DEFAULT_CENTER_LNG) || -75.6063,
      parseFloat(import.meta.env.VITE_DEFAULT_CENTER_LAT) || 1.6144,
    ],
    defaultZoom: parseInt(import.meta.env.VITE_DEFAULT_ZOOM) || 8,
    caquetaBbox: (import.meta.env.VITE_CAQUETA_BBOX || "-76.3,-0.7,-73.6,2.3")
      .split(",")
      .map(parseFloat),
  },
};

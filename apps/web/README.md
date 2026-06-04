# apps/web — Frontend React

SPA de SembrarIA: 13 pantallas responsive (393 / 768 / 1440 px), mapas interactivos, integración con el backend FastAPI.

## Stack

- **React 18** + **Vite 5** — Build ultrarrápido
- **React Router 6** — Routing con layouts anidados
- **Tailwind CSS 3** — Utility-first con CSS vars de marca
- **MapLibre GL** — Mapas vectoriales (sin token, sin coste)
- **Zustand** — State global (auth) con persistencia en localStorage
- **Axios** — Cliente HTTP con interceptor JWT
- **shadcn-style components** — UI accesibles (Card, Button, Input, Badge, Label)
- **Lucide React** — Iconos SVG tree-shakeable

## Estructura

```
apps/web/
├── public/                 # Assets estáticos (favicon, etc)
├── src/
│   ├── main.jsx            # Entry: renderiza <App />
│   ├── App.jsx             # Router con public/private + layouts
│   ├── config.js           # Lee VITE_* + constantes de marca
│   ├── api/
│   │   └── axios.js        # Cliente con JWT + 401 handler
│   ├── store/
│   │   └── authStore.js    # Zustand: user, token, login, register, logout
│   ├── components/
│   │   ├── ui/             # Primitivos (Card, Button, Input, Badge, Label)
│   │   ├── layout/         # AppLayout (sidebar) + PublicLayout (top nav)
│   │   └── map/
│   │       └── FarmMap.jsx # MapLibre con polígonos
│   ├── pages/              # 13 pantallas
│   │   ├── LandingPage.jsx
│   │   ├── LoginPage.jsx
│   │   ├── RegisterPage.jsx
│   │   ├── DashboardPage.jsx
│   │   ├── FarmAnalysisPage.jsx
│   │   ├── ResultsPage.jsx
│   │   ├── AlertsPage.jsx
│   │   ├── ReportsPage.jsx
│   │   ├── PricesPage.jsx
│   │   ├── RegionalMapPage.jsx
│   │   ├── CooperativePage.jsx
│   │   ├── SettingsPage.jsx
│   │   ├── MethodologyPage.jsx
│   │   └── NotFoundPage.jsx
│   ├── lib/
│   │   └── utils.js        # cn() para Tailwind class merging
│   └── styles/
│       └── index.css       # Tailwind + SembrarIA brand vars
├── components.json         # shadcn config
├── index.html
├── package.json
├── postcss.config.js
├── tailwind.config.js
├── vite.config.js          # Alias @/ -> src/
└── .env.example
```

## Desarrollo

```bash
# 1. Setup
bash scripts/setup/setup-frontend.sh    # npm install

# 2. Iniciar
bash scripts/dev/start-frontend.sh      # vite en :5173

# 3. Build producción
cd apps/web && npm run build

# 4. Lint
cd apps/web && npm run lint
```

## Aliases

Vite config define `@/` como alias a `src/`:

```js
import FarmMap from "@/components/map/FarmMap";   // en vez de ../../components/map/FarmMap
import api from "@/api/axios";
```

## Convenciones de código

- **Naming**: PascalCase para componentes (`FarmMap.jsx`), camelCase para utils (`utils.js`)
- **Mobile-first**: breakpoints `sm:` 640 / `md:` 768 / `lg:` 1024 / `xl:` 1280
- **Colores de marca**: usar las vars de Tailwind (`bg-sembriaia-action`, `text-sembriaia-primary`, etc)
- **Sin emojis** salvo que el usuario lo pida
- **Sin comentarios** salvo que el usuario lo pida

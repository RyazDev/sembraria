import { Routes, Route, Navigate } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";

import LandingPage from "@/pages/LandingPage";
import LoginPage from "@/pages/LoginPage";
import RegisterPage from "@/pages/RegisterPage";
import DashboardPage from "@/pages/DashboardPage";
import FarmAnalysisPage from "@/pages/FarmAnalysisPage";
import ResultsPage from "@/pages/ResultsPage";
import AlertsPage from "@/pages/AlertsPage";
import ReportsPage from "@/pages/ReportsPage";
import PricesPage from "@/pages/PricesPage";
import RegionalMapPage from "@/pages/RegionalMapPage";
import CooperativePage from "@/pages/CooperativePage";
import SettingsPage from "@/pages/SettingsPage";
import MethodologyPage from "@/pages/MethodologyPage";
import NotFoundPage from "@/pages/NotFoundPage";

import AppLayout from "@/components/layout/AppLayout";
import PublicLayout from "@/components/layout/PublicLayout";

function PrivateRoute({ children }) {
  const isAuth = useAuthStore((s) => s.isAuthenticated);
  return isAuth ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route element={<PublicLayout />}>
        <Route path="/" element={<LandingPage />} />
        <Route path="/mapa-regional" element={<RegionalMapPage />} />
        <Route path="/metodologia" element={<MethodologyPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>

      {/* Private routes (auth required) */}
      <Route element={<PrivateRoute><AppLayout /></PrivateRoute>}>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/analizar" element={<FarmAnalysisPage />} />
        <Route path="/analizar/:farmId" element={<FarmAnalysisPage />} />
        <Route path="/resultados/:analysisId" element={<ResultsPage />} />
        <Route path="/alertas" element={<AlertsPage />} />
        <Route path="/reportes" element={<ReportsPage />} />
        <Route path="/precios" element={<PricesPage />} />
        <Route path="/cooperativa" element={<CooperativePage />} />
        <Route path="/configuracion" element={<SettingsPage />} />
      </Route>

      {/* 404 */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}

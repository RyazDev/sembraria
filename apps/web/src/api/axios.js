import axios from "axios";
import { config } from "@/config";

const api = axios.create({
  baseURL: config.apiUrl,
  timeout: 130000, // 130s para analisis sincrono
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor: agregar JWT a cada request
api.interceptors.request.use((cfg) => {
  const token = localStorage.getItem("sembriaia_token");
  if (token) {
    cfg.headers.Authorization = `Bearer ${token}`;
  }
  return cfg;
});

// Interceptor: manejo de errores 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("sembriaia_token");
      localStorage.removeItem("sembriaia_user");
      // Redirigir a login si no estamos ya
      if (!window.location.pathname.includes("/login")) {
        window.location.href = "/login";
      }
    }
    return Promise.reject(err);
  }
);

export default api;

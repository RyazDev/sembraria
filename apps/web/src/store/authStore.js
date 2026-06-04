import { create } from "zustand";
import { persist } from "zustand/middleware";
import api from "@/api/axios";

export const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: async (email, password) => {
        const res = await api.post("/auth/login", { email, password });
        const { access_token, user } = res.data;
        localStorage.setItem("sembriaia_token", access_token);
        localStorage.setItem("sembriaia_user", JSON.stringify(user));
        set({ user, token: access_token, isAuthenticated: true });
        return user;
      },

      register: async (payload) => {
        const res = await api.post("/auth/register", payload);
        const { access_token, user } = res.data;
        localStorage.setItem("sembriaia_token", access_token);
        localStorage.setItem("sembriaia_user", JSON.stringify(user));
        set({ user, token: access_token, isAuthenticated: true });
        return user;
      },

      logout: () => {
        localStorage.removeItem("sembriaia_token");
        localStorage.removeItem("sembriaia_user");
        set({ user: null, token: null, isAuthenticated: false });
      },

      fetchMe: async () => {
        const res = await api.get("/auth/me");
        set({ user: res.data });
        return res.data;
      },
    }),
    {
      name: "sembriaia-auth",
      partialize: (state) => ({ user: state.user, token: state.token, isAuthenticated: state.isAuthenticated }),
    }
  )
);

import { create } from "zustand";
import { persist } from "zustand/middleware";
import api from "../lib/api";
import {
  type User,
  type LoginCredentials,
  type RegisterCredentials,
  type AuthResponse,
  type ApiError,
} from "../types/auth";

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface AuthActions {
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<void>;
  logout: () => void;
  clearError: () => void;
  checkAuth: () => Promise<void>;
}

type AuthStore = AuthState & AuthActions;

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // State
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      login: async (credentials: LoginCredentials) => {
        set({ isLoading: true, error: null });

        try {
          const response = await api.post<AuthResponse>(
            "/auth/login",
            credentials
          );
          const { user, accessToken, refreshToken } = response.data;

          // Store tokens
          localStorage.setItem("accessToken", accessToken);
          if (refreshToken) {
            localStorage.setItem("refreshToken", refreshToken);
          }

          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          const apiError = error.response?.data as ApiError;
          set({
            isLoading: false,
            error: apiError?.error?.message || "Login failed",
          });
          throw error;
        }
      },

      register: async (credentials: RegisterCredentials) => {
        set({ isLoading: true, error: null });

        try {
          const response = await api.post<AuthResponse>(
            "/auth/register",
            credentials
          );
          const { user, accessToken, refreshToken } = response.data;

          // Store tokens
          localStorage.setItem("accessToken", accessToken);
          if (refreshToken) {
            localStorage.setItem("refreshToken", refreshToken);
          }

          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          const apiError = error.response?.data as ApiError;
          set({
            isLoading: false,
            error: apiError?.error?.message || "Registration failed",
          });
          throw error;
        }
      },

      logout: () => {
        const refreshToken = localStorage.getItem("refreshToken");

        // Call logout endpoint if refresh token exists
        if (refreshToken) {
          api.post("/auth/logout", { refreshToken }).catch(() => {
            // Ignore errors, just clean up locally
          });
        }

        // Clear tokens and state
        localStorage.removeItem("accessToken");
        localStorage.removeItem("refreshToken");

        set({
          user: null,
          isAuthenticated: false,
          error: null,
        });
      },

      clearError: () => {
        set({ error: null });
      },

      checkAuth: async () => {
        const token = localStorage.getItem("accessToken");

        if (!token) {
          set({ isAuthenticated: false, user: null });
          return;
        }

        try {
          set({ isLoading: true });
          const response = await api.get<User>("/users/me");

          set({
            user: response.data,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          // Token is invalid, clear auth state
          localStorage.removeItem("accessToken");
          localStorage.removeItem("refreshToken");

          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

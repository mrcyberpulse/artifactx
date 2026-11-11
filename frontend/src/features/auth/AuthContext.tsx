import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";

import { ApiError, api } from "@/lib/api-client";
import { getAccessToken, setAccessToken, subscribeAccessToken } from "@/lib/token-store";
import type { User } from "@/types/api";

interface TokenResponse {
  access_token: string;
  expires_in: number;
  user: User;
}

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, fullName: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [, forceRender] = useState(0);

  useEffect(() => subscribeAccessToken(() => forceRender((n) => n + 1)), []);

  useEffect(() => {
    // On full page load there is no in-memory access token yet. Attempt a silent refresh
    // using the HttpOnly cookie before deciding the user is logged out.
    let cancelled = false;
    (async () => {
      try {
        const res = await api.post<TokenResponse>("/auth/refresh", {}, { skipAuthRetry: true });
        if (cancelled) return;
        setAccessToken(res.access_token);
        setUser(res.user);
      } catch {
        if (!cancelled) setUser(null);
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const res = await api.post<TokenResponse>("/auth/login", { email, password }, { skipAuthRetry: true });
    setAccessToken(res.access_token);
    setUser(res.user);
  }, []);

  const register = useCallback(async (email: string, fullName: string, password: string) => {
    const res = await api.post<TokenResponse>(
      "/auth/register",
      { email, full_name: fullName, password },
      { skipAuthRetry: true },
    );
    setAccessToken(res.access_token);
    setUser(res.user);
  }, []);

  const logout = useCallback(async () => {
    try {
      await api.post("/auth/logout", {}, { skipAuthRetry: true });
    } catch (err) {
      // Even if the server call fails, clear local state so the UI reflects logged-out.
      if (!(err instanceof ApiError)) throw err;
    } finally {
      setAccessToken(null);
      setUser(null);
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, isLoading, isAuthenticated: Boolean(user && getAccessToken()), login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider.");
  return ctx;
}

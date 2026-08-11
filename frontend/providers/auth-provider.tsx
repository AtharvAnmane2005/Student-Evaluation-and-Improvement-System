"use client";

import axios from "axios";
import { createContext, useCallback, useContext, useEffect, useState } from "react";

import { apiClient } from "@/lib/api-client";
import { setAccessToken } from "@/lib/token-store";
import type { AuthUser } from "@/types/auth";

interface AuthContextValue {
  user: AuthUser | null;
  isLoading: boolean;
  /** Called right after login/register/Google sign-in to populate the context immediately,
   *  without waiting on a redundant /auth/me round-trip. */
  setUser: (user: AuthUser | null) => void;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

/**
 * Access tokens live in memory only (see lib/token-store.ts) and are wiped
 * on every hard reload. This provider re-establishes the session once, on
 * mount, by silently hitting /auth/refresh (which relies on the httpOnly
 * cookie the browser already has) and then /auth/me. If either fails, the
 * user is simply treated as logged out — page-level guards handle the
 * redirect to /login, this provider only owns "who is logged in right now".
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      try {
        const { data } = await axios.post<{ access_token: string }>("/api/backend/auth/refresh", null, {
          withCredentials: true,
        });
        setAccessToken(data.access_token);
        const me = await apiClient.get<AuthUser>("/auth/me");
        if (!cancelled) setUser(me.data);
      } catch {
        setAccessToken(null);
        if (!cancelled) setUser(null);
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    bootstrap();
    return () => {
      cancelled = true;
    };
  }, []);

  const logout = useCallback(async () => {
    try {
      await apiClient.post("/auth/logout");
    } catch {
      // Best-effort — the cookie may already be gone. Client state is
      // cleared below regardless.
    }
    setAccessToken(null);
    setUser(null);
    document.cookie = "placer_role=; path=/; max-age=0; SameSite=Strict";
  }, []);

  return <AuthContext.Provider value={{ user, isLoading, setUser, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider.");
  }
  return ctx;
}

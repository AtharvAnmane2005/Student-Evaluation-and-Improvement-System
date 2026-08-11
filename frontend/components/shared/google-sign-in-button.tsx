"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef } from "react";

import { apiClient } from "@/lib/api-client";
import { setAccessToken } from "@/lib/token-store";
import { useAuth } from "@/providers/auth-provider";
import type { LoginResponse, UserRole } from "@/types/auth";

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: Record<string, unknown>) => void;
          renderButton: (parent: HTMLElement, options: Record<string, unknown>) => void;
        };
      };
    };
  }
}

interface GoogleSignInButtonProps {
  /** Only used if this Google sign-in creates a brand-new account. */
  role?: Extract<UserRole, "student" | "tpo">;
}

/**
 * Renders Google's own "Sign in with Google" button. On success, sends the
 * ID token to POST /auth/google, which either logs in an existing account
 * or creates a new one — same response shape as the password login flow,
 * so the redirect logic below matches app/(auth)/login/page.tsx exactly.
 */
export function GoogleSignInButton({ role = "student" }: GoogleSignInButtonProps) {
  const buttonRef = useRef<HTMLDivElement>(null);
  const router = useRouter();
  const { setUser } = useAuth();
  const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;

  useEffect(() => {
    if (!clientId) return;

    async function handleCredentialResponse(googleResponse: { credential: string }) {
      try {
        const { data } = await apiClient.post<LoginResponse>("/auth/google", {
          credential: googleResponse.credential,
          role,
        });
        setAccessToken(data.access_token);
        setUser(data.user);
        document.cookie = `placer_role=${data.user.role}; path=/; SameSite=Strict`;

        const roleHome =
          data.user.role === "admin" ? "/admin/dashboard" : data.user.role === "tpo" ? "/tpo/dashboard" : "/dashboard";
        router.push(data.profile_incomplete ? `${roleHome}?complete_profile=true` : roleHome);
      } catch {
        // Google's button has no built-in error slot. A toast/notification
        // system isn't built yet (see Notifications module, later phase) —
        // for now the user simply stays on the page and can retry.
      }
    }

    function initialize() {
      if (!window.google || !buttonRef.current) return;
      window.google.accounts.id.initialize({ client_id: clientId, callback: handleCredentialResponse });
      window.google.accounts.id.renderButton(buttonRef.current, {
        theme: "outline",
        size: "large",
        width: 360,
      });
    }

    if (window.google) {
      initialize();
      return;
    }

    const script = document.createElement("script");
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.defer = true;
    script.onload = initialize;
    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clientId, role]);

  if (!clientId) {
    // Fails silently in the UI rather than rendering a broken button —
    // logged once so it's not a mystery in dev.
    if (process.env.NODE_ENV === "development") {
      console.warn("NEXT_PUBLIC_GOOGLE_CLIENT_ID is not set — Google Sign-In button hidden.");
    }
    return null;
  }

  return <div ref={buttonRef} className="flex justify-center" />;
}

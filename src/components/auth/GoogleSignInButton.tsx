"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/authStore";
import { authService } from "@/services/authService";
import { Loader2 } from "lucide-react";

interface GoogleSignInButtonProps {
  label?: string;
  redirectTo?: string;
  className?: string;
}

declare global {
  interface Window {
    google?: any;
  }
}

export const GoogleSignInButton: React.FC<GoogleSignInButtonProps> = ({
  label = "Continue with Google",
  redirectTo,
  className = "",
}) => {
  const router = useRouter();
  const { loginWithGoogle, isLoading: storeLoading } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [scriptLoaded, setScriptLoaded] = useState(false);

  const clientId =
    process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "";

  // Load Google Identity Services script
  useEffect(() => {
    if (typeof window === "undefined") return;

    if (window.google?.accounts?.id) {
      setScriptLoaded(true);
      return;
    }

    const script = document.createElement("script");
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.defer = true;
    script.onload = () => {
      setScriptLoaded(true);
    };
    script.onerror = () => {
      console.warn("Failed to load Google Identity Services script, fallback will be used.");
    };
    document.head.appendChild(script);

    return () => {
      // Keep script in head for other components
    };
  }, []);

  // Initialize Google Identity Services when script is ready
  useEffect(() => {
    if (!scriptLoaded || typeof window === "undefined" || !window.google?.accounts?.id) return;

    try {
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: handleGoogleCredentialResponse,
        auto_select: false,
        cancel_on_tap_outside: true,
      });
    } catch (e) {
      console.warn("Google Identity initialization error:", e);
    }
  }, [scriptLoaded, clientId]);

  const handleGoogleCredentialResponse = async (response: any) => {
    if (!response?.credential) return;

    setLoading(true);
    try {
      await loginWithGoogle({ credential: response.credential, id_token: response.credential });
      const destination = redirectTo || "/citizen/dashboard";
      router.push(destination);
    } catch (err) {
      console.error("Google authentication failed:", err);
      setLoading(false);
    }
  };

  const handleClick = async () => {
    setLoading(true);

    // Try opening GSI popup prompt if available
    if (window.google?.accounts?.id) {
      try {
        window.google.accounts.id.prompt((notification: any) => {
          if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
            // If One-Tap prompt is not displayed or blocked, trigger OAuth redirect fallback
            initiateOAuthRedirect();
          }
        });
        // Give 2.5s for popup before redirect fallback
        setTimeout(() => {
          setLoading(false);
        }, 2500);
        return;
      } catch (err) {
        console.warn("Google prompt error, falling back to redirect:", err);
      }
    }

    // Direct OAuth Redirect flow fallback
    await initiateOAuthRedirect();
  };

  const initiateOAuthRedirect = async () => {
    try {
      const redirectUri = `${window.location.origin}/auth/callback/google`;
      const { auth_url } = await authService.getGoogleAuthUrl(redirectUri);
      window.location.href = auth_url;
    } catch (e) {
      console.error("Failed to construct Google authorization URL:", e);
      setLoading(false);
    }
  };

  const isBusy = loading || storeLoading;

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={isBusy}
      className={`w-full py-2.5 px-4 bg-white hover:bg-slate-50 text-slate-700 hover:text-slate-900 border border-slate-300 rounded text-xs font-semibold shadow-xs transition-all flex items-center justify-center gap-2.5 disabled:opacity-60 disabled:cursor-not-allowed ${className}`}
    >
      {isBusy ? (
        <>
          <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
          <span>Connecting to Google...</span>
        </>
      ) : (
        <>
          {/* Official Google G Logo SVG */}
          <svg className="w-4 h-4 flex-shrink-0" viewBox="0 0 24 24" aria-hidden="true">
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
            />
          </svg>
          <span className="truncate">{label}</span>
        </>
      )}
    </button>
  );
};

"use client";

import React, { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { useAuthStore } from "@/stores/authStore";
import { Loader2, AlertCircle, ArrowRight, ShieldCheck } from "lucide-react";

function GoogleCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { loginWithGoogle, user, role } = useAuthStore();
  const [error, setError] = useState<string | null>(null);
  const [statusText, setStatusText] = useState("Verifying Google credentials with governance backend...");

  useEffect(() => {
    const code = searchParams.get("code");
    const errorParam = searchParams.get("error");

    if (errorParam) {
      setError(`Google authorization was declined: ${errorParam}`);
      return;
    }

    if (!code) {
      setError("No authorization code received from Google.");
      return;
    }

    let isMounted = true;

    async function processCode() {
      try {
        setStatusText("Exchanging security token and provisioning citizen session...");
        const redirectUri = `${window.location.origin}/auth/callback/google`;
        await loginWithGoogle({ code, redirect_uri: redirectUri });

        if (!isMounted) return;
        setStatusText("Session verified. Redirecting to workspace...");

        setTimeout(() => {
          const targetRole = useAuthStore.getState().role;
          if (targetRole === "admin") {
            router.push("/admin");
          } else if (targetRole === "officer") {
            router.push("/officer/dashboard");
          } else {
            router.push("/citizen/dashboard");
          }
        }, 600);
      } catch (err: any) {
        if (!isMounted) return;
        console.error("Google OAuth callback error:", err);
        setError(
          err?.response?.data?.detail ||
          err?.message ||
          "Failed to complete Google authentication. Please try logging in again."
        );
      }
    }

    processCode();

    return () => {
      isMounted = false;
    };
  }, [searchParams, loginWithGoogle, router]);

  return (
    <div className="bg-white py-8 px-6 sm:px-10 shadow-card rounded-lg border border-slate-200/90 text-center">
      {error ? (
        <div className="space-y-4">
          <div className="w-12 h-12 rounded-full bg-red-50 text-red-600 flex items-center justify-center mx-auto border border-red-200">
            <AlertCircle className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900">Authentication Failed</h3>
            <p className="mt-1 text-xs text-red-600 bg-red-50 p-2.5 rounded border border-red-200">
              {error}
            </p>
          </div>
          <Link
            href="/login"
            className="inline-flex items-center justify-center gap-1.5 py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-semibold shadow-subtle transition-colors w-full"
          >
            <span>Return to Login</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="w-12 h-12 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center mx-auto border border-blue-100">
            <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900">Authenticating Citizen Identity</h3>
            <p className="mt-1 text-xs text-slate-500 font-mono">
              {statusText}
            </p>
          </div>
          <div className="pt-3 border-t border-slate-100 flex items-center justify-center gap-1.5 text-[11px] text-slate-400">
            <ShieldCheck className="w-3.5 h-3.5 text-teal-600" />
            <span>Protected by CivicMind AI Government Security Layer</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default function GoogleCallbackPage() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center mb-6">
        <Link href="/" className="inline-flex items-center gap-2">
          <div className="w-9 h-9 rounded bg-blue-600 text-white flex items-center justify-center font-bold text-sm shadow-subtle">
            CM
          </div>
          <span className="font-bold text-xl text-slate-900 tracking-tight">CivicMind AI</span>
        </Link>
      </div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0">
        <Suspense
          fallback={
            <div className="bg-white py-8 px-6 shadow-card rounded-lg border border-slate-200/90 text-center">
              <Loader2 className="w-6 h-6 animate-spin text-blue-600 mx-auto" />
              <p className="mt-2 text-xs text-slate-500">Initializing secure session...</p>
            </div>
          }
        >
          <GoogleCallbackContent />
        </Suspense>
      </div>
    </div>
  );
}

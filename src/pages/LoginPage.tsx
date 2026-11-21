import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import { UserRole } from "@/types";
import { MOCK_USERS } from "@/mocks/mockData";
import { Eye, EyeOff, Shield, ArrowRight, CheckCircle2, Lock, Sparkles, Building, User } from "lucide-react";
import { cn } from "@/lib/utils";
import { GoogleSignInButton } from "@/components/auth/GoogleSignInButton";

export default function LoginPage() {
  const navigate = useNavigate();
  const { login, isLoading } = useAuthStore();

  const [email, setEmail] = useState("commissioner.grievance@gov.in");
  const [password, setPassword] = useState("civicmind@2026");
  const [role, setRole] = useState<UserRole>("admin");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!email || !email.includes("@")) {
      setError("Please enter a valid official or citizen email address.");
      return;
    }
    if (!password || password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }

    try {
      await login({ email, password, role, rememberMe });
      if (role === "admin") {
        navigate("/admin");
      } else if (role === "officer") {
        navigate("/officer/dashboard");
      } else {
        navigate("/citizen/dashboard");
      }
    } catch (err: any) {
      setError(err?.message || "Failed to authenticate. Please check credentials.");
    }
  };

  const handleSelectDemo = (selectedUser: typeof MOCK_USERS[0]) => {
    setEmail(selectedUser.email);
    setRole(selectedUser.role);
    setPassword("civicmind@2026");
    setError(null);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <Link to="/" className="inline-flex items-center gap-2 mb-4">
          <div className="w-9 h-9 rounded bg-blue-600 text-white flex items-center justify-center font-bold text-sm shadow-subtle">
            CM
          </div>
          <span className="font-bold text-xl text-slate-900 tracking-tight">
            CivicMind AI
          </span>
        </Link>
        <h2 className="text-xl font-bold tracking-tight text-slate-900">
          Sign In to Governance Workspace
        </h2>
        <p className="mt-1 text-xs text-slate-500">
          Unified Citizen Grievance Intelligence and Resolution Prediction
        </p>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0">
        <div className="bg-white py-7 px-6 sm:px-8 shadow-card rounded-lg border border-slate-200/90">
          {error && (
            <div className="mb-4 p-3 rounded bg-red-50 border border-red-200 text-xs text-red-700">
              {error}
            </div>
          )}

          {/* Google Single Sign-On */}
          <div className="mb-4">
            <GoogleSignInButton label="Continue with Google" />
          </div>

          <div className="relative my-4">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200/90" />
            </div>
            <div className="relative flex justify-center text-[10px] uppercase">
              <span className="bg-white px-2.5 text-slate-400 font-mono font-semibold tracking-wider">
                Or sign in with official credentials
              </span>
            </div>
          </div>

          {/* Role Tabs */}
          <div className="mb-5">
            <label className="block text-xs font-semibold text-slate-700 mb-2 font-mono uppercase">
              Select Access Role
            </label>
            <div className="grid grid-cols-3 gap-1 p-1 bg-slate-100 rounded-md border border-slate-200/80">
              {(["citizen", "officer", "admin"] as UserRole[]).map((r) => (
                <button
                  type="button"
                  key={r}
                  onClick={() => {
                    setRole(r);
                    const defaultUser = MOCK_USERS.find((u) => u.role === r);
                    if (defaultUser) setEmail(defaultUser.email);
                  }}
                  className={cn(
                    "py-1.5 text-xs font-semibold rounded capitalize transition-all",
                    role === r
                      ? "bg-white text-blue-700 shadow-xs border border-slate-200"
                      : "text-slate-500 hover:text-slate-800"
                  )}
                >
                  {r === "admin" ? "Administrator" : r === "officer" ? "Duty Officer" : "Citizen"}
                </button>
              ))}
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Email Address
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@organization.gov.in"
                className="w-full px-3 py-2 text-xs border border-slate-200 rounded text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-xs font-semibold text-slate-700">
                  Password
                </label>
                <Link
                  to="/forgot-password"
                  className="text-[11px] text-blue-600 hover:text-blue-800 font-medium"
                >
                  Forgot password?
                </Link>
              </div>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full pl-3 pr-10 py-2 text-xs border border-slate-200 rounded text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-600"
                >
                  {showPassword ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-3.5 h-3.5"
                />
                <span className="text-xs text-slate-600">Remember this workstation</span>
              </label>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-semibold shadow-subtle transition-colors flex items-center justify-center gap-1.5"
            >
              {isLoading ? (
                "Authenticating Session..."
              ) : (
                <>
                  Enter {role === "admin" ? "Intelligence Command" : role === "officer" ? "Officer Desk" : "Citizen Portal"}
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </form>

          {/* Quick Demo Logins Section */}
          <div className="mt-6 pt-5 border-t border-slate-200/80">
            <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 font-bold block mb-2.5 text-center">
              Quick One-Click Demo Accounts
            </span>
            <div className="space-y-2">
              {MOCK_USERS.map((u) => (
                <button
                  key={u.id}
                  type="button"
                  onClick={() => handleSelectDemo(u)}
                  className={cn(
                    "w-full text-left p-2.5 rounded border text-xs flex items-center justify-between transition-colors",
                    email === u.email
                      ? "bg-blue-50/70 border-blue-300 text-blue-900 font-medium"
                      : "bg-slate-50 hover:bg-slate-100 border-slate-200 text-slate-700"
                  )}
                >
                  <div className="truncate">
                    <p className="font-semibold text-slate-900 truncate">{u.name}</p>
                    <p className="text-[11px] text-slate-500 font-mono truncate">{u.email}</p>
                  </div>
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-white border border-slate-200 font-semibold text-slate-600 flex-shrink-0">
                    {u.role}
                  </span>
                </button>
              ))}
            </div>
          </div>

          <div className="mt-5 text-center text-xs text-slate-500">
            Don't have an account?{" "}
            <Link to="/register" className="text-blue-600 hover:text-blue-800 font-semibold">
              Register as Citizen
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

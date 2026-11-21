import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import { ArrowRight, ShieldCheck } from "lucide-react";
import { GoogleSignInButton } from "@/components/auth/GoogleSignInButton";

export default function RegisterPage() {
  const navigate = useNavigate();
  const { setUser } = useAuthStore();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [ward, setWard] = useState("Ward 14 (South Zone)");
  const [password, setPassword] = useState("");
  const [success, setSuccess] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setUser({
      id: `usr_${Date.now()}`,
      name: name || "New Citizen",
      email,
      phone,
      ward,
      role: "citizen",
    });
    setSuccess(true);
    setTimeout(() => {
      navigate("/citizen/dashboard");
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <Link to="/" className="inline-flex items-center gap-2 mb-4">
          <div className="w-9 h-9 rounded bg-blue-600 text-white flex items-center justify-center font-bold text-sm shadow-subtle">
            CM
          </div>
          <span className="font-bold text-xl text-slate-900 tracking-tight">CivicMind AI</span>
        </Link>
        <h2 className="text-xl font-bold tracking-tight text-slate-900">
          Create Citizen Account
        </h2>
        <p className="mt-1 text-xs text-slate-500">
          Register to file complaints, receive automated AI status updates, and verify resolutions.
        </p>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0">
        <div className="bg-white py-7 px-6 sm:px-8 shadow-card rounded-lg border border-slate-200">
          {success && (
            <div className="mb-4 p-3 rounded bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 font-medium">
              Registration successful! Redirecting to your Citizen Dashboard...
            </div>
          )}

          {/* Google Fast Registration */}
          <div className="mb-4">
            <GoogleSignInButton label="Sign up with Google" />
          </div>

          <div className="relative my-4">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200/90" />
            </div>
            <div className="relative flex justify-center text-[10px] uppercase">
              <span className="bg-white px-2.5 text-slate-400 font-mono font-semibold tracking-wider">
                Or register with email details
              </span>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Full Legal Name
              </label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Aarav Sharma"
                className="w-full px-3 py-2 text-xs border border-slate-200 rounded text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Email Address
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="aarav.sharma@example.com"
                className="w-full px-3 py-2 text-xs border border-slate-200 rounded text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Mobile Number
                </label>
                <input
                  type="tel"
                  required
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="+91 98765 43210"
                  className="w-full px-3 py-2 text-xs border border-slate-200 rounded text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Primary Ward
                </label>
                <select
                  value={ward}
                  onChange={(e) => setWard(e.target.value)}
                  className="w-full px-3 py-2 text-xs border border-slate-200 rounded text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="Ward 14 (South Zone)">Ward 14 (South)</option>
                  <option value="Ward 15 (South Zone)">Ward 15 (South)</option>
                  <option value="Ward 07 (Central Zone)">Ward 07 (Central)</option>
                  <option value="Ward 12 (West Zone)">Ward 12 (West)</option>
                  <option value="Ward 22 (East Zone)">Ward 22 (East)</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Create Password
              </label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full px-3 py-2 text-xs border border-slate-200 rounded text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>

            <button
              type="submit"
              className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-semibold shadow-subtle transition-colors flex items-center justify-center gap-1.5"
            >
              Complete Registration
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </form>

          <div className="mt-5 text-center text-xs text-slate-500">
            Already registered?{" "}
            <Link to="/login" className="text-blue-600 hover:text-blue-800 font-semibold">
              Sign In to Existing Account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

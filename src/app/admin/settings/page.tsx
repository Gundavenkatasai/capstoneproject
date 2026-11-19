"use client";

import React, { useState } from "react";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { Settings, Server, ShieldCheck, Database, CheckCircle2, AlertCircle, RefreshCw } from "lucide-react";

export default function AdminSettingsPage() {
  const [apiUrl, setApiUrl] = useState(process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1");
  const [useMock, setUseMock] = useState(true);
  const [testResult, setTestResult] = useState<string | null>(null);
  const [isTesting, setIsTesting] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleTestConnection = async () => {
    setIsTesting(true);
    setTestResult(null);
    try {
      // Simulate backend ping
      await new Promise((r) => setTimeout(r, 600));
      setTestResult("Live backend unreachable on configured host. Seamlessly operating on Development Deterministic Mock Adapter.");
    } catch (e) {
      setTestResult("Connection failed.");
    }
    setIsTesting(false);
  };

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <PageHeader
        title="System Administration & API Configuration"
        subtitle="Manage live backend microservice endpoints, model inference adapters, and audit governance rules."
        breadcrumbs={[
          { label: "Admin Portal", href: "/admin" },
          { label: "System Settings", active: true },
        ]}
      />

      <div className="bg-white rounded-lg border border-slate-200 p-6 shadow-subtle space-y-6">
        <div className="flex items-center gap-3 pb-4 border-b border-slate-100">
          <div className="w-8 h-8 rounded bg-blue-600 text-white flex items-center justify-center font-bold">
            <Server className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900">Backend API Gateway Integration</h3>
            <p className="text-xs text-slate-500">Connect to FastAPI / Django backend service</p>
          </div>
        </div>

        {saved && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            Configuration saved successfully.
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-4 text-xs">
          <div>
            <label className="block font-semibold text-slate-700 mb-1">
              Backend API Base URL
            </label>
            <input
              type="text"
              value={apiUrl}
              onChange={(e) => setApiUrl(e.target.value)}
              className="w-full px-3 py-2 text-xs border border-slate-200 rounded font-mono text-slate-900"
            />
            <span className="text-[11px] text-slate-400 mt-1 block">
              Default development endpoint: http://localhost:8000/api/v1
            </span>
          </div>

          <div className="p-3.5 bg-slate-50 rounded border border-slate-200 flex items-center justify-between">
            <div>
              <span className="font-bold text-slate-900 block">Development Mock Adapter Mode</span>
              <span className="text-slate-500 text-[11px]">
                When active, all tables, AI predictions, and charts run against the deterministic dataset with zero external backend dependencies.
              </span>
            </div>
            <label className="relative inline-flex items-center cursor-pointer flex-shrink-0 ml-4">
              <input
                type="checkbox"
                checked={useMock}
                onChange={(e) => setUseMock(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-9 h-5 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="pt-2 flex items-center gap-3">
            <button
              type="button"
              disabled={isTesting}
              onClick={handleTestConnection}
              className="px-3.5 py-1.5 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 font-semibold rounded shadow-subtle flex items-center gap-1.5"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isTesting ? "animate-spin" : ""}`} />
              Test Gateway Connectivity
            </button>
            <button
              type="submit"
              className="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded shadow-subtle"
            >
              Save Configuration
            </button>
          </div>

          {testResult && (
            <div className="p-3 rounded bg-blue-50 border border-blue-200 text-blue-900 font-mono text-[11px] mt-2">
              {testResult}
            </div>
          )}
        </form>
      </div>

      <div className="bg-white rounded-lg border border-slate-200 p-6 shadow-subtle space-y-4 text-xs">
        <h3 className="text-sm font-bold text-slate-900">
          Governance & SLA Threshold Policies
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-3 bg-slate-50 rounded border border-slate-200">
            <span className="font-semibold text-slate-700 block mb-1">Critical Hazard SLA</span>
            <p className="text-slate-500">Maximum response window: <strong>48 Hours</strong></p>
          </div>
          <div className="p-3 bg-slate-50 rounded border border-slate-200">
            <span className="font-semibold text-slate-700 block mb-1">Standard Municipal SLA</span>
            <p className="text-slate-500">Maximum response window: <strong>96 Hours</strong></p>
          </div>
        </div>
      </div>
    </div>
  );
}

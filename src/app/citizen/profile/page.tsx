"use client";

import React, { useState } from "react";
import { useAuthStore } from "@/stores/authStore";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { User, Phone, Mail, MapPin, ShieldCheck, Check } from "lucide-react";

export default function CitizenProfilePage() {
  const { user, setUser } = useAuthStore();
  const [name, setName] = useState(user?.name || "Aarav Sharma");
  const [phone, setPhone] = useState(user?.phone || "+91 98765 43210");
  const [ward, setWard] = useState(user?.ward || "Ward 14 (Vasant Kunj)");
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    if (user) {
      setUser({
        ...user,
        name,
        phone,
        ward,
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    }
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <PageHeader
        title="Citizen Profile & Settings"
        subtitle="Manage your contact information, default municipal ward, and notifications."
        breadcrumbs={[
          { label: "Citizen Portal", href: "/citizen/dashboard" },
          { label: "Profile", active: true },
        ]}
      />

      <div className="bg-white rounded-lg border border-slate-200 p-6 shadow-subtle space-y-6">
        <div className="flex items-center gap-4 pb-6 border-b border-slate-100">
          <div className="w-16 h-16 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xl shadow-subtle overflow-hidden">
            {user?.avatar ? (
              <img src={user.avatar} alt={user.name} className="w-full h-full object-cover" />
            ) : (
              name.charAt(0)
            )}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-slate-900">{name}</h2>
              <span className="inline-flex items-center gap-1 text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                <ShieldCheck className="w-3 h-3" />
                Verified Resident
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5 font-mono">{user?.email}</p>
          </div>
        </div>

        {saved && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded text-xs flex items-center gap-2">
            <Check className="w-4 h-4 text-emerald-600" />
            Profile preferences successfully updated.
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Full Legal Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 text-xs border border-slate-200 rounded text-slate-900"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Primary Contact Phone
            </label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="w-full px-3 py-2 text-xs border border-slate-200 rounded text-slate-900 font-mono"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Primary Residential Ward
            </label>
            <select
              value={ward}
              onChange={(e) => setWard(e.target.value)}
              className="w-full px-3 py-2 text-xs border border-slate-200 rounded text-slate-900 font-medium"
            >
              <option value="Ward 14 (Vasant Kunj)">Ward 14 (Vasant Kunj, South Zone)</option>
              <option value="Ward 15 (Outer Ring Corridor)">Ward 15 (Outer Ring Corridor, South Zone)</option>
              <option value="Ward 07 (Karol Bagh)">Ward 07 (Karol Bagh, Central Zone)</option>
              <option value="Ward 12 (Dwarka)">Ward 12 (Dwarka, West Zone)</option>
              <option value="Ward 18 (Tilak Nagar)">Ward 18 (Tilak Nagar, West Zone)</option>
              <option value="Ward 22 (Mayur Vihar)">Ward 22 (Mayur Vihar, East Zone)</option>
            </select>
          </div>

          <div className="pt-3 flex justify-end">
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-semibold shadow-subtle transition-colors"
            >
              Save Profile Preferences
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

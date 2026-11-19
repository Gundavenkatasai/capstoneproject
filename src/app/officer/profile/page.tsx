"use client";

import React from "react";
import { useAuthStore } from "@/stores/authStore";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { ShieldCheck, Award, Building, Phone, Mail, MapPin } from "lucide-react";

export default function OfficerProfilePage() {
  const { user } = useAuthStore();

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <PageHeader
        title="Duty Officer Profile"
        subtitle="Jurisdiction credentials, assigned division, and duty roster."
        breadcrumbs={[
          { label: "Officer Portal", href: "/officer/dashboard" },
          { label: "Profile & Ward", active: true },
        ]}
      />

      <div className="bg-white rounded-lg border border-slate-200 p-6 shadow-subtle space-y-6">
        <div className="flex items-center gap-4 pb-6 border-b border-slate-100">
          <div className="w-16 h-16 rounded-full bg-amber-600 text-white flex items-center justify-center font-bold text-xl shadow-subtle overflow-hidden">
            {user?.avatar ? (
              <img src={user.avatar} alt={user.name} className="w-full h-full object-cover" />
            ) : (
              user?.name?.charAt(0) || "O"
            )}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-slate-900">{user?.name}</h2>
              <span className="inline-flex items-center gap-1 text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                <ShieldCheck className="w-3 h-3" />
                Superintending Engineer
              </span>
            </div>
            <p className="text-xs text-slate-500 font-mono mt-0.5">{user?.department}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="p-3 bg-slate-50 rounded border border-slate-200">
            <span className="text-slate-400 font-mono uppercase text-[10px] block">Government Email</span>
            <p className="font-semibold text-slate-800 mt-1 font-mono">{user?.email}</p>
          </div>

          <div className="p-3 bg-slate-50 rounded border border-slate-200">
            <span className="text-slate-400 font-mono uppercase text-[10px] block">Official Phone</span>
            <p className="font-semibold text-slate-800 mt-1 font-mono">{user?.phone}</p>
          </div>

          <div className="p-3 bg-slate-50 rounded border border-slate-200">
            <span className="text-slate-400 font-mono uppercase text-[10px] block">Jurisdiction Ward</span>
            <p className="font-semibold text-slate-800 mt-1">{user?.ward || "Central Division - Roads"}</p>
          </div>

          <div className="p-3 bg-slate-50 rounded border border-slate-200">
            <span className="text-slate-400 font-mono uppercase text-[10px] block">Duty Status</span>
            <p className="font-semibold text-emerald-700 mt-1 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              Active on Roster
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

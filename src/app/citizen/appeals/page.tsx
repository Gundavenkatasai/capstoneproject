"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { grievanceService } from "@/services/grievanceService";
import { Grievance } from "@/types";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { StatusBadge } from "@/components/common/StatusBadge";
import { PriorityBadge } from "@/components/common/PriorityBadge";
import { formatDate } from "@/lib/utils";
import { RotateCcw, AlertTriangle, ArrowRight, ShieldCheck } from "lucide-react";

export default function CitizenAppealsPage() {
  const [appeals, setAppeals] = useState<Grievance[]>([]);

  useEffect(() => {
    async function load() {
      const all = await grievanceService.getAll();
      setAppeals(all.filter((g) => g.status === "reopened" || g.status === "escalated"));
    }
    load();
  }, []);

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <PageHeader
        title="Appeals & Disputed Resolutions"
        subtitle="Complaints where the initial resolution was contested by citizens and reopened for senior supervisory audit."
        breadcrumbs={[
          { label: "Citizen Portal", href: "/citizen/dashboard" },
          { label: "Appeals & Reviews", active: true },
        ]}
      />

      <div className="bg-amber-50/70 border border-amber-200 p-4 rounded-lg flex items-start gap-3 text-xs text-amber-900">
        <ShieldCheck className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">Citizen Right of Appeal</span>
          <p className="mt-0.5 text-amber-800 leading-relaxed">
            Every citizen has the legal right to challenge any premature or unsatisfactory resolution. Reopened complaints bypass junior field dispatch and are assigned directly to the Zonal Chief Engineer.
          </p>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-slate-200 shadow-subtle divide-y divide-slate-100 overflow-hidden">
        {appeals.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-400">
            No active appeals or disputed complaints at this time.
          </div>
        ) : (
          appeals.map((g) => (
            <div key={g.id} className="p-5 flex items-start justify-between gap-4">
              <div className="space-y-1.5">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-800">
                    {g.id}
                  </span>
                  <StatusBadge status={g.status} />
                  <PriorityBadge priority={g.priority} />
                </div>
                <h3 className="text-sm font-bold text-slate-900">{g.title}</h3>
                <p className="text-xs text-slate-600 leading-relaxed">{g.description}</p>
                <div className="text-[11px] text-slate-500 pt-1">
                  Dept: <strong className="text-slate-800">{g.departmentName}</strong> • Reopened:{" "}
                  <strong className="text-slate-800 font-mono">{formatDate(g.updatedAt)}</strong>
                </div>
              </div>

              <Link
                href={`/citizen/grievances/${g.id}`}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-white hover:bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 shadow-subtle flex-shrink-0"
              >
                Inspect Audit <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

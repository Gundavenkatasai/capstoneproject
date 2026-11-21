import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { grievanceService } from "@/services/grievanceService";
import { Grievance } from "@/types";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { StatusBadge } from "@/components/common/StatusBadge";
import { PriorityBadge } from "@/components/common/PriorityBadge";
import { formatDate } from "@/lib/utils";
import { AlertTriangle, ArrowRight, ShieldAlert } from "lucide-react";

export default function OfficerEscalationsPage() {
  const [escalations, setEscalations] = useState<Grievance[]>([]);

  useEffect(() => {
    async function load() {
      const all = await grievanceService.getAll();
      setEscalations(all.filter((g) => g.status === "escalated" || g.slaBreached));
    }
    load();
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Escalations & SLA Breach Alerts"
        subtitle="Critical caseload where standard resolution SLA thresholds have been exceeded or life-safety risks triggered automatic supervisor escalation."
        breadcrumbs={[
          { label: "Officer Portal", href: "/officer/dashboard" },
          { label: "Escalations Queue", active: true },
        ]}
      />

      <div className="bg-red-50/80 border border-red-200 p-4 rounded-lg flex items-start gap-3 text-xs text-red-950">
        <ShieldAlert className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">Automated SLA Escalation Protocol</span>
          <p className="mt-0.5 text-red-800 leading-relaxed">
            These cases are actively flagged on the Apex Municipal Commissioner dashboard. Immediate field resolution or documented rationale is required.
          </p>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-slate-200 shadow-subtle divide-y divide-slate-100 overflow-hidden">
        {escalations.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-400">
            No escalated or overdue cases in your division. Excellent SLA compliance!
          </div>
        ) : (
          escalations.map((g) => (
            <div key={g.id} className="p-5 flex items-start justify-between gap-4 hover:bg-slate-50/60 transition-colors">
              <div className="space-y-1.5 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-800">
                    {g.id}
                  </span>
                  <StatusBadge status={g.status} />
                  <PriorityBadge priority={g.priority} />
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-red-100 text-red-700 font-bold border border-red-200">
                    BREACHED SLA
                  </span>
                </div>
                <h3 className="text-sm font-bold text-slate-900">{g.title}</h3>
                <p className="text-xs text-slate-600 leading-relaxed">{g.description}</p>
                <div className="text-[11px] text-slate-500 pt-1">
                  Ward: <strong className="text-slate-800">{g.location.ward}</strong> • SLA Deadline was:{" "}
                  <strong className="text-red-700 font-mono">{formatDate(g.slaDeadline)}</strong>
                </div>
              </div>

              <Link
                to={`/officer/grievances/${g.id}`}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded bg-red-600 hover:bg-red-700 text-white text-xs font-bold shadow-subtle flex-shrink-0 transition-colors"
              >
                Expedite Case <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

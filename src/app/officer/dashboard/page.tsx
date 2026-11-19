"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useAuthStore } from "@/stores/authStore";
import { grievanceService } from "@/services/grievanceService";
import { Grievance } from "@/types";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { MetricCard } from "@/components/common/MetricCard";
import { StatusBadge } from "@/components/common/StatusBadge";
import { PriorityBadge } from "@/components/common/PriorityBadge";
import { LoadingSkeleton, EmptyState } from "@/components/common/EmptyState";
import { formatDate } from "@/lib/utils";
import {
  ShieldAlert,
  Clock,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Wrench,
  ChevronRight,
  TrendingUp,
} from "lucide-react";

export default function OfficerDashboardPage() {
  const { user } = useAuthStore();
  const [grievances, setGrievances] = useState<Grievance[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      const all = await grievanceService.getAll();
      setGrievances(all);
      setLoading(false);
    }
    loadData();
  }, []);

  const assigned = grievances.length;
  const pending = grievances.filter((g) => g.status === "assigned" || g.status === "submitted").length;
  const inProgress = grievances.filter((g) => g.status === "in_progress").length;
  const resolved = grievances.filter((g) => g.status === "closed" || g.status === "resolution_submitted").length;
  const overdue = grievances.filter((g) => g.slaBreached).length;
  const critical = grievances.filter((g) => g.priority === "critical" || g.priority === "high").length;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Department Officer Workspace"
        subtitle={`Welcome, ${user?.name || "Duty Officer"} (${user?.department || "Public Works Department"}). Inspect assigned ward cases and submit resolution reports.`}
        badge="Field Duty Active"
        actions={
          <Link
            href="/officer/assigned"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-semibold shadow-subtle transition-colors"
          >
            View Assigned Queue ({assigned})
          </Link>
        }
      />

      {/* KPI Cards Row */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <MetricCard
          title="Assigned Cases"
          value={assigned}
          subtitle="Total department caseload"
          icon={Clock}
        />
        <MetricCard
          title="Pending Action"
          value={pending}
          subtitle="New dispatches"
          icon={AlertTriangle}
        />
        <MetricCard
          title="In Progress"
          value={inProgress}
          subtitle="Active field work"
          icon={Wrench}
        />
        <MetricCard
          title="Resolved (Mtd)"
          value={resolved}
          subtitle="Verified & closed"
          icon={CheckCircle2}
          isPositive={true}
        />
        <MetricCard
          title="Overdue SLA"
          value={overdue}
          subtitle="Requires escalation"
          icon={ShieldAlert}
          className={overdue > 0 ? "border-red-300 bg-red-50/20" : ""}
          isPositive={false}
        />
        <MetricCard
          title="High/Critical"
          value={critical}
          subtitle="Urgent hazard level"
          icon={TrendingUp}
          className="border-amber-300 bg-amber-50/20"
        />
      </div>

      {/* Main Caseload Table */}
      {loading ? (
        <LoadingSkeleton count={4} />
      ) : (
        <div className="bg-white rounded-lg border border-slate-200 overflow-hidden shadow-subtle">
          <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Priority Assigned Cases</h3>
              <p className="text-xs text-slate-500">Sorted by SLA countdown & hazard urgency</p>
            </div>
            <Link href="/officer/assigned" className="text-xs text-blue-600 hover:text-blue-800 font-semibold">
              Full Queue Table →
            </Link>
          </div>

          <div className="divide-y divide-slate-100">
            {grievances.slice(0, 5).map((g) => (
              <div
                key={g.id}
                className="p-4 hover:bg-slate-50/80 transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-4"
              >
                <div className="space-y-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-800 border border-slate-200">
                      {g.id}
                    </span>
                    <StatusBadge status={g.status} />
                    <PriorityBadge priority={g.priority} />
                    {g.slaBreached ? (
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-red-100 text-red-700 font-bold border border-red-200 animate-pulse">
                        SLA BREACHED
                      </span>
                    ) : (
                      <span className="text-[10px] font-mono text-slate-500">
                        Deadline: {formatDate(g.slaDeadline)}
                      </span>
                    )}
                  </div>

                  <h4 className="text-xs font-bold text-slate-900 truncate">{g.title}</h4>
                  <p className="text-[11px] text-slate-500 line-clamp-1">
                    {g.location.address} ({g.location.ward})
                  </p>
                </div>

                <div className="flex items-center gap-2 flex-shrink-0">
                  <Link
                    href={`/officer/grievances/${g.id}`}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-subtle transition-colors"
                  >
                    Take Action <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
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
  PlusCircle,
  FileText,
  Clock,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  ShieldAlert,
  ChevronRight,
} from "lucide-react";

export default function CitizenDashboardPage() {
  const { user } = useAuthStore();
  const [grievances, setGrievances] = useState<Grievance[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      const data = await grievanceService.getAll();
      setGrievances(data);
      setLoading(false);
    }
    loadData();
  }, []);

  const total = grievances.length;
  const pending = grievances.filter((g) => ["submitted", "analyzed", "assigned", "in_progress"].includes(g.status)).length;
  const resolved = grievances.filter((g) => ["closed", "citizen_verified"].includes(g.status)).length;
  const requiresAttention = grievances.filter((g) => g.status === "resolution_submitted").length;

  const activeComplaint = grievances.find((g) => g.status === "in_progress" || g.status === "assigned") || grievances[0];

  return (
    <div className="space-y-6">
      <PageHeader
        title={`Citizen Services Portal`}
        subtitle={`Welcome back, ${user?.name || "Resident"}. Track and file complaints across municipal departments with automated AI assistance.`}
        badge="Citizen Verified"
        actions={
          <Link
            to="/citizen/submit"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-subtle transition-colors"
          >
            <PlusCircle className="w-4 h-4" />
            Submit New Grievance
          </Link>
        }
      />

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Complaints Filed"
          value={total}
          subtitle="Lifetime civic submissions"
          icon={FileText}
        />
        <MetricCard
          title="In Resolution Pipeline"
          value={pending}
          subtitle="Assigned to field squads"
          icon={Clock}
          changeType="neutral"
        />
        <MetricCard
          title="Successfully Resolved"
          value={resolved}
          subtitle="Verified by citizens"
          icon={CheckCircle2}
          isPositive={true}
        />
        <MetricCard
          title="Action Required"
          value={requiresAttention}
          subtitle="Resolution reports waiting for your sign-off"
          icon={AlertTriangle}
          className={requiresAttention > 0 ? "border-amber-300 bg-amber-50/20" : ""}
        />
      </div>

      {loading ? (
        <LoadingSkeleton count={3} />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Active Tracking Card */}
          <div className="lg:col-span-2 space-y-6">
            {activeComplaint && (
              <div className="bg-white rounded-lg border border-slate-200 p-6 shadow-subtle">
                <div className="flex items-center justify-between pb-4 border-b border-slate-100">
                  <div className="flex items-center gap-2.5">
                    <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                      {activeComplaint.id}
                    </span>
                    <span className="text-xs text-slate-500 font-medium">Currently Monitored</span>
                  </div>
                  <StatusBadge status={activeComplaint.status} />
                </div>

                <div className="mt-4">
                  <h3 className="text-base font-bold text-slate-900">{activeComplaint.title}</h3>
                  <p className="text-xs text-slate-600 mt-1.5 leading-relaxed line-clamp-2">
                    {activeComplaint.description}
                  </p>
                </div>

                {/* Progress bar visual */}
                <div className="mt-6 pt-4 border-t border-slate-100">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-700 mb-2">
                    <span>Resolution Lifecycle</span>
                    <span className="font-mono text-blue-600">
                      Estimated Completion: {formatDate(activeComplaint.expectedResolutionDate)}
                    </span>
                  </div>
                  <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                    <div
                      className="bg-blue-600 h-full rounded-full transition-all duration-500"
                      style={{
                        width:
                          activeComplaint.status === "closed"
                            ? "100%"
                            : activeComplaint.status === "resolution_submitted"
                            ? "85%"
                            : activeComplaint.status === "in_progress"
                            ? "60%"
                            : activeComplaint.status === "assigned"
                            ? "35%"
                            : "15%",
                      }}
                    />
                  </div>

                  <div className="grid grid-cols-5 text-[10px] text-slate-400 font-mono mt-2 text-center">
                    <span className="text-blue-700 font-semibold">Submitted</span>
                    <span className={["assigned", "in_progress", "resolution_submitted", "closed"].includes(activeComplaint.status) ? "text-blue-700 font-semibold" : ""}>Assigned</span>
                    <span className={["in_progress", "resolution_submitted", "closed"].includes(activeComplaint.status) ? "text-blue-700 font-semibold" : ""}>In Progress</span>
                    <span className={["resolution_submitted", "closed"].includes(activeComplaint.status) ? "text-blue-700 font-semibold" : ""}>Resolved</span>
                    <span className={activeComplaint.status === "closed" ? "text-emerald-700 font-semibold" : ""}>Verified</span>
                  </div>
                </div>

                <div className="mt-6 flex items-center justify-between pt-4 border-t border-slate-100">
                  <div className="text-xs text-slate-500">
                    Assigned Officer:{" "}
                    <span className="font-semibold text-slate-800">
                      {activeComplaint.assignedOfficerName || "Auto-Dispatching..."}
                    </span>
                  </div>
                  <Link
                    to={`/citizen/grievances/${activeComplaint.id}`}
                    className="inline-flex items-center gap-1.5 text-xs font-bold text-blue-600 hover:text-blue-800"
                  >
                    View Grievance Details <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            )}

            {/* Recent Submissions List */}
            <div className="bg-white rounded-lg border border-slate-200 overflow-hidden shadow-subtle">
              <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
                <h3 className="text-sm font-bold text-slate-900">Your Recent Grievances</h3>
                <Link to="/citizen/grievances" className="text-xs text-blue-600 hover:text-blue-800 font-semibold">
                  View All ({grievances.length}) →
                </Link>
              </div>

              <div className="divide-y divide-slate-100">
                {grievances.slice(0, 4).map((g) => (
                  <Link
                    key={g.id}
                    to={`/citizen/grievances/${g.id}`}
                    className="p-4 hover:bg-slate-50/80 transition-colors flex items-center justify-between group block"
                  >
                    <div className="min-w-0 pr-4">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-mono text-[11px] font-bold text-slate-600">
                          {g.id}
                        </span>
                        <StatusBadge status={g.status} className="py-0 px-2 text-[10px]" />
                        <PriorityBadge priority={g.priority} className="py-0 px-1.5 text-[10px]" />
                      </div>
                      <h4 className="text-xs font-semibold text-slate-900 group-hover:text-blue-600 transition-colors truncate">
                        {g.title}
                      </h4>
                      <p className="text-[11px] text-slate-400 mt-0.5">
                        {g.departmentName} • {formatDate(g.submittedAt)}
                      </p>
                    </div>

                    <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-slate-600 flex-shrink-0" />
                  </Link>
                ))}
              </div>
            </div>
          </div>

          {/* Right Rail: Quick Help & AI Notice */}
          <div className="space-y-6">
            <div className="p-5 rounded-lg border border-blue-200 bg-gradient-to-br from-blue-50/60 to-white shadow-subtle">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-7 h-7 rounded bg-blue-600 text-white flex items-center justify-center">
                  <Sparkles className="w-4 h-4" />
                </div>
                <h4 className="text-xs font-bold text-slate-900">AI-Powered Citizen Transparency</h4>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                CivicMind AI automatically reads your complaint, categorizes the issue, detects similar nearby reports to prevent duplication, and assigns it to the exact field engineer with a guaranteed SLA deadline.
              </p>
              <Link
                to="/citizen/submit"
                className="mt-4 block text-center py-2 px-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded text-xs transition-colors shadow-subtle"
              >
                File an Issue Now
              </Link>
            </div>

            <div className="p-5 rounded-lg border border-slate-200 bg-white shadow-subtle">
              <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-3">
                Emergency Civic Hotlines
              </h4>
              <div className="space-y-2.5 text-xs">
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-600">Central Municipal Call Center</span>
                  <span className="font-mono font-bold text-slate-900">1916</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-600">Water Pipeline Emergency</span>
                  <span className="font-mono font-bold text-slate-900">1916-Ext 2</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-600">Electricity & Power Outage</span>
                  <span className="font-mono font-bold text-slate-900">1912</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-600">Solid Waste Rapid Pickup</span>
                  <span className="font-mono font-bold text-slate-900">1800-11-2244</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

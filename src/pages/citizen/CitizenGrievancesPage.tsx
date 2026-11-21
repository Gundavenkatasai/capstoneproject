import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { grievanceService } from "@/services/grievanceService";
import { Grievance } from "@/types";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { SearchInput } from "@/components/common/SearchInput";
import { FilterDropdown } from "@/components/common/SearchInput";
import { StatusBadge } from "@/components/common/StatusBadge";
import { PriorityBadge } from "@/components/common/PriorityBadge";
import { LoadingSkeleton, EmptyState } from "@/components/common/EmptyState";
import { formatDate } from "@/lib/utils";
import { Plus, ChevronRight, Eye } from "lucide-react";

export default function CitizenGrievancesListPage() {
  const [grievances, setGrievances] = useState<Grievance[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      const data = await grievanceService.getAll({
        search,
        status: statusFilter,
      });
      setGrievances(data);
      setLoading(false);
    }
    loadData();
  }, [search, statusFilter]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="My Civic Grievances"
        subtitle="Track the real-time progress and verification status of all your submitted complaints."
        breadcrumbs={[
          { label: "Citizen Portal", href: "/citizen/dashboard" },
          { label: "My Grievances", active: true },
        ]}
        actions={
          <Link
            to="/citizen/submit"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-semibold shadow-subtle transition-colors"
          >
            <Plus className="w-3.5 h-3.5" /> File New Grievance
          </Link>
        }
      />

      {/* Filter and Search Bar */}
      <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-subtle flex flex-col sm:flex-row items-center justify-between gap-3">
        <SearchInput
          value={search}
          onChange={setSearch}
          placeholder="Search by ID, keyword, or location..."
        />

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <FilterDropdown
            label="Status"
            value={statusFilter}
            onChange={setStatusFilter}
            options={[
              { label: "All Statuses", value: "all" },
              { label: "Submitted", value: "submitted" },
              { label: "Assigned", value: "assigned" },
              { label: "In Progress", value: "in_progress" },
              { label: "Resolution Filed", value: "resolution_submitted" },
              { label: "Closed", value: "closed" },
              { label: "Reopened", value: "reopened" },
            ]}
          />
        </div>
      </div>

      {/* Grievances List */}
      {loading ? (
        <LoadingSkeleton count={4} />
      ) : grievances.length === 0 ? (
        <EmptyState
          title="No grievances found"
          description="No complaints matched your search criteria. Submit a new complaint to get started."
          actionLabel="Submit Grievance"
          onAction={() => (window.location.href = "/citizen/submit")}
        />
      ) : (
        <div className="bg-white rounded-lg border border-slate-200 overflow-hidden shadow-subtle divide-y divide-slate-100">
          {grievances.map((g) => (
            <div
              key={g.id}
              className="p-5 hover:bg-slate-50/70 transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-4"
            >
              <div className="space-y-1.5 min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-800 border border-slate-200">
                    {g.id}
                  </span>
                  <StatusBadge status={g.status} />
                  <PriorityBadge priority={g.priority} />
                  <span className="text-[11px] text-slate-400 font-mono">
                    Filed: {formatDate(g.submittedAt)}
                  </span>
                </div>

                <h3 className="text-sm font-bold text-slate-900 line-clamp-1">
                  {g.title}
                </h3>

                <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed">
                  {g.description}
                </p>

                <div className="text-[11px] text-slate-500 flex flex-wrap gap-x-4 gap-y-1 pt-1">
                  <span>
                    Dept: <strong className="text-slate-700">{g.departmentName}</strong>
                  </span>
                  <span>
                    Location: <strong className="text-slate-700">{g.location.address}</strong>
                  </span>
                  <span>
                    Expected SLA:{" "}
                    <strong className="text-slate-700 font-mono">
                      {formatDate(g.expectedResolutionDate)}
                    </strong>
                  </span>
                </div>
              </div>

              <div className="flex sm:flex-col items-center sm:items-end justify-between sm:justify-center gap-2 flex-shrink-0">
                <Link
                  to={`/citizen/grievances/${g.id}`}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-blue-50 hover:bg-blue-100 border border-blue-200 text-blue-700 text-xs font-semibold transition-colors"
                >
                  <Eye className="w-3.5 h-3.5" />
                  View Progress
                </Link>
                {g.status === "resolution_submitted" && (
                  <span className="text-[10px] font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200 animate-pulse">
                    Action Required
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

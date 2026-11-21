import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { grievanceService } from "@/services/grievanceService";
import { Grievance } from "@/types";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { SearchInput } from "@/components/common/SearchInput";
import { FilterDropdown } from "@/components/common/SearchInput";
import { StatusBadge } from "@/components/common/StatusBadge";
import { PriorityBadge } from "@/components/common/PriorityBadge";
import { ExportMenu } from "@/components/common/SearchInput";
import { LoadingSkeleton, EmptyState } from "@/components/common/EmptyState";
import { ComplaintDetailDrawer } from "@/components/common/ComplaintDetailDrawer";
import { formatDate, exportToCsv } from "@/lib/utils";
import { Eye, ArrowRight } from "lucide-react";

export default function OfficerAssignedPage() {
  const [grievances, setGrievances] = useState<Grievance[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");

  const [selectedGrievance, setSelectedGrievance] = useState<Grievance | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await grievanceService.getAll({
        search,
        priority: priorityFilter,
        status: statusFilter,
      });
      setGrievances(data);
      setLoading(false);
    }
    load();
  }, [search, priorityFilter, statusFilter]);

  const handleExport = () => {
    exportToCsv(
      `officer_caseload_${Date.now()}`,
      grievances.map((g) => ({
        ID: g.id,
        Title: g.title,
        Category: g.category,
        Department: g.departmentName,
        Priority: g.priority,
        Status: g.status,
        Address: g.location.address,
        Ward: g.location.ward,
        Deadline: g.slaDeadline,
        Breached: g.slaBreached ? "YES" : "NO",
      }))
    );
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Assigned Field Queue"
        subtitle="Operational caseload assigned to your jurisdiction. Review evidence, manage dispatch, and file completion reports."
        breadcrumbs={[
          { label: "Officer Portal", href: "/officer/dashboard" },
          { label: "Assigned Caseload", active: true },
        ]}
        actions={<ExportMenu onExportCsv={handleExport} />}
      />

      {/* Filter and Search Bar */}
      <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-subtle flex flex-col sm:flex-row items-center justify-between gap-3">
        <SearchInput
          value={search}
          onChange={setSearch}
          placeholder="Search by ID, keyword, citizen, ward..."
        />

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <FilterDropdown
            label="Priority"
            value={priorityFilter}
            onChange={setPriorityFilter}
            options={[
              { label: "All Priorities", value: "all" },
              { label: "Critical", value: "critical" },
              { label: "High", value: "high" },
              { label: "Medium", value: "medium" },
              { label: "Low", value: "low" },
            ]}
          />
          <FilterDropdown
            label="Status"
            value={statusFilter}
            onChange={setStatusFilter}
            options={[
              { label: "All Statuses", value: "all" },
              { label: "Assigned", value: "assigned" },
              { label: "In Progress", value: "in_progress" },
              { label: "Resolution Filed", value: "resolution_submitted" },
              { label: "Closed", value: "closed" },
            ]}
          />
        </div>
      </div>

      {loading ? (
        <LoadingSkeleton type="table" count={5} />
      ) : grievances.length === 0 ? (
        <EmptyState
          title="No grievances in assigned queue"
          description="All assigned complaints for this filter set have been attended to or reassigned."
        />
      ) : (
        <div className="bg-white rounded-lg border border-slate-200 overflow-hidden shadow-subtle">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-mono text-[11px] uppercase">
                  <th className="py-3 px-4 font-semibold">Complaint ID</th>
                  <th className="py-3 px-4 font-semibold">Title & Description</th>
                  <th className="py-3 px-4 font-semibold">Ward & Location</th>
                  <th className="py-3 px-4 font-semibold">Priority</th>
                  <th className="py-3 px-4 font-semibold">Status</th>
                  <th className="py-3 px-4 font-semibold">SLA Target</th>
                  <th className="py-3 px-4 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {grievances.map((g) => (
                  <tr key={g.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 px-4 font-mono font-bold text-slate-900 whitespace-nowrap">
                      {g.id}
                    </td>
                    <td className="py-3 px-4 max-w-xs">
                      <p className="font-semibold text-slate-900 truncate">{g.title}</p>
                      <p className="text-[11px] text-slate-400 truncate">{g.category}</p>
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap">
                      <p className="text-slate-800 font-medium">{g.location.ward}</p>
                      <p className="text-[10px] text-slate-400 truncate max-w-[150px]">{g.location.address}</p>
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap">
                      <PriorityBadge priority={g.priority} />
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap">
                      <StatusBadge status={g.status} />
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap font-mono">
                      {g.slaBreached ? (
                        <span className="text-red-700 font-bold bg-red-50 px-1.5 py-0.5 rounded border border-red-200">
                          OVERDUE
                        </span>
                      ) : (
                        <span className="text-slate-700">{formatDate(g.slaDeadline)}</span>
                      )}
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap text-right space-x-1">
                      <button
                        onClick={() => {
                          setSelectedGrievance(g);
                          setDrawerOpen(true);
                        }}
                        className="px-2.5 py-1 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded border border-slate-200 transition-colors"
                        title="Quick View Drawer"
                      >
                        Inspect
                      </button>
                      <Link
                        to={`/officer/grievances/${g.id}`}
                        className="inline-flex items-center gap-1 px-2.5 py-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded shadow-subtle transition-colors"
                      >
                        Action <ArrowRight className="w-3 h-3" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Quick Drawer */}
      <ComplaintDetailDrawer
        grievance={selectedGrievance}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        baseRoute="/officer"
      />
    </div>
  );
}

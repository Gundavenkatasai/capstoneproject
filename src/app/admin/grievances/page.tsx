"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { grievanceService } from "@/services/grievanceService";
import { Grievance, GrievanceStatus, GrievancePriority } from "@/types";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { SearchInput, FilterDropdown, ExportMenu } from "@/components/common/SearchInput";
import { StatusBadge } from "@/components/common/StatusBadge";
import { PriorityBadge } from "@/components/common/PriorityBadge";
import { ConfidenceIndicator } from "@/components/common/ConfidenceIndicator";
import { ComplaintDetailDrawer } from "@/components/common/ComplaintDetailDrawer";
import { LoadingSkeleton, EmptyState } from "@/components/common/EmptyState";
import { formatDate, exportToCsv } from "@/lib/utils";
import {
  FileText,
  Filter,
  CheckSquare,
  ArrowRight,
  MoreHorizontal,
  Eye,
  SlidersHorizontal,
  ChevronLeft,
  ChevronRight,
  ShieldAlert,
} from "lucide-react";

export default function AdminGrievancesPage() {
  const [grievances, setGrievances] = useState<Grievance[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [priorityFilter, setPriorityFilter] = useState("all");
  const [deptFilter, setDeptFilter] = useState("all");

  // Selection & Bulk Actions
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  // Drawer
  const [selectedGrievance, setSelectedGrievance] = useState<Grievance | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 8;

  useEffect(() => {
    async function fetchList() {
      setLoading(true);
      const data = await grievanceService.getAll({
        search,
        status: statusFilter,
        priority: priorityFilter,
        departmentId: deptFilter,
      });
      setGrievances(data);
      setLoading(false);
    }
    fetchList();
  }, [search, statusFilter, priorityFilter, deptFilter]);

  const handleSelectAll = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.checked) {
      setSelectedIds(grievances.map((g) => g.id));
    } else {
      setSelectedIds([]);
    }
  };

  const handleToggleSelect = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const handleExportCsv = () => {
    exportToCsv(
      `civicmind_all_grievances_${Date.now()}`,
      grievances.map((g) => ({
        ID: g.id,
        Title: g.title,
        Citizen: g.citizenName,
        Department: g.departmentName,
        Category: g.category,
        Priority: g.priority,
        Status: g.status,
        Confidence: `${Math.round(g.aiConfidence * 100)}%`,
        Ward: g.location.ward,
        Address: g.location.address,
        SubmittedAt: g.submittedAt,
        Deadline: g.slaDeadline,
        SLABreached: g.slaBreached ? "YES" : "NO",
      }))
    );
  };

  // Pagination slice
  const totalPages = Math.ceil(grievances.length / pageSize) || 1;
  const paginatedList = grievances.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  return (
    <div className="space-y-6">
      <PageHeader
        title="All Grievances & Priority Queue"
        subtitle="Comprehensive cross-departmental complaint ledger with multi-level filtering, automated triage scores, and bulk administration."
        breadcrumbs={[
          { label: "Admin Portal", href: "/admin" },
          { label: "All Grievances", active: true },
        ]}
        actions={
          <div className="flex items-center gap-2">
            <ExportMenu onExportCsv={handleExportCsv} />
          </div>
        }
      />

      {/* Filter Toolbar */}
      <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-subtle flex flex-col md:flex-row items-center justify-between gap-3">
        <SearchInput
          value={search}
          onChange={setSearch}
          placeholder="Search by ID, keyword, citizen, ward, street..."
          className="w-full md:w-80"
        />

        <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
          <FilterDropdown
            label="Department"
            value={deptFilter}
            onChange={setDeptFilter}
            options={[
              { label: "All Departments", value: "all" },
              { label: "Water Supply (WSSB)", value: "dept_wssb" },
              { label: "Public Works (PWD)", value: "dept_pwd" },
              { label: "Solid Waste (SWM)", value: "dept_swm" },
              { label: "Electricity (UESL)", value: "dept_elec" },
            ]}
          />
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
              { label: "Submitted", value: "submitted" },
              { label: "Assigned", value: "assigned" },
              { label: "In Progress", value: "in_progress" },
              { label: "Resolution Filed", value: "resolution_submitted" },
              { label: "Closed", value: "closed" },
              { label: "Escalated", value: "escalated" },
              { label: "Reopened", value: "reopened" },
            ]}
          />
        </div>
      </div>

      {/* Bulk Action Toolbar if items selected */}
      {selectedIds.length > 0 && (
        <div className="p-3 rounded-md bg-blue-50 border border-blue-200 flex items-center justify-between text-xs animate-in fade-in">
          <div className="flex items-center gap-2">
            <span className="font-bold text-blue-900">{selectedIds.length} complaints selected</span>
            <span className="text-blue-700">| Bulk Actions:</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => alert(`Bulk escalation triggered for ${selectedIds.length} cases.`)}
              className="px-2.5 py-1 bg-white hover:bg-slate-50 border border-blue-200 text-blue-800 font-semibold rounded"
            >
              Bulk Escalate to Zonal Chief
            </button>
            <button
              onClick={() => setSelectedIds([])}
              className="text-slate-500 hover:text-slate-800 underline ml-2"
            >
              Clear Selection
            </button>
          </div>
        </div>
      )}

      {/* Main Data Table */}
      {loading ? (
        <LoadingSkeleton type="table" count={6} />
      ) : grievances.length === 0 ? (
        <EmptyState
          title="No grievances found"
          description="Try broadening your search term or resetting your filter criteria."
        />
      ) : (
        <div className="bg-white rounded-lg border border-slate-200 overflow-hidden shadow-subtle">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-mono text-[11px] uppercase">
                  <th className="py-3 px-3.5 w-8">
                    <input
                      type="checkbox"
                      checked={selectedIds.length === grievances.length && grievances.length > 0}
                      onChange={handleSelectAll}
                      className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                    />
                  </th>
                  <th className="py-3 px-3.5 font-semibold">ID</th>
                  <th className="py-3 px-3.5 font-semibold">Citizen</th>
                  <th className="py-3 px-3.5 font-semibold">Description</th>
                  <th className="py-3 px-3.5 font-semibold">Department</th>
                  <th className="py-3 px-3.5 font-semibold">Location</th>
                  <th className="py-3 px-3.5 font-semibold">Priority</th>
                  <th className="py-3 px-3.5 font-semibold">AI Conf.</th>
                  <th className="py-3 px-3.5 font-semibold">Status</th>
                  <th className="py-3 px-3.5 font-semibold">Submitted</th>
                  <th className="py-3 px-3.5 font-semibold">Expected SLA</th>
                  <th className="py-3 px-3.5 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {paginatedList.map((g) => (
                  <tr
                    key={g.id}
                    className={`hover:bg-slate-50/80 transition-colors ${
                      selectedIds.includes(g.id) ? "bg-blue-50/30" : ""
                    }`}
                  >
                    <td className="py-3 px-3.5">
                      <input
                        type="checkbox"
                        checked={selectedIds.includes(g.id)}
                        onChange={() => handleToggleSelect(g.id)}
                        className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                      />
                    </td>
                    <td className="py-3 px-3.5 font-mono font-bold text-slate-900 whitespace-nowrap">
                      {g.id}
                    </td>
                    <td className="py-3 px-3.5 whitespace-nowrap">
                      <span className="font-semibold text-slate-800">
                        {g.isAnonymous ? "Anonymous" : g.citizenName}
                      </span>
                    </td>
                    <td className="py-3 px-3.5 max-w-xs">
                      <p className="font-medium text-slate-900 truncate">{g.title}</p>
                      <p className="text-[11px] text-slate-400 truncate">{g.description}</p>
                    </td>
                    <td className="py-3 px-3.5 whitespace-nowrap">
                      <span className="font-medium text-slate-800">{g.departmentName}</span>
                    </td>
                    <td className="py-3 px-3.5 whitespace-nowrap">
                      <span className="text-slate-800">{g.location.ward}</span>
                      <p className="text-[10px] text-slate-400 font-mono truncate max-w-[120px]">
                        {g.location.address}
                      </p>
                    </td>
                    <td className="py-3 px-3.5 whitespace-nowrap">
                      <PriorityBadge priority={g.priority} />
                    </td>
                    <td className="py-3 px-3.5 whitespace-nowrap">
                      <ConfidenceIndicator confidence={g.aiConfidence} showBar={false} />
                    </td>
                    <td className="py-3 px-3.5 whitespace-nowrap">
                      <StatusBadge status={g.status} />
                    </td>
                    <td className="py-3 px-3.5 whitespace-nowrap font-mono text-slate-500">
                      {formatDate(g.submittedAt)}
                    </td>
                    <td className="py-3 px-3.5 whitespace-nowrap font-mono">
                      {g.slaBreached ? (
                        <span className="text-[10px] font-bold text-red-700 bg-red-50 px-1.5 py-0.5 rounded border border-red-200">
                          OVERDUE
                        </span>
                      ) : (
                        <span className="text-slate-700">{formatDate(g.slaDeadline)}</span>
                      )}
                    </td>
                    <td className="py-3 px-3.5 whitespace-nowrap text-right space-x-1">
                      <button
                        onClick={() => {
                          setSelectedGrievance(g);
                          setDrawerOpen(true);
                        }}
                        className="px-2.5 py-1 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded border border-slate-200 font-medium"
                        title="Slideout Drawer"
                      >
                        Inspect
                      </button>
                      <Link
                        href={`/admin/grievances/${g.id}`}
                        className="inline-flex items-center gap-1 px-2.5 py-1 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded border border-blue-200 font-semibold"
                      >
                        Details <ArrowRight className="w-3 h-3" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination Footer */}
          <div className="px-4 py-3 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500">
            <div>
              Showing{" "}
              <strong>
                {(currentPage - 1) * pageSize + 1} -{" "}
                {Math.min(currentPage * pageSize, grievances.length)}
              </strong>{" "}
              of <strong>{grievances.length}</strong> complaints
            </div>

            <div className="flex items-center gap-1">
              <button
                disabled={currentPage === 1}
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                className="p-1.5 rounded border border-slate-200 bg-white hover:bg-slate-100 disabled:opacity-40"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="px-3 py-1 font-mono text-slate-700 font-medium">
                Page {currentPage} of {totalPages}
              </span>
              <button
                disabled={currentPage === totalPages}
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                className="p-1.5 rounded border border-slate-200 bg-white hover:bg-slate-100 disabled:opacity-40"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Slide-out Drawer */}
      <ComplaintDetailDrawer
        grievance={selectedGrievance}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        baseRoute="/admin"
      />
    </div>
  );
}

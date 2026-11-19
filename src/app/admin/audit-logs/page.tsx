"use client";

import React, { useState } from "react";
import { MOCK_AUDIT_LOGS } from "@/mocks/mockData";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { SearchInput, FilterDropdown, ExportMenu } from "@/components/common/SearchInput";
import { formatDate, exportToCsv } from "@/lib/utils";
import { ScrollText, Shield, User, Bot, AlertTriangle, CheckCircle2 } from "lucide-react";

export default function AuditLogsPage() {
  const [logs, setLogs] = useState(MOCK_AUDIT_LOGS);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");

  const filtered = logs.filter((log) => {
    const matchesSearch =
      log.action.toLowerCase().includes(search.toLowerCase()) ||
      log.details.toLowerCase().includes(search.toLowerCase()) ||
      log.performedBy.toLowerCase().includes(search.toLowerCase()) ||
      log.entityId.toLowerCase().includes(search.toLowerCase());
    const matchesType = typeFilter === "all" || log.entityType === typeFilter;
    return matchesSearch && matchesType;
  });

  const handleExport = () => {
    exportToCsv("civicmind_audit_trail", filtered);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Audit Logs & Regulatory Compliance"
        subtitle="Immutable transaction ledger recording all administrative decisions, manual overrides, duplicate merges, and automated SLA escalations."
        breadcrumbs={[
          { label: "Admin Portal", href: "/admin" },
          { label: "Audit Logs", active: true },
        ]}
        actions={<ExportMenu onExportCsv={handleExport} />}
        badge="WORM Tamper-Evident"
      />

      <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-subtle flex flex-col sm:flex-row items-center justify-between gap-3">
        <SearchInput
          value={search}
          onChange={setSearch}
          placeholder="Search action, user, entity ID, or details..."
          className="w-full sm:w-80"
        />

        <FilterDropdown
          label="Entity Type"
          value={typeFilter}
          onChange={setTypeFilter}
          options={[
            { label: "All Entities", value: "all" },
            { label: "Grievances", value: "grievance" },
            { label: "Clusters", value: "cluster" },
            { label: "Models", value: "model" },
            { label: "Officers", value: "officer" },
          ]}
        />
      </div>

      <div className="bg-white rounded-lg border border-slate-200 overflow-hidden shadow-subtle">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-mono text-[11px] uppercase">
                <th className="py-3 px-4 font-semibold">Timestamp</th>
                <th className="py-3 px-4 font-semibold">Action Type</th>
                <th className="py-3 px-4 font-semibold">Entity Target</th>
                <th className="py-3 px-4 font-semibold">Actor / Role</th>
                <th className="py-3 px-4 font-semibold">Details / Rationale</th>
                <th className="py-3 px-4 font-semibold text-right">IP Origin</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-sans">
              {filtered.map((log) => (
                <tr key={log.id} className="hover:bg-slate-50/70 transition-colors">
                  <td className="py-3 px-4 whitespace-nowrap font-mono text-slate-500 text-[11px]">
                    {formatDate(log.timestamp, { hour: "numeric", minute: "numeric" })}
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap font-mono font-bold text-blue-700">
                    {log.action}
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap font-mono font-semibold text-slate-800">
                    {log.entityId} <span className="text-[10px] text-slate-400">({log.entityType})</span>
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap">
                    <span className="font-semibold text-slate-900 block">{log.performedBy}</span>
                    <span className="text-[10px] text-slate-400 uppercase font-mono">{log.userRole}</span>
                  </td>
                  <td className="py-3 px-4 text-slate-700 max-w-md leading-relaxed">
                    {log.details}
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap font-mono text-slate-400 text-right text-[10px]">
                    {log.ipAddress}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

import React from "react";
import { Link } from "react-router-dom";
import { MOCK_DEPARTMENTS, MOCK_OFFICERS } from "@/mocks/mockData";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { MetricCard } from "@/components/common/MetricCard";
import { ChartCard } from "@/components/common/ChartCard";
import {
  Users,
  Building,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Sliders,
  TrendingUp,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { cn } from "@/lib/utils";

export default function WorkloadManagementPage() {
  const chartData = MOCK_DEPARTMENTS.map((d) => ({
    name: d.code,
    active: d.activeGrievances,
    officers: d.officerCount,
    avgDays: d.avgResolutionDays,
  }));

  return (
    <div className="space-y-6">
      <PageHeader
        title="Department Workload & Staffing Intelligence"
        subtitle="Cross-departmental capacity utilization, active backlog saturation, and officer assignment distribution across city zones."
        breadcrumbs={[
          { label: "Admin Portal", href: "/admin" },
          { label: "Workload Management", active: true },
        ]}
        actions={
          <Link
            to="/admin/simulator"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-subtle transition-colors"
          >
            <Sliders className="w-3.5 h-3.5" />
            Launch Workload Simulator
          </Link>
        }
      />

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Field Officers"
          value={MOCK_OFFICERS.length * 15}
          subtitle="214 active across 64 wards"
          icon={Users}
        />
        <MetricCard
          title="Active Municipal Backlog"
          value="1,127 Cases"
          subtitle="Mean per officer: 5.2 cases"
          icon={Clock}
        />
        <MetricCard
          title="Bottleneck Department"
          value="Water Supply"
          subtitle="312 active cases (Overloaded)"
          icon={AlertTriangle}
          className="border-red-300 bg-red-50/20"
          isPositive={false}
        />
        <MetricCard
          title="Optimal Department"
          value="Solid Waste"
          subtitle="94.8% SLA compliance rate"
          icon={CheckCircle2}
          isPositive={true}
        />
      </div>

      {/* Workload Comparison Chart */}
      <ChartCard
        title="Department Backlog vs Field Officer Distribution"
        subtitle="Comparing active complaints load relative to dedicated officer workforce"
        badge="Resource Allocation"
      >
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} />
              <Tooltip />
              <Legend iconSize={8} wrapperStyle={{ fontSize: "11px" }} />
              <Bar dataKey="active" name="Active Complaints" fill="#2563eb" radius={[4, 4, 0, 0]} />
              <Bar dataKey="officers" name="Officer Headcount" fill="#94a3b8" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </ChartCard>

      {/* Department Summary Table */}
      <div className="bg-white rounded-lg border border-slate-200 overflow-hidden shadow-subtle space-y-3 p-5">
        <h3 className="text-sm font-bold text-slate-900">
          Departmental Operational Health & SLA Scorecard
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-mono text-[11px] uppercase">
                <th className="py-3 px-3.5 font-semibold">Department</th>
                <th className="py-3 px-3.5 font-semibold">Department Head</th>
                <th className="py-3 px-3.5 font-semibold">Officers</th>
                <th className="py-3 px-3.5 font-semibold">Active Caseload</th>
                <th className="py-3 px-3.5 font-semibold">Avg Resolution</th>
                <th className="py-3 px-3.5 font-semibold">SLA Compliance</th>
                <th className="py-3 px-3.5 font-semibold">Load Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {MOCK_DEPARTMENTS.map((d) => (
                <tr key={d.id} className="hover:bg-slate-50/70 transition-colors">
                  <td className="py-3 px-3.5 font-bold text-slate-900">{d.name}</td>
                  <td className="py-3 px-3.5 text-slate-700">{d.head}</td>
                  <td className="py-3 px-3.5 font-mono text-slate-700">{d.officerCount} staff</td>
                  <td className="py-3 px-3.5 font-mono font-bold text-blue-600">{d.activeGrievances} cases</td>
                  <td className="py-3 px-3.5 font-mono text-slate-700">{d.avgResolutionDays} days</td>
                  <td className="py-3 px-3.5 font-mono font-bold text-emerald-700">{d.slaComplianceRate}%</td>
                  <td className="py-3 px-3.5">
                    <span
                      className={cn(
                        "px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase",
                        d.workloadStatus === "critical_overload"
                          ? "bg-red-50 text-red-700 border border-red-200"
                          : d.workloadStatus === "heavy"
                          ? "bg-amber-50 text-amber-700 border border-amber-200"
                          : "bg-emerald-50 text-emerald-700 border border-emerald-200"
                      )}
                    >
                      {d.workloadStatus.replace("_", " ")}
                    </span>
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

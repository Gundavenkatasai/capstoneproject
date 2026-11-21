import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { grievanceService } from "@/services/grievanceService";
import { earlyWarningService } from "@/services/earlyWarningService";
import { Grievance, Hotspot } from "@/types";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { MetricCard } from "@/components/common/MetricCard";
import { ChartCard } from "@/components/common/ChartCard";
import { StatusBadge } from "@/components/common/StatusBadge";
import { PriorityBadge } from "@/components/common/PriorityBadge";
import { FilterDropdown } from "@/components/common/SearchInput";
import { LoadingSkeleton } from "@/components/common/EmptyState";
import { formatDate } from "@/lib/utils";
import {
  FileText,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Copy,
  Radio,
  TrendingUp,
  ShieldAlert,
  ArrowRight,
  Sparkles,
  BarChart3,
  Layers,
  MapPin,
  ChevronRight,
} from "lucide-react";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

export default function AdminIntelligenceDashboardPage() {
  const [grievances, setGrievances] = useState<Grievance[]>([]);
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [deptFilter, setDeptFilter] = useState("all");
  const [zoneFilter, setZoneFilter] = useState("all");
  const [timeRange, setTimeRange] = useState("30d");

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      const [gData, hData] = await Promise.all([
        grievanceService.getAll({
          departmentId: deptFilter !== "all" ? deptFilter : undefined,
        }),
        earlyWarningService.getHotspots(),
      ]);
      setGrievances(gData);
      setHotspots(hData);
      setLoading(false);
    }
    loadData();
  }, [deptFilter, zoneFilter, timeRange]);

  // Derived KPI computations
  const total = grievances.length;
  const pending = grievances.filter((g) => ["submitted", "analyzed", "assigned", "in_progress"].includes(g.status)).length;
  const resolved = grievances.filter((g) => ["closed", "citizen_verified"].includes(g.status)).length;
  const highPriority = grievances.filter((g) => g.priority === "critical" || g.priority === "high").length;
  const duplicates = grievances.filter((g) => (g.duplicateProbability || 0) > 0.6).length;
  const avgDays = (grievances.reduce((acc, g) => acc + (g.predictedDurationDays || 3), 0) / (total || 1)).toFixed(1);
  const slaBreaches = grievances.filter((g) => g.slaBreached || g.slaBreachRisk === "critical").length;
  const emergingIssues = hotspots.filter((h) => h.trend === "increasing").length;

  // Chart data
  const submissionTrendData = [
    { date: "Nov 01", incoming: 42, resolved: 38 },
    { date: "Nov 05", incoming: 58, resolved: 49 },
    { date: "Nov 09", incoming: 64, resolved: 56 },
    { date: "Nov 13", incoming: 78, resolved: 65 },
    { date: "Nov 16", incoming: 92, resolved: 74 },
    { date: "Nov 19", incoming: 85, resolved: 81 },
  ];

  const deptPerformanceData = [
    { name: "Water Supply", active: 312, resolved: 280, sla: 79.5 },
    { name: "Solid Waste", active: 245, resolved: 310, sla: 94.8 },
    { name: "Street Lights", active: 198, resolved: 185, sla: 88.2 },
    { name: "PWD Roads", active: 184, resolved: 195, sla: 91.2 },
    { name: "Public Health", active: 112, resolved: 120, sla: 96.1 },
    { name: "Horticulture", active: 76, resolved: 80, sla: 90.0 },
  ];

  const categoryDistributionData = [
    { name: "Water & Sewerage", value: 38, color: "#0D9488" },
    { name: "Solid Waste", value: 26, color: "#D97706" },
    { name: "Electricity", value: 18, color: "#8B5CF6" },
    { name: "Roads (PWD)", value: 12, color: "#1E6BE6" },
    { name: "Other Civic", value: 6, color: "#64748B" },
  ];

  const highRiskQueue = grievances
    .filter((g) => g.priority === "critical" || g.slaBreached || g.slaBreachRisk === "critical")
    .slice(0, 4);

  return (
    <div className="space-y-6">
      {/* Header and Filter Row */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-5 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900">
              Grievance Intelligence Overview
            </h1>
            <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
              APEX COMMAND
            </span>
          </div>
          <p className="mt-1 text-xs sm:text-sm text-slate-500">
            Real-time multi-department intelligence, spatial early warning radar, and automated SLA risk prediction.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
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
            label="Zone"
            value={zoneFilter}
            onChange={setZoneFilter}
            options={[
              { label: "All Zones", value: "all" },
              { label: "South Zone", value: "south" },
              { label: "Central Zone", value: "central" },
              { label: "West Zone", value: "west" },
              { label: "East Zone", value: "east" },
            ]}
          />
          <FilterDropdown
            label="Period"
            value={timeRange}
            onChange={setTimeRange}
            options={[
              { label: "Last 7 Days", value: "7d" },
              { label: "Last 30 Days", value: "30d" },
              { label: "This Quarter", value: "90d" },
            ]}
          />
        </div>
      </div>

      {/* 8 KPI Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
        <MetricCard
          title="Total Caseload"
          value={total}
          subtitle="All complaints"
          icon={FileText}
        />
        <MetricCard
          title="Pending Queue"
          value={pending}
          subtitle="In pipeline"
          icon={Clock}
          changeType="neutral"
        />
        <MetricCard
          title="Resolved"
          value={resolved}
          subtitle="Closed & verified"
          icon={CheckCircle2}
          isPositive={true}
        />
        <MetricCard
          title="High Priority"
          value={highPriority}
          subtitle="Critical triage"
          icon={AlertTriangle}
          className="border-amber-300 bg-amber-50/20"
        />
        <MetricCard
          title="Duplicates"
          value={duplicates}
          subtitle="Semantic matches"
          icon={Copy}
          badge="AI Cluster"
        />
        <MetricCard
          title="Mean Days"
          value={`${avgDays}d`}
          subtitle="Resolution velocity"
          icon={TrendingUp}
        />
        <MetricCard
          title="SLA Breaches"
          value={slaBreaches}
          subtitle="Flagged by AI"
          icon={ShieldAlert}
          className={slaBreaches > 0 ? "border-red-300 bg-red-50/20" : ""}
          isPositive={false}
        />
        <MetricCard
          title="Radar Hotspots"
          value={emergingIssues}
          subtitle="Surging clusters"
          icon={Radio}
          className="border-blue-300 bg-blue-50/20"
        />
      </div>

      {/* AI OPERATIONAL INSIGHTS BANNER */}
      <div className="p-4 rounded-lg bg-gradient-to-r from-blue-900 via-indigo-900 to-navy-950 text-white shadow-elevated flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 rounded-full bg-blue-500/20 border border-blue-400/40 flex items-center justify-center flex-shrink-0 mt-0.5">
            <Sparkles className="w-4 h-4 text-blue-300" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-xs uppercase tracking-wider text-blue-300 font-mono">
                AI Operational Intelligence Alert
              </span>
              <span className="text-[10px] bg-red-500/80 text-white font-mono px-1.5 py-0.2 rounded font-bold">
                HIGH ATTENTION
              </span>
            </div>
            <p className="text-xs text-slate-200 mt-1 leading-relaxed max-w-3xl">
              Water Supply & Sewerage Board is operating at <strong>118% capacity</strong> due to Feeder Pipe rupture in Ward 14. Semantic duplicate consolidation detected 4 related complaints, and Workload Simulator recommends reallocating 3 PWD excavation backhoes to avert 8 impending SLA breaches.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          <Link
            to="/admin/early-warning"
            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-semibold shadow-subtle transition-colors"
          >
            Open Radar Map
          </Link>
          <Link
            to="/admin/simulator"
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 rounded text-xs font-semibold transition-colors"
          >
            Launch Simulator
          </Link>
        </div>
      </div>

      {/* Primary Analytics Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <ChartCard
          title="Grievance Submission & Resolution Trend"
          subtitle="Incoming citizen complaints vs successfully resolved cases"
          badge="Daily Telemetry"
          className="lg:col-span-2"
        >
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={submissionTrendData}>
                <defs>
                  <linearGradient id="colorIncoming" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2563eb" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorResolved" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0d9488" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#0d9488" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="date" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="incoming"
                  name="Incoming Submissions"
                  stroke="#2563eb"
                  fillOpacity={1}
                  fill="url(#colorIncoming)"
                  strokeWidth={2}
                />
                <Area
                  type="monotone"
                  dataKey="resolved"
                  name="Resolved"
                  stroke="#0d9488"
                  fillOpacity={1}
                  fill="url(#colorResolved)"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        <ChartCard
          title="Complaint Distribution by Category"
          subtitle="Semantic classification breakdown across urban services"
          badge="NLP Model v4.2"
        >
          <div className="h-64 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={categoryDistributionData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={78}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {categoryDistributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend iconSize={8} wrapperStyle={{ fontSize: "11px" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
      </div>

      {/* Secondary Row: Department Workload & Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard
          title="Department Active Load vs Capacity"
          subtitle="Active open complaints by department with SLA compliance %"
          badge="Live Backlog"
        >
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={deptPerformanceData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="name" stroke="#64748b" fontSize={10} interval={0} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip />
                <Bar dataKey="active" name="Active Backlog" fill="#2563eb" radius={[4, 4, 0, 0]} />
                <Bar dataKey="resolved" name="Resolved MTD" fill="#94a3b8" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        {/* High-Risk Queue & Emerging Hotspots */}
        <div className="bg-white rounded-lg border border-slate-200 overflow-hidden shadow-subtle flex flex-col justify-between">
          <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Critical SLA Risk Queue</h3>
              <p className="text-xs text-slate-500">Cases requiring executive intervention</p>
            </div>
            <Link to="/admin/predictions" className="text-xs text-blue-600 hover:text-blue-800 font-semibold">
              View SLA Forecaster →
            </Link>
          </div>

          <div className="divide-y divide-slate-100 p-2">
            {highRiskQueue.map((g) => (
              <div
                key={g.id}
                className="p-3 hover:bg-slate-50/70 transition-colors flex items-center justify-between gap-3 text-xs"
              >
                <div className="min-w-0">
                  <div className="flex items-center gap-1.5 mb-0.5">
                    <span className="font-mono font-bold text-slate-800">{g.id}</span>
                    <PriorityBadge priority={g.priority} className="py-0 px-1 text-[9px]" />
                    {g.slaBreached && (
                      <span className="text-[9px] font-mono px-1 rounded bg-red-100 text-red-700 font-bold">
                        BREACHED
                      </span>
                    )}
                  </div>
                  <p className="font-semibold text-slate-900 truncate">{g.title}</p>
                  <p className="text-[11px] text-slate-400 truncate">{g.departmentName} • {g.location.ward}</p>
                </div>

                <Link
                  to={`/admin/grievances/${g.id}`}
                  className="px-2.5 py-1 text-[11px] bg-slate-100 hover:bg-blue-50 text-slate-700 hover:text-blue-700 font-semibold rounded border border-slate-200 flex-shrink-0 transition-colors"
                >
                  Manage
                </Link>
              </div>
            ))}
          </div>

          <div className="p-3 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
            <span>{slaBreaches} total high-risk cases identified</span>
            <Link to="/admin/grievances?filter=priority" className="font-semibold text-blue-600 hover:underline">
              Inspect Full Queue →
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

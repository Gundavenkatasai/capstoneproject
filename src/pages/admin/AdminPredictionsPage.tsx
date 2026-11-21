import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { predictionService, SlaBreachRiskItem, DepartmentForecast } from "@/services/predictionService";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { MetricCard } from "@/components/common/MetricCard";
import { ChartCard } from "@/components/common/ChartCard";
import { LoadingSkeleton } from "@/components/common/EmptyState";
import {
  TrendingUp,
  Clock,
  ShieldAlert,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  BarChart3,
  Building,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  Legend,
} from "recharts";
import { cn } from "@/lib/utils";

export default function PredictiveAnalyticsPage() {
  const [slaQueue, setSlaQueue] = useState<SlaBreachRiskItem[]>([]);
  const [deptForecast, setDeptForecast] = useState<DepartmentForecast[]>([]);
  const [accuracyData, setAccuracyData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const [sData, dData, aData] = await Promise.all([
        predictionService.getSlaBreachQueue(),
        predictionService.getDepartmentForecast(),
        predictionService.getResolutionTimeAccuracy(),
      ]);
      setSlaQueue(sData);
      setDeptForecast(dData);
      setAccuracyData(aData);
      setLoading(false);
    }
    load();
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Predictive Analytics & SLA Forecaster"
        subtitle="Gradient-boosted decision support models predicting resolution horizons, proactive SLA breach risks, and 7-day departmental workload surges."
        breadcrumbs={[
          { label: "Admin Portal", href: "/admin" },
          { label: "Predictive Analytics", active: true },
        ]}
        badge="LightGBM v2.4 + XGBoost"
      />

      {/* KPI Highlights */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Predicted SLA Breaches"
          value={slaQueue.filter((s) => s.riskTier === "critical" || s.riskTier === "high").length}
          subtitle="Flagged for proactive intervention"
          icon={ShieldAlert}
          className="border-red-300 bg-red-50/20"
          isPositive={false}
        />
        <MetricCard
          title="Overall Model MAE"
          value="0.68 Days"
          subtitle="Mean absolute duration error"
          icon={Clock}
          badge="High Fidelity"
        />
        <MetricCard
          title="Forecast Overload Depts"
          value="1 Department"
          subtitle="Water Supply (118% capacity)"
          icon={AlertTriangle}
          className="border-amber-300 bg-amber-50/20"
        />
        <MetricCard
          title="PR-AUC Accuracy"
          value="0.904"
          subtitle="Precision-Recall Area Under Curve"
          icon={TrendingUp}
          isPositive={true}
        />
      </div>

      {/* SECTION A: RESOLUTION TIME ACCURACY & COMPARISON */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard
          title="Actual vs Predicted Resolution Duration (Days)"
          subtitle="Category-wise model calibration on benchmarked historical cases"
          badge="Regression Metric"
        >
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={accuracyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="category" stroke="#64748b" fontSize={11} interval={0} />
                <YAxis stroke="#64748b" fontSize={11} unit="d" />
                <Tooltip />
                <Legend iconSize={8} wrapperStyle={{ fontSize: "11px" }} />
                <Bar dataKey="actualAvgDays" name="Actual Mean (Days)" fill="#94a3b8" radius={[4, 4, 0, 0]} />
                <Bar dataKey="predictedAvgDays" name="Predicted Mean (Days)" fill="#2563eb" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        {/* SECTION C: 7-DAY DEPARTMENT CAPACITY UTILIZATION */}
        <ChartCard
          title="Projected 7-Day Capacity Utilization (%)"
          subtitle="Anticipated workload pressure relative to staffing capacity"
          badge="Capacity Forecaster"
        >
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={deptForecast}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="department" stroke="#64748b" fontSize={10} interval={0} tickFormatter={(v) => v.split(" ")[0]} />
                <YAxis stroke="#64748b" fontSize={11} unit="%" />
                <Tooltip />
                <Bar
                  dataKey="capacityUtilizationPct"
                  name="Capacity Utilization %"
                  fill="#1e40af"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
      </div>

      {/* SECTION B: PROACTIVE SLA BREACH PREDICTION QUEUE */}
      <div className="bg-white rounded-lg border border-slate-200 overflow-hidden shadow-subtle space-y-4 p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-100">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-slate-900">
                SLA Breach Risk Queue (Prioritized by Failure Probability)
              </h3>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-red-50 text-red-700 font-bold border border-red-200">
                Early Intervention Queue
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Complaints flagged with high probability of missing the Citizen Charter SLA deadline
            </p>
          </div>
        </div>

        {loading ? (
          <LoadingSkeleton type="table" count={4} />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-mono text-[11px] uppercase">
                  <th className="py-3 px-3.5 font-semibold">Complaint ID</th>
                  <th className="py-3 px-3.5 font-semibold">Department</th>
                  <th className="py-3 px-3.5 font-semibold">Breach Probability</th>
                  <th className="py-3 px-3.5 font-semibold">Risk Tier</th>
                  <th className="py-3 px-3.5 font-semibold">Time Remaining</th>
                  <th className="py-3 px-3.5 font-semibold">Contributing Factors</th>
                  <th className="py-3 px-3.5 font-semibold text-right">Recommended Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {slaQueue.map((item) => (
                  <tr key={item.grievanceId} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 px-3.5 font-mono font-bold text-slate-900 whitespace-nowrap">
                      <Link
                        to={`/admin/grievances/${item.grievanceId}`}
                        className="text-blue-600 hover:underline"
                      >
                        {item.grievanceId}
                      </Link>
                    </td>
                    <td className="py-3 px-3.5 font-medium text-slate-800 whitespace-nowrap">
                      {item.department}
                    </td>
                    <td className="py-3 px-3.5 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-slate-200 h-1.5 rounded-full overflow-hidden">
                          <div
                            className={cn(
                              "h-full rounded-full",
                              item.breachProbability > 0.8
                                ? "bg-red-500"
                                : item.breachProbability > 0.5
                                ? "bg-amber-500"
                                : "bg-blue-500"
                            )}
                            style={{ width: `${Math.round(item.breachProbability * 100)}%` }}
                          />
                        </div>
                        <span className="font-mono font-bold text-slate-900">
                          {Math.round(item.breachProbability * 100)}%
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-3.5 whitespace-nowrap">
                      <span
                        className={cn(
                          "px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase",
                          item.riskTier === "critical"
                            ? "bg-red-50 text-red-700 border border-red-200"
                            : item.riskTier === "high"
                            ? "bg-amber-50 text-amber-700 border border-amber-200"
                            : "bg-blue-50 text-blue-700 border border-blue-200"
                        )}
                      >
                        {item.riskTier}
                      </span>
                    </td>
                    <td className="py-3 px-3.5 whitespace-nowrap font-mono">
                      {item.hoursRemaining < 0 ? (
                        <span className="text-red-700 font-bold bg-red-50 px-1.5 py-0.5 rounded border border-red-200">
                          Breached ({Math.abs(item.hoursRemaining)}h ago)
                        </span>
                      ) : (
                        <span className="text-slate-700">{item.hoursRemaining} Hours left</span>
                      )}
                    </td>
                    <td className="py-3 px-3.5 max-w-xs text-slate-600">
                      <ul className="list-disc list-inside space-y-0.5 text-[11px]">
                        {item.contributingFactors.map((f, i) => (
                          <li key={i} className="truncate">
                            {f}
                          </li>
                        ))}
                      </ul>
                    </td>
                    <td className="py-3 px-3.5 whitespace-nowrap text-right">
                      <span className="text-[11px] font-semibold text-slate-700 bg-slate-100 px-2 py-1 rounded border border-slate-200 block truncate max-w-[200px]">
                        {item.recommendedAction}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

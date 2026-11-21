import React, { useState, useEffect } from "react";
import { simulatorService } from "@/services/simulatorService";
import { SimulatorInput, SimulatorResult } from "@/types";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { MetricCard } from "@/components/common/MetricCard";
import { ChartCard } from "@/components/common/ChartCard";
import { LoadingSkeleton } from "@/components/common/EmptyState";
import {
  Sliders,
  Sparkles,
  TrendingUp,
  Clock,
  ShieldCheck,
  RotateCcw,
  Info,
  CheckCircle2,
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

export default function CounterfactualWorkloadSimulatorPage() {
  const [inputs, setInputs] = useState<SimulatorInput>({
    additionalOfficers: 15,
    departmentCapacityMultiplier: 1.25,
    workloadRedistributionPct: 20,
    routingWeightAIFactor: 0.85,
    escalationThresholdHours: 36,
  });

  const [result, setResult] = useState<SimulatorResult | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function runSim() {
      setLoading(true);
      const res = await simulatorService.runSimulation(inputs);
      setResult(res);
      setLoading(false);
    }
    runSim();
  }, [inputs]);

  const handleReset = () => {
    setInputs({
      additionalOfficers: 0,
      departmentCapacityMultiplier: 1.0,
      workloadRedistributionPct: 0,
      routingWeightAIFactor: 0.5,
      escalationThresholdHours: 48,
    });
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Counterfactual Workload Simulator"
        subtitle="Interactive policy testbench modeling how staffing injections, inter-departmental load shedding, and AI routing weights alter backlog clearance velocity and SLA breach risks."
        breadcrumbs={[
          { label: "Admin Portal", href: "/admin" },
          { label: "Workload Simulator", active: true },
        ]}
        actions={
          <button
            onClick={handleReset}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 text-xs font-semibold rounded shadow-subtle transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Reset to Baseline
          </button>
        }
        badge="Counterfactual Engine"
      />

      {/* Simulator Notice */}
      <div className="p-3.5 bg-purple-50/70 border border-purple-200 rounded-md flex items-start gap-3 text-xs text-purple-950">
        <Sparkles className="w-4 h-4 text-purple-600 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">What-If Counterfactual Sandbox Notice</span>
          <p className="mt-0.5 text-purple-800 leading-relaxed">
            All projections represent stochastic queue simulation models calibrated against historical municipal throughput. Changing input levers dynamically computes expected systemic equilibrium without altering live production databases.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Interactive Levers / Sliders (5 cols) */}
        <div className="lg:col-span-5 bg-white rounded-lg border border-slate-200 p-5 shadow-subtle space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider font-mono flex items-center gap-1.5">
              <Sliders className="w-4 h-4 text-blue-600" />
              Policy Levers & Staffing Inputs
            </h3>
            <span className="text-[10px] text-slate-400 font-mono">Live Recalculation</span>
          </div>

          {/* Lever 1: Additional Officers */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-slate-800">Additional Field Officers</span>
              <span className="font-mono font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                +{inputs.additionalOfficers} Officers
              </span>
            </div>
            <input
              type="range"
              min={0}
              max={50}
              step={1}
              value={inputs.additionalOfficers}
              onChange={(e) =>
                setInputs({ ...inputs, additionalOfficers: Number(e.target.value) })
              }
              className="w-full accent-blue-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>0 (Baseline)</span>
              <span>+25</span>
              <span>+50 Officers</span>
            </div>
          </div>

          {/* Lever 2: Capacity Multiplier */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-slate-800">Department Operational Efficiency</span>
              <span className="font-mono font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                {inputs.departmentCapacityMultiplier}x Throughput
              </span>
            </div>
            <input
              type="range"
              min={1.0}
              max={2.0}
              step={0.05}
              value={inputs.departmentCapacityMultiplier}
              onChange={(e) =>
                setInputs({ ...inputs, departmentCapacityMultiplier: Number(e.target.value) })
              }
              className="w-full accent-blue-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>1.0x (Standard)</span>
              <span>1.5x</span>
              <span>2.0x (Double Speed)</span>
            </div>
          </div>

          {/* Lever 3: Workload Redistribution */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-slate-800">Inter-Departmental Load Redistribution</span>
              <span className="font-mono font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                {inputs.workloadRedistributionPct}% Shared
              </span>
            </div>
            <input
              type="range"
              min={0}
              max={40}
              step={5}
              value={inputs.workloadRedistributionPct}
              onChange={(e) =>
                setInputs({ ...inputs, workloadRedistributionPct: Number(e.target.value) })
              }
              className="w-full accent-blue-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>0% (Siloed)</span>
              <span>20%</span>
              <span>40% (High Mutual Aid)</span>
            </div>
          </div>

          {/* Lever 4: AI Routing Factor */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-slate-800">AI Autonomous Routing Weight</span>
              <span className="font-mono font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                {Math.round(inputs.routingWeightAIFactor * 100)}% Confidence
              </span>
            </div>
            <input
              type="range"
              min={0.5}
              max={1.0}
              step={0.05}
              value={inputs.routingWeightAIFactor}
              onChange={(e) =>
                setInputs({ ...inputs, routingWeightAIFactor: Number(e.target.value) })
              }
              className="w-full accent-blue-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>50% (Manual Triage)</span>
              <span>75%</span>
              <span>100% (Full Auto)</span>
            </div>
          </div>

          {/* Lever 5: Escalation Threshold */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-slate-800">Supervisor Escalation Horizon</span>
              <span className="font-mono font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                {inputs.escalationThresholdHours} Hours
              </span>
            </div>
            <input
              type="range"
              min={12}
              max={72}
              step={6}
              value={inputs.escalationThresholdHours}
              onChange={(e) =>
                setInputs({ ...inputs, escalationThresholdHours: Number(e.target.value) })
              }
              className="w-full accent-blue-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>12h (Aggressive)</span>
              <span>48h</span>
              <span>72h (Relaxed)</span>
            </div>
          </div>
        </div>

        {/* Right Column: Simulated Outcomes & Before-After Comparison (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Outcome Metric Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-subtle">
              <span className="text-[10px] font-mono text-slate-400 uppercase block">Active Backlog</span>
              <div className="mt-1 flex items-baseline gap-2">
                <span className="text-xl font-bold text-slate-900 font-mono">
                  {result?.simulatedBacklog || 1127}
                </span>
                <span className="text-xs text-emerald-600 font-bold font-mono">
                  ↓ {result ? result.currentBacklog - result.simulatedBacklog : 0} cases
                </span>
              </div>
              <span className="text-[10px] text-slate-400">Baseline: 1,127 cases</span>
            </div>

            <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-subtle">
              <span className="text-[10px] font-mono text-slate-400 uppercase block">Avg Resolution Speed</span>
              <div className="mt-1 flex items-baseline gap-2">
                <span className="text-xl font-bold text-slate-900 font-mono">
                  {result?.simulatedAvgResolutionDays || 4.3}d
                </span>
                <span className="text-xs text-emerald-600 font-bold font-mono">
                  ↓ {(4.3 - (result?.simulatedAvgResolutionDays || 4.3)).toFixed(1)}d faster
                </span>
              </div>
              <span className="text-[10px] text-slate-400">Baseline: 4.3 days</span>
            </div>

            <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-subtle">
              <span className="text-[10px] font-mono text-slate-400 uppercase block">Projected SLA Breach Rate</span>
              <div className="mt-1 flex items-baseline gap-2">
                <span className="text-xl font-bold text-slate-900 font-mono">
                  {result?.simulatedSlaBreachRate || 12.8}%
                </span>
                <span className="text-xs text-emerald-600 font-bold font-mono">
                  ↓ {(12.8 - (result?.simulatedSlaBreachRate || 12.8)).toFixed(1)}% pts
                </span>
              </div>
              <span className="text-[10px] text-slate-400">Baseline: 12.8% breaches</span>
            </div>
          </div>

          {/* Executive Scenario Summary */}
          {result && (
            <div className="p-4 bg-emerald-50/70 border border-emerald-200 rounded-lg text-xs text-emerald-950 space-y-1">
              <span className="font-bold block flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                Simulated Policy Impact Assessment:
              </span>
              <p className="text-emerald-900 leading-relaxed">{result.summary}</p>
            </div>
          )}

          {/* Before-and-After Department Comparison Chart */}
          <ChartCard
            title="Department Caseload: Baseline vs Simulated Projection"
            subtitle="Evaluating how policy levers relieve bottlenecked municipal departments"
            badge="Before vs After"
          >
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={result?.departmentWorkload || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="department" stroke="#64748b" fontSize={10} interval={0} tickFormatter={(v) => v.split(" ")[0]} />
                  <YAxis stroke="#64748b" fontSize={11} />
                  <Tooltip />
                  <Legend iconSize={8} wrapperStyle={{ fontSize: "11px" }} />
                  <Bar dataKey="currentLoad" name="Current Baseline Backlog" fill="#94a3b8" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="projectedLoad" name="Simulated Projected Load" fill="#2563eb" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="capacity" name="Department Capacity" fill="#10b981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>
        </div>
      </div>
    </div>
  );
}

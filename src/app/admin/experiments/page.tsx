"use client";

import React from "react";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { MetricCard } from "@/components/common/MetricCard";
import { ChartCard } from "@/components/common/ChartCard";
import { FlaskConical, CheckCircle2, TrendingUp, Sparkles } from "lucide-react";
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

export default function ExperimentResultsPage() {
  const modelComparisons = [
    {
      model: "CivicDeBERTa-v4.2 (Our Final)",
      accuracy: 94.8,
      macroF1: 93.9,
      latencyMs: 42,
      paramsM: 125,
      status: "Production Candidate",
      isBest: true,
    },
    {
      model: "RoBERTa-Base (Fine-Tuned)",
      accuracy: 91.2,
      macroF1: 90.1,
      latencyMs: 38,
      paramsM: 110,
      status: "Archived Benchmark",
      isBest: false,
    },
    {
      model: "mBERT (Multilingual Base)",
      accuracy: 88.5,
      macroF1: 86.8,
      latencyMs: 45,
      paramsM: 178,
      status: "Archived Benchmark",
      isBest: false,
    },
    {
      model: "TF-IDF + XGBoost Baseline",
      accuracy: 81.4,
      macroF1: 78.2,
      latencyMs: 8,
      paramsM: 2,
      status: "Baseline Control",
      isBest: false,
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Scientific Experiments & Architecture Benchmarking"
        subtitle="Controlled comparative evaluations across transformer architectures and classical baselines for grievance classification."
        breadcrumbs={[
          { label: "Admin Portal", href: "/admin" },
          { label: "Experiment Results", active: true },
        ]}
        badge="4 Formal Trials"
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Leading Model"
          value="DeBERTa-v4.2"
          subtitle="Top performer across all 6 departments"
          icon={Sparkles}
          badge="Winner"
        />
        <MetricCard
          title="Accuracy Improvement"
          value="+13.4%"
          subtitle="Gain over classical TF-IDF baseline"
          icon={TrendingUp}
          isPositive={true}
        />
        <MetricCard
          title="Inference Latency"
          value="42 ms"
          subtitle="Real-time edge serving latency"
          icon={FlaskConical}
        />
        <MetricCard
          title="Model Parameter Size"
          value="125M"
          subtitle="Optimized for CPU & GPU inference"
          icon={CheckCircle2}
        />
      </div>

      <ChartCard
        title="Comparative Model Accuracy & Macro F1"
        subtitle="Evaluating deep contextual transformers against baseline classification techniques"
        badge="Holdout Benchmark"
      >
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={modelComparisons}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="model" stroke="#64748b" fontSize={10} interval={0} tickFormatter={(m) => m.split(" ")[0]} />
              <YAxis stroke="#64748b" fontSize={11} domain={[70, 100]} unit="%" />
              <Tooltip />
              <Legend iconSize={8} wrapperStyle={{ fontSize: "11px" }} />
              <Bar dataKey="accuracy" name="Accuracy %" fill="#2563eb" radius={[4, 4, 0, 0]} />
              <Bar dataKey="macroF1" name="Macro F1 %" fill="#0d9488" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </ChartCard>

      {/* Detailed Experiment Table */}
      <div className="bg-white rounded-lg border border-slate-200 overflow-hidden shadow-subtle p-5 space-y-3">
        <h3 className="text-sm font-bold text-slate-900">
          Formal Experiment Log & Model Specifications
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-mono text-[11px] uppercase">
                <th className="py-3 px-3.5 font-semibold">Model Architecture</th>
                <th className="py-3 px-3.5 font-semibold">Parameters</th>
                <th className="py-3 px-3.5 font-semibold">Inference Latency</th>
                <th className="py-3 px-3.5 font-semibold">Accuracy</th>
                <th className="py-3 px-3.5 font-semibold">Macro F1</th>
                <th className="py-3 px-3.5 font-semibold">Evaluation Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {modelComparisons.map((c, i) => (
                <tr key={i} className={`hover:bg-slate-50/70 transition-colors ${c.isBest ? "bg-blue-50/20" : ""}`}>
                  <td className="py-3 px-3.5 font-bold text-slate-900">
                    {c.model} {c.isBest && <span className="text-[10px] font-mono text-blue-600 ml-1">★ BEST</span>}
                  </td>
                  <td className="py-3 px-3.5 font-mono text-slate-700">{c.paramsM}M</td>
                  <td className="py-3 px-3.5 font-mono text-slate-700">{c.latencyMs} ms</td>
                  <td className="py-3 px-3.5 font-mono font-bold text-slate-900">{c.accuracy}%</td>
                  <td className="py-3 px-3.5 font-mono font-bold text-emerald-700">{c.macroF1}%</td>
                  <td className="py-3 px-3.5 font-semibold text-slate-700">{c.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

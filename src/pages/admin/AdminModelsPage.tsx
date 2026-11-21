import React from "react";
import { MOCK_RESEARCH_METRICS } from "@/mocks/mockData";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { MetricCard } from "@/components/common/MetricCard";
import { ChartCard } from "@/components/common/ChartCard";
import { Database, BrainCircuit, CheckCircle2, Info, Sparkles, Layers } from "lucide-react";

export default function ModelPerformancePage() {
  const m = MOCK_RESEARCH_METRICS;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Model Performance & Scientific Benchmarks"
        subtitle="Evaluation metrics, confusion matrices, and loss curves across the multimodal CivicMind AI architecture."
        breadcrumbs={[
          { label: "Admin Portal", href: "/admin" },
          { label: "Model Performance", active: true },
        ]}
        badge="Evaluated on 142.5K Records"
      />

      <div className="p-3.5 bg-slate-100 border border-slate-200 rounded-md flex items-start gap-3 text-xs text-slate-700">
        <Info className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold text-slate-900">Research Benchmark Notice</span>
          <p className="mt-0.5 text-slate-600 leading-relaxed">
            Metrics below represent cross-validated holdout evaluations across our test corpus. All results conform to reproducible scientific reporting standards.
          </p>
        </div>
      </div>

      {/* CLASSIFICATION METRICS */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 font-mono flex items-center gap-1.5">
            <BrainCircuit className="w-4 h-4 text-blue-600" />
            1. Multilingual Semantic Triage Model (DeBERTa-v4.2-Civic)
          </h3>
          <span className="text-[10px] font-mono text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
            Status: Production Active
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <MetricCard title="Overall Accuracy" value={`${m.classification.accuracy}%`} subtitle="Top-1 exact match" />
          <MetricCard title="Macro Precision" value={`${m.classification.precision}%`} subtitle="Unweighted mean" />
          <MetricCard title="Macro Recall" value={`${m.classification.recall}%`} subtitle="Sensitivity rate" />
          <MetricCard title="Macro F1-Score" value={`${m.classification.f1}%`} subtitle="Harmonic mean" isPositive={true} />
        </div>

        {/* Confusion Matrix Table */}
        <div className="mt-4 bg-white rounded-lg border border-slate-200 p-5 shadow-subtle space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-900 font-mono uppercase">
              Multi-Class Confusion Matrix (Predicted vs Actual Holdout Set)
            </span>
            <span className="text-[10px] text-slate-400 font-mono">N = 1,120 Test Records</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-center border-collapse text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-mono text-[10px]">
                  <th className="py-2 px-3 text-left">Actual \ Predicted</th>
                  {m.classification.categories.map((c, i) => (
                    <th key={i} className="py-2 px-2 truncate max-w-[90px]">{c}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono">
                {m.classification.confusionMatrix.map((row, rIdx) => (
                  <tr key={rIdx} className="hover:bg-slate-50">
                    <td className="py-2.5 px-3 text-left font-bold text-slate-700 font-sans text-xs">
                      {m.classification.categories[rIdx]}
                    </td>
                    {row.map((val, cIdx) => (
                      <td
                        key={cIdx}
                        className={`py-2 px-2 text-xs font-semibold ${
                          rIdx === cIdx ? "bg-blue-50 text-blue-800 font-bold" : "text-slate-400"
                        }`}
                      >
                        {val}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* DUPLICATE DETECTION METRICS */}
      <div className="pt-2">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 font-mono flex items-center gap-1.5 mb-3">
          <Layers className="w-4 h-4 text-purple-600" />
          2. Cross-Encoder Duplicate Detector (SBERT-Cosine)
        </h3>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <MetricCard title="Precision@K" value={`${m.duplicate.precisionAtK}%`} subtitle="Top-K relevance" />
          <MetricCard title="Recall@K" value={`${m.duplicate.recallAtK}%`} subtitle="Coverage rate" />
          <MetricCard title="F1-Score" value={`${m.duplicate.f1}%`} subtitle="Cluster quality" />
          <MetricCard title="Mean Average Precision (mAP)" value={m.duplicate.mapScore} subtitle="Ranking fidelity" isPositive={true} />
        </div>
      </div>

      {/* REGRESSION & SLA METRICS */}
      <div className="pt-2 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 font-mono">
            3. Resolution Duration Regressor (LightGBM)
          </h3>
          <div className="grid grid-cols-2 gap-3">
            <MetricCard title="Mean Absolute Error (MAE)" value={`${m.regression.mae}d`} subtitle="~16.3 Hours variance" />
            <MetricCard title="Root Mean Squared Error" value={`${m.regression.rmse}d`} subtitle="Penalty for outliers" />
            <MetricCard title="Median Absolute Error" value={`${m.regression.medae}d`} subtitle="Robust central error" />
            <MetricCard title="Coefficient of Determination (R²)" value={m.regression.r2} subtitle="Variance explained" isPositive={true} />
          </div>
        </div>

        <div className="space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 font-mono">
            4. SLA Breach Risk Classifier (XGBoost)
          </h3>
          <div className="grid grid-cols-2 gap-3">
            <MetricCard title="Breach Precision" value={`${m.slaBreach.precision}%`} subtitle="False alarm control" />
            <MetricCard title="Breach Recall" value={`${m.slaBreach.recall}%`} subtitle="Catches 86% of breaches" />
            <MetricCard title="PR-AUC Score" value={m.slaBreach.prAuc} subtitle="Precision-Recall Area" isPositive={true} />
            <MetricCard title="Brier Calibration Score" value={m.slaBreach.brierScore} subtitle="Lower is better (0-1)" />
          </div>
        </div>
      </div>
    </div>
  );
}

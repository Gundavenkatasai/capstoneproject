"use client";

import React, { useState } from "react";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { MetricCard } from "@/components/common/MetricCard";
import { ChartCard } from "@/components/common/ChartCard";
import { ConfidenceIndicator } from "@/components/common/ConfidenceIndicator";
import {
  BrainCircuit,
  Sparkles,
  Info,
  CheckCircle2,
  HelpCircle,
  Building,
  Layers,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { cn } from "@/lib/utils";

export default function ExplainableAIPage() {
  const [selectedCase, setSelectedCase] = useState("GRV-2026-8941");

  // Realistic SHAP feature contributions for the selected complaint
  const shapFeatures = [
    { feature: "Lexical 'flooding / burst'", impact: 0.38, type: "positive", category: "Keyword Ontology" },
    { feature: "Asset 'main feeder line'", impact: 0.31, type: "positive", category: "Knowledge Entity" },
    { feature: "Keyword 'clean drinking water'", impact: 0.22, type: "positive", category: "Keyword Ontology" },
    { feature: "Spatial Density Cluster > 4", impact: 0.15, type: "positive", category: "Spatial Hotspot" },
    { feature: "Sentiment Polarity (-0.74)", impact: 0.12, type: "positive", category: "Sentiment Lexicon" },
    { feature: "Language Complexity (Short)", impact: -0.06, type: "negative", category: "Syntactic Form" },
    { feature: "Absence of 'contractor name'", impact: -0.04, type: "negative", category: "Context Field" },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Explainable AI (XAI) & SHAP Decision Auditing"
        subtitle="Transparent feature attribution, TreeSHAP values, and lexical routing traces behind every automated categorization and priority decision."
        breadcrumbs={[
          { label: "Admin Portal", href: "/admin" },
          { label: "Explainable AI", active: true },
        ]}
        badge="TreeSHAP + KernelSHAP"
      />

      {/* Model Transparency Disclaimer Notice */}
      <div className="p-3.5 bg-slate-100 border border-slate-200 rounded-md flex items-start gap-3 text-xs text-slate-700">
        <Info className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold text-slate-900">Explainability Audit Standards Notice</span>
          <p className="mt-0.5 text-slate-600 leading-relaxed">
            In compliance with democratic AI accountability standards, all classification decisions provide SHAP (Shapley Additive Explanations) attributions indicating the relative positive or negative contribution of each lexical token and spatial parameter. Illustrative demonstration metrics are clearly cataloged for research validation.
          </p>
        </div>
      </div>

      {/* Case Selector Tabs */}
      <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-subtle flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-slate-700">Sample Complaint for XAI Inspection:</span>
          <select
            value={selectedCase}
            onChange={(e) => setSelectedCase(e.target.value)}
            className="text-xs font-semibold text-slate-900 border border-slate-200 rounded px-2.5 py-1.5 bg-slate-50"
          >
            <option value="GRV-2026-8941">GRV-2026-8941 (Major Water Feeder Rupture)</option>
            <option value="GRV-2026-8942">GRV-2026-8942 (Hazardous Arterial Pothole)</option>
            <option value="GRV-2026-8939">GRV-2026-8939 (12 Dark Streetlights Corridor)</option>
            <option value="GRV-2026-8940">GRV-2026-8940 (Commercial Waste Overflow)</option>
          </select>
        </div>

        <span className="text-xs font-mono text-slate-500">
          DeBERTa-v4.2 Baseline Bias: <strong className="text-slate-800">0.052</strong>
        </span>
      </div>

      {/* Overview Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Predicted Category"
          value="Water Supply"
          subtitle="Subcategory: Pipeline Rupture"
          icon={Layers}
        />
        <MetricCard
          title="AI Confidence"
          value="96.4%"
          subtitle="Margin over 2nd choice: +44%"
          icon={Sparkles}
          badge="High Reliability"
        />
        <MetricCard
          title="Recommended Dept"
          value="WSSB"
          subtitle="Water Supply & Sewerage Board"
          icon={Building}
        />
        <MetricCard
          title="Triage Priority"
          value="Critical"
          subtitle="Elevated due to flooding risk"
          icon={BrainCircuit}
          className="border-red-300 bg-red-50/20"
        />
      </div>

      {/* SHAP Waterfall / Feature Contribution Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <ChartCard
          title="SHAP Feature Importance & Contribution Chart"
          subtitle="Relative feature attribution pushing classification score toward Water Supply (+Impact) vs alternative departments (-Impact)"
          badge="Shapley Values"
          className="lg:col-span-7"
        >
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart layout="vertical" data={shapFeatures}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis type="number" stroke="#64748b" fontSize={11} domain={[-0.1, 0.45]} />
                <YAxis dataKey="feature" type="category" stroke="#64748b" fontSize={10} width={150} />
                <Tooltip />
                <Bar dataKey="impact" name="SHAP Contribution Weight">
                  {shapFeatures.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.impact > 0 ? "#2563eb" : "#ef4444"}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-2 text-center text-[11px] text-slate-400 font-mono">
            Blue bars represent positive evidence towards target category; Red bars represent suppressing factors.
          </div>
        </ChartCard>

        {/* Right Rail: Decision Trace & Audit Trail */}
        <div className="lg:col-span-5 bg-white rounded-lg border border-slate-200 p-5 shadow-subtle space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-100">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider font-mono">
              Decision Reasoning Trace
            </h3>
            <span className="text-[10px] font-mono bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded border border-blue-200">
              Audit Verified
            </span>
          </div>

          <div className="space-y-3 text-xs">
            <div className="p-3 bg-slate-50 rounded border border-slate-200">
              <span className="font-semibold text-slate-900 block mb-1">
                1. Token Extraction & Semantic Alignment
              </span>
              <p className="text-slate-600 leading-relaxed">
                Tokens <code className="bg-white px-1 py-0.5 rounded border text-blue-700">burst</code> and{" "}
                <code className="bg-white px-1 py-0.5 rounded border text-blue-700">feeder line</code> matched node{" "}
                <code className="bg-white px-1 py-0.5 rounded border text-purple-700">Hydraulic Asset #4</code> in Civic Knowledge Graph.
              </p>
            </div>

            <div className="p-3 bg-slate-50 rounded border border-slate-200">
              <span className="font-semibold text-slate-900 block mb-1">
                2. Risk Escalation Matrix
              </span>
              <p className="text-slate-600 leading-relaxed">
                Phrase <code className="bg-white px-1 py-0.5 rounded border text-red-700">flooding basement</code> triggered Life-Safety Triage Clause #14-B, elevating priority from Medium to Critical.
              </p>
            </div>

            <div className="p-3 bg-slate-50 rounded border border-slate-200">
              <span className="font-semibold text-slate-900 block mb-1">
                3. Spatial Proximity Reinforcement
              </span>
              <p className="text-slate-600 leading-relaxed">
                Incident GPS falls within 280m of known pipeline pressure anomaly detected 18 hours prior, providing +0.15 SHAP boost to cluster association.
              </p>
            </div>
          </div>

          <div className="pt-2 border-t border-slate-100 text-[11px] text-slate-400 font-mono">
            Cryptographic Decision Hash: <code>0x9a8f4c21...8941</code>
          </div>
        </div>
      </div>
    </div>
  );
}

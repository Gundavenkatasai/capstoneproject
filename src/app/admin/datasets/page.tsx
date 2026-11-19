"use client";

import React from "react";
import { MOCK_RESEARCH_METRICS } from "@/mocks/mockData";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { MetricCard } from "@/components/common/MetricCard";
import { ChartCard } from "@/components/common/ChartCard";
import { Database, FileText, Globe, Layers, CheckCircle2 } from "lucide-react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

export default function DatasetExplorerPage() {
  const stats = MOCK_RESEARCH_METRICS.datasetStats;

  const languageData = [
    { name: "English", value: 58, color: "#1E6BE6" },
    { name: "Hindi (हिंदी)", value: 31, color: "#D97706" },
    { name: "Hinglish (Code-Switched)", value: 11, color: "#0D9488" },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Dataset Explorer & Corpus Composition"
        subtitle="Audited breakdown of the 142.5K civic grievance corpus utilized for training, validation, and fair representation across municipal wards."
        breadcrumbs={[
          { label: "Admin Portal", href: "/admin" },
          { label: "Dataset Explorer", active: true },
        ]}
        badge="Corpus v4.2"
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Corpus Records"
          value={stats.totalRecords.toLocaleString()}
          subtitle="Grievance statements cataloged"
          icon={Database}
        />
        <MetricCard
          title="Supervised Labeled Set"
          value={stats.labeledRecords.toLocaleString()}
          subtitle="97.0% ground-truth labeled"
          icon={CheckCircle2}
          isPositive={true}
        />
        <MetricCard
          title="Geographic Wards Covered"
          value={stats.geographicWards}
          subtitle="Comprehensive city coverage"
          icon={Globe}
        />
        <MetricCard
          title="Corpus Integrity"
          value="99.4%"
          subtitle="<0.6% missing fields"
          icon={FileText}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard
          title="Language Representation in Corpus"
          subtitle="Multilingual distribution across English, Hindi, and colloquial Hinglish"
          badge="Multimodal NLP"
        >
          <div className="h-64 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={languageData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {languageData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend iconSize={8} wrapperStyle={{ fontSize: "11px" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        <div className="bg-white rounded-lg border border-slate-200 p-6 shadow-subtle space-y-4 text-xs">
          <h3 className="text-sm font-bold text-slate-900">
            Data Provenance & Augmentation Metadata
          </h3>
          <p className="text-slate-600 leading-relaxed">
            The dataset merges open public municipal disclosure records with controlled synthetic augmentation to address class imbalance for rare high-risk hazards (such as high-tension electrical wire collapse and industrial gas leakage).
          </p>

          <div className="space-y-2 pt-2">
            <div className="p-3 bg-slate-50 rounded border border-slate-200 flex justify-between">
              <span className="text-slate-600">Open Public Data Percentage</span>
              <strong className="text-slate-900 font-mono">{stats.realPublicDataPercentage}</strong>
            </div>
            <div className="p-3 bg-slate-50 rounded border border-slate-200 flex justify-between">
              <span className="text-slate-600">Synthetic Balancing (SMOTE / Back-Translation)</span>
              <strong className="text-blue-700 font-mono">{stats.syntheticPercentage}</strong>
            </div>
            <div className="p-3 bg-slate-50 rounded border border-slate-200 flex justify-between">
              <span className="text-slate-600">Categories / Subcategories Count</span>
              <strong className="text-slate-900 font-mono">{stats.categoriesCount} / {stats.subcategoriesCount}</strong>
            </div>
            <div className="p-3 bg-slate-50 rounded border border-slate-200 flex justify-between">
              <span className="text-slate-600">Data License</span>
              <strong className="text-slate-900">Open Government Data (OGD) License</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

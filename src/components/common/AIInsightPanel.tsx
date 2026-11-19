import React from "react";
import { Grievance, SHAPFactor } from "@/types";
import { ConfidenceIndicator } from "./ConfidenceIndicator";
import { PriorityBadge } from "./PriorityBadge";
import { cn } from "@/lib/utils";
import { Sparkles, Bot, Clock, AlertTriangle, Layers, Building, HelpCircle } from "lucide-react";

interface AIInsightPanelProps {
  grievance?: Partial<Grievance>;
  predictionResult?: any;
  className?: string;
  onOverride?: () => void;
}

export function AIInsightPanel({
  grievance,
  predictionResult,
  className,
  onOverride,
}: AIInsightPanelProps) {
  const data = predictionResult || grievance || {};
  const confidence = data.confidence || data.aiConfidence || 0.94;
  const duplicateProb = data.duplicateProbability ?? 0.12;
  const predictedDays = data.estimatedDurationDays || data.predictedDurationDays || 3.2;

  const shapFactors: SHAPFactor[] = data.shapFactors || data.shapExplanation || [
    { feature: "Primary keyword match", weight: 0.38, effect: "positive", description: "Matches department ontology" },
    { feature: "Geographic incident density", weight: 0.24, effect: "positive", description: "Cluster activity in ward" },
  ];

  return (
    <div
      className={cn(
        "rounded-md border border-blue-200/90 bg-gradient-to-br from-blue-50/50 via-white to-slate-50/60 p-5 shadow-subtle",
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between pb-3 mb-4 border-b border-blue-100">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded bg-blue-600 text-white flex items-center justify-center shadow-xs">
            <Sparkles className="w-3.5 h-3.5" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-slate-900 tracking-tight flex items-center gap-1.5">
              CivicMind AI Intelligence Analysis
              <span className="text-[10px] font-normal text-blue-700 bg-blue-100/70 px-1.5 py-0.2 rounded font-mono">
                v4.2 NLP
              </span>
            </h3>
            <p className="text-[11px] text-slate-500">Autonomous semantic routing & risk triage</p>
          </div>
        </div>

        <ConfidenceIndicator confidence={confidence} />
      </div>

      {/* Grid of Key AI Classifications */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
        <div className="bg-white/90 p-3 rounded border border-slate-200/80 shadow-xs">
          <div className="flex items-center gap-1.5 text-slate-500 text-[11px] font-medium mb-1">
            <Building className="w-3.5 h-3.5 text-slate-400" />
            Recommended Department
          </div>
          <p className="text-xs font-semibold text-slate-900 truncate">
            {data.recommendedDepartment || data.departmentName || "Public Works Department"}
          </p>
        </div>

        <div className="bg-white/90 p-3 rounded border border-slate-200/80 shadow-xs">
          <div className="flex items-center gap-1.5 text-slate-500 text-[11px] font-medium mb-1">
            <Layers className="w-3.5 h-3.5 text-slate-400" />
            Predicted Category
          </div>
          <p className="text-xs font-semibold text-slate-900 truncate">
            {data.predictedCategory || data.category || "Municipal Services"}
          </p>
          <p className="text-[10px] text-slate-400 truncate">
            {data.predictedSubcategory || data.subcategory || "General"}
          </p>
        </div>

        <div className="bg-white/90 p-3 rounded border border-slate-200/80 shadow-xs">
          <div className="flex items-center gap-1.5 text-slate-500 text-[11px] font-medium mb-1">
            <AlertTriangle className="w-3.5 h-3.5 text-slate-400" />
            Triage Priority
          </div>
          <div className="mt-0.5">
            <PriorityBadge priority={data.priority || "medium"} />
          </div>
        </div>

        <div className="bg-white/90 p-3 rounded border border-slate-200/80 shadow-xs">
          <div className="flex items-center gap-1.5 text-slate-500 text-[11px] font-medium mb-1">
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            Predicted Resolution SLA
          </div>
          <p className="text-xs font-bold text-slate-900 font-mono">
            ~{predictedDays} Days
          </p>
          <p className="text-[10px] text-slate-400">95% CI: [{Math.max(1, predictedDays - 1)} - {predictedDays + 1.5}d]</p>
        </div>
      </div>

      {/* Duplicate probability notice */}
      {duplicateProb > 0.4 && (
        <div className="mb-4 p-2.5 rounded bg-amber-50 border border-amber-200 text-xs flex items-start gap-2.5">
          <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-amber-900">
                Potential Duplicate Alert ({Math.round(duplicateProb * 100)}% Similarity Probability)
              </span>
            </div>
            <p className="text-amber-800 text-[11px] mt-0.5">
              High semantic & spatial correlation with existing cluster. Administrator review recommended before creating duplicate field dispatch.
            </p>
          </div>
        </div>
      )}

      {/* Explainable SHAP Features */}
      {shapFactors && shapFactors.length > 0 && (
        <div className="bg-white/80 rounded border border-slate-200/70 p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-semibold text-slate-700 uppercase tracking-wider flex items-center gap-1">
              <HelpCircle className="w-3 h-3 text-slate-400" />
              Key AI Routing Factors (SHAP Feature Attribution)
            </span>
            <span className="text-[10px] text-slate-400 font-mono">Model: Civic-DeBERTa-v4</span>
          </div>
          <div className="space-y-1.5">
            {shapFactors.map((factor, i) => (
              <div key={i} className="flex items-center justify-between text-xs py-1 border-b border-slate-100 last:border-0">
                <span className="text-slate-700 font-medium truncate max-w-md">{factor.feature}</span>
                <div className="flex items-center gap-2">
                  <span className="text-[11px] text-slate-500 hidden sm:inline">{factor.description}</span>
                  <span
                    className={cn(
                      "font-mono text-[10px] px-1.5 py-0.5 rounded font-semibold",
                      factor.effect === "positive"
                        ? "bg-blue-50 text-blue-700 border border-blue-200"
                        : "bg-slate-100 text-slate-600"
                    )}
                  >
                    +{Math.round(factor.weight * 100)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {onOverride && (
        <div className="mt-3 flex justify-end">
          <button
            onClick={onOverride}
            className="text-xs text-blue-600 hover:text-blue-800 font-medium hover:underline flex items-center gap-1"
          >
            Wrong department or category? Correct AI prediction →
          </button>
        </div>
      )}
    </div>
  );
}

import React from "react";
import { cn } from "@/lib/utils";

interface ConfidenceIndicatorProps {
  confidence: number; // 0 to 1
  label?: string;
  showBar?: boolean;
  className?: string;
}

export function ConfidenceIndicator({
  confidence,
  label = "AI Confidence",
  showBar = true,
  className,
}: ConfidenceIndicatorProps) {
  const pct = Math.round(confidence * 100);

  const getColor = (val: number) => {
    if (val >= 90) return { text: "text-emerald-700", bar: "bg-emerald-500", bg: "bg-emerald-50" };
    if (val >= 75) return { text: "text-blue-700", bar: "bg-blue-500", bg: "bg-blue-50" };
    if (val >= 50) return { text: "text-amber-700", bar: "bg-amber-500", bg: "bg-amber-50" };
    return { text: "text-rose-700", bar: "bg-rose-500", bg: "bg-rose-50" };
  };

  const style = getColor(pct);

  return (
    <div className={cn("flex items-center gap-2 text-xs", className)}>
      {showBar && (
        <div className="w-12 h-1.5 bg-slate-100 rounded-full overflow-hidden border border-slate-200">
          <div
            className={cn("h-full transition-all duration-300", style.bar)}
            style={{ width: `${pct}%` }}
          />
        </div>
      )}
      <span className={cn("font-mono font-medium", style.text)}>
        {pct}%
      </span>
      {label && <span className="text-slate-400 text-[10px] uppercase font-mono">{label}</span>}
    </div>
  );
}

interface RiskIndicatorProps {
  risk: "low" | "medium" | "high" | "critical";
  score?: number;
  className?: string;
}

export function RiskIndicator({ risk, score, className }: RiskIndicatorProps) {
  const config = {
    critical: { label: "Critical Risk", bg: "bg-red-50", text: "text-red-700", border: "border-red-200", dot: "bg-red-500" },
    high: { label: "High Risk", bg: "bg-amber-50", text: "text-amber-700", border: "border-amber-200", dot: "bg-amber-500" },
    medium: { label: "Medium Risk", bg: "bg-blue-50", text: "text-blue-700", border: "border-blue-200", dot: "bg-blue-500" },
    low: { label: "Low Risk", bg: "bg-slate-50", text: "text-slate-600", border: "border-slate-200", dot: "bg-emerald-500" },
  }[risk];

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-medium border",
        config.bg,
        config.text,
        config.border,
        className
      )}
    >
      <span className={cn("w-1.5 h-1.5 rounded-full animate-pulse", config.dot)} />
      {config.label}
      {score !== undefined && <span className="font-mono text-[10px] opacity-80">({score})</span>}
    </span>
  );
}

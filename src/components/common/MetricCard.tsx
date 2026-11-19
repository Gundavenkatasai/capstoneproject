import React from "react";
import { cn } from "@/lib/utils";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  change?: string;
  changeType?: "increase" | "decrease" | "neutral";
  isPositive?: boolean; // if increase is good, true; if increase in backlog is bad, false
  icon?: React.ComponentType<{ className?: string }>;
  badge?: string;
  className?: string;
  onClick?: () => void;
}

export function MetricCard({
  title,
  value,
  subtitle,
  change,
  changeType = "neutral",
  isPositive,
  icon: Icon,
  badge,
  className,
  onClick,
}: MetricCardProps) {
  // Determine color for change
  let changeColor = "text-slate-500 bg-slate-50 border-slate-200";
  let TrendIcon = Minus;

  if (changeType === "increase") {
    TrendIcon = TrendingUp;
    if (isPositive === true) {
      changeColor = "text-emerald-700 bg-emerald-50 border-emerald-200";
    } else if (isPositive === false) {
      changeColor = "text-red-700 bg-red-50 border-red-200";
    } else {
      changeColor = "text-blue-700 bg-blue-50 border-blue-200";
    }
  } else if (changeType === "decrease") {
    TrendIcon = TrendingDown;
    if (isPositive === true) {
      changeColor = "text-emerald-700 bg-emerald-50 border-emerald-200";
    } else if (isPositive === false) {
      changeColor = "text-red-700 bg-red-50 border-red-200";
    } else {
      changeColor = "text-slate-600 bg-slate-50 border-slate-200";
    }
  }

  return (
    <div
      onClick={onClick}
      className={cn(
        "bg-white rounded-md border border-slate-200/80 p-5 shadow-subtle hover:border-slate-300 transition-all",
        onClick && "cursor-pointer hover:shadow-card",
        className
      )}
    >
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 truncate">
          {title}
        </span>
        <div className="flex items-center gap-1.5">
          {badge && (
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200">
              {badge}
            </span>
          )}
          {Icon && (
            <div className="w-7 h-7 rounded bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-600">
              <Icon className="w-4 h-4" />
            </div>
          )}
        </div>
      </div>

      <div className="mt-3 flex items-baseline justify-between gap-2">
        <div className="text-2xl font-bold tracking-tight text-slate-900 font-sans">
          {value}
        </div>
        {change && (
          <div
            className={cn(
              "inline-flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded border font-mono",
              changeColor
            )}
          >
            <TrendIcon className="w-3 h-3" />
            {change}
          </div>
        )}
      </div>

      {subtitle && (
        <p className="mt-1.5 text-xs text-slate-500 line-clamp-1">{subtitle}</p>
      )}
    </div>
  );
}

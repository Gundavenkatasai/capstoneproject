import React from "react";
import { GrievancePriority } from "@/types";
import { cn } from "@/lib/utils";
import { AlertCircle, ArrowUp, ArrowRight, ArrowDown } from "lucide-react";

interface PriorityBadgeProps {
  priority: GrievancePriority;
  className?: string;
  showIcon?: boolean;
}

const priorityConfig: Record<
  GrievancePriority,
  { label: string; bg: string; text: string; border: string; dot: string; icon: React.ComponentType<{ className?: string }> }
> = {
  critical: {
    label: "Critical",
    bg: "bg-red-50",
    text: "text-red-700",
    border: "border-red-200",
    dot: "bg-red-500",
    icon: AlertCircle,
  },
  high: {
    label: "High",
    bg: "bg-amber-50",
    text: "text-amber-800",
    border: "border-amber-200",
    dot: "bg-amber-500",
    icon: ArrowUp,
  },
  medium: {
    label: "Medium",
    bg: "bg-blue-50",
    text: "text-blue-700",
    border: "border-blue-200",
    dot: "bg-blue-500",
    icon: ArrowRight,
  },
  low: {
    label: "Low",
    bg: "bg-slate-50",
    text: "text-slate-600",
    border: "border-slate-200",
    dot: "bg-slate-400",
    icon: ArrowDown,
  },
};

export function PriorityBadge({ priority, className, showIcon = true }: PriorityBadgeProps) {
  const config = priorityConfig[priority] || priorityConfig.medium;
  const Icon = config.icon;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-semibold border",
        config.bg,
        config.text,
        config.border,
        className
      )}
    >
      <span className={cn("w-1.5 h-1.5 rounded-full", config.dot)} />
      {showIcon && <Icon className="w-3 h-3" />}
      {config.label}
    </span>
  );
}

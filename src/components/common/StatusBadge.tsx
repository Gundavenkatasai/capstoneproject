import React from "react";
import { GrievanceStatus } from "@/types";
import { cn } from "@/lib/utils";
import {
  Clock,
  Sparkles,
  UserCheck,
  Wrench,
  CheckCircle2,
  ShieldCheck,
  AlertTriangle,
  RotateCcw,
} from "lucide-react";

interface StatusBadgeProps {
  status: GrievanceStatus;
  className?: string;
  showIcon?: boolean;
}

const statusConfig: Record<
  GrievanceStatus,
  { label: string; bg: string; text: string; border: string; icon: React.ComponentType<{ className?: string }> }
> = {
  submitted: {
    label: "Submitted",
    bg: "bg-slate-50",
    text: "text-slate-700",
    border: "border-slate-200",
    icon: Clock,
  },
  analyzed: {
    label: "AI Analyzed",
    bg: "bg-blue-50",
    text: "text-blue-700",
    border: "border-blue-200",
    icon: Sparkles,
  },
  assigned: {
    label: "Assigned",
    bg: "bg-sky-50",
    text: "text-sky-700",
    border: "border-sky-200",
    icon: UserCheck,
  },
  in_progress: {
    label: "In Progress",
    bg: "bg-amber-50",
    text: "text-amber-800",
    border: "border-amber-200",
    icon: Wrench,
  },
  resolution_submitted: {
    label: "Resolution Filed",
    bg: "bg-indigo-50",
    text: "text-indigo-700",
    border: "border-indigo-200",
    icon: CheckCircle2,
  },
  citizen_verified: {
    label: "Citizen Verified",
    bg: "bg-emerald-50",
    text: "text-emerald-700",
    border: "border-emerald-200",
    icon: ShieldCheck,
  },
  closed: {
    label: "Resolved & Closed",
    bg: "bg-teal-50",
    text: "text-teal-700",
    border: "border-teal-200",
    icon: CheckCircle2,
  },
  escalated: {
    label: "Escalated",
    bg: "bg-rose-50",
    text: "text-rose-700",
    border: "border-rose-200",
    icon: AlertTriangle,
  },
  reopened: {
    label: "Reopened",
    bg: "bg-orange-50",
    text: "text-orange-700",
    border: "border-orange-200",
    icon: RotateCcw,
  },
};

export function StatusBadge({ status, className, showIcon = true }: StatusBadgeProps) {
  const config = statusConfig[status] || statusConfig.submitted;
  const Icon = config.icon;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border",
        config.bg,
        config.text,
        config.border,
        className
      )}
    >
      {showIcon && <Icon className="w-3 h-3" />}
      {config.label}
    </span>
  );
}

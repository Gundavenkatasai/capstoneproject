import React from "react";
import { AlertTriangle, Info, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface ConfirmationDialogProps {
  open: boolean;
  title: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  type?: "danger" | "warning" | "info" | "success";
  onConfirm: () => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function ConfirmationDialog({
  open,
  title,
  description,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  type = "info",
  onConfirm,
  onCancel,
  isLoading = false,
}: ConfirmationDialogProps) {
  if (!open) return null;

  const iconConfig = {
    danger: { icon: AlertTriangle, color: "text-red-600", bg: "bg-red-50", btn: "bg-red-600 hover:bg-red-700 text-white" },
    warning: { icon: AlertTriangle, color: "text-amber-600", bg: "bg-amber-50", btn: "bg-amber-600 hover:bg-amber-700 text-white" },
    info: { icon: Info, color: "text-blue-600", bg: "bg-blue-50", btn: "bg-blue-600 hover:bg-blue-700 text-white" },
    success: { icon: CheckCircle2, color: "text-emerald-600", bg: "bg-emerald-50", btn: "bg-emerald-600 hover:bg-emerald-700 text-white" },
  }[type];

  const Icon = iconConfig.icon;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="relative w-full max-w-md bg-white rounded-lg shadow-elevated border border-slate-200 overflow-hidden">
        <div className="p-5 flex gap-4">
          <div className={cn("w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0", iconConfig.bg)}>
            <Icon className={cn("w-5 h-5", iconConfig.color)} />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-900">{title}</h3>
            <p className="mt-1 text-xs text-slate-500 leading-relaxed">{description}</p>
          </div>
        </div>

        <div className="px-5 py-3 bg-slate-50 border-t border-slate-100 flex items-center justify-end gap-2">
          <button
            type="button"
            disabled={isLoading}
            onClick={onCancel}
            className="px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-200/60 rounded border border-slate-200 bg-white transition-colors"
          >
            {cancelLabel}
          </button>
          <button
            type="button"
            disabled={isLoading}
            onClick={onConfirm}
            className={cn(
              "px-3.5 py-1.5 text-xs font-semibold rounded shadow-subtle transition-colors flex items-center gap-1.5",
              iconConfig.btn,
              isLoading && "opacity-70 cursor-not-allowed"
            )}
          >
            {isLoading ? "Processing..." : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

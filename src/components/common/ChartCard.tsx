import React from "react";
import { cn } from "@/lib/utils";

interface ChartCardProps {
  title: string;
  subtitle?: string;
  badge?: string;
  action?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  footer?: React.ReactNode;
}

export function ChartCard({
  title,
  subtitle,
  badge,
  action,
  children,
  className,
  footer,
}: ChartCardProps) {
  return (
    <div
      className={cn(
        "bg-white rounded-md border border-slate-200/80 shadow-subtle flex flex-col overflow-hidden",
        className
      )}
    >
      <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-slate-900 tracking-tight">
              {title}
            </h3>
            {badge && (
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200 font-medium">
                {badge}
              </span>
            )}
          </div>
          {subtitle && (
            <p className="text-xs text-slate-500 mt-0.5 line-clamp-1">{subtitle}</p>
          )}
        </div>
        {action && <div className="flex items-center gap-2 flex-shrink-0">{action}</div>}
      </div>

      <div className="p-5 flex-1">{children}</div>

      {footer && (
        <div className="px-5 py-3 border-t border-slate-100 bg-slate-50/50 text-xs text-slate-500 flex items-center justify-between">
          {footer}
        </div>
      )}
    </div>
  );
}

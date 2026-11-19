import React from "react";
import { cn } from "@/lib/utils";
import { Inbox, AlertCircle, RefreshCw } from "lucide-react";

interface EmptyStateProps {
  title: string;
  description: string;
  icon?: React.ComponentType<{ className?: string }>;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
}

export function EmptyState({
  title,
  description,
  icon: Icon = Inbox,
  actionLabel,
  onAction,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center p-10 text-center bg-white rounded-md border border-dashed border-slate-200",
        className
      )}
    >
      <div className="w-12 h-12 rounded-full bg-slate-50 border border-slate-200/80 flex items-center justify-center text-slate-400 mb-3.5">
        <Icon className="w-6 h-6" />
      </div>
      <h4 className="text-sm font-semibold text-slate-900 mb-1">{title}</h4>
      <p className="text-xs text-slate-500 max-w-sm mb-4 leading-relaxed">{description}</p>
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium transition-colors shadow-subtle"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}

interface LoadingSkeletonProps {
  type?: "table" | "card" | "detail" | "chart";
  count?: number;
  className?: string;
}

export function LoadingSkeleton({ type = "card", count = 3, className }: LoadingSkeletonProps) {
  if (type === "table") {
    return (
      <div className={cn("w-full bg-white rounded border border-slate-200 p-4 space-y-3", className)}>
        <div className="h-8 bg-slate-100 rounded animate-pulse w-full mb-4" />
        {Array.from({ length: count }).map((_, i) => (
          <div key={i} className="flex gap-4 items-center">
            <div className="h-4 bg-slate-100 rounded animate-pulse w-24" />
            <div className="h-4 bg-slate-100 rounded animate-pulse flex-1" />
            <div className="h-4 bg-slate-100 rounded animate-pulse w-28" />
            <div className="h-4 bg-slate-100 rounded animate-pulse w-16" />
          </div>
        ))}
      </div>
    );
  }

  if (type === "chart") {
    return (
      <div className={cn("w-full h-72 bg-white rounded border border-slate-200 p-5 flex flex-col justify-between", className)}>
        <div className="space-y-2">
          <div className="h-4 bg-slate-100 rounded animate-pulse w-48" />
          <div className="h-3 bg-slate-50 rounded animate-pulse w-72" />
        </div>
        <div className="h-44 bg-slate-50 rounded animate-pulse w-full" />
      </div>
    );
  }

  return (
    <div className={cn("grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4", className)}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="bg-white rounded border border-slate-200 p-5 space-y-3">
          <div className="flex justify-between items-center">
            <div className="h-3 bg-slate-100 rounded animate-pulse w-24" />
            <div className="h-5 w-5 bg-slate-100 rounded animate-pulse" />
          </div>
          <div className="h-7 bg-slate-100 rounded animate-pulse w-16" />
          <div className="h-3 bg-slate-50 rounded animate-pulse w-32" />
        </div>
      ))}
    </div>
  );
}

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorState({
  title = "Failed to load data",
  message = "An error occurred while connecting to the intelligence service. Please check your network or try again.",
  onRetry,
  className,
}: ErrorStateProps) {
  return (
    <div
      className={cn(
        "p-6 rounded-md bg-red-50/50 border border-red-200/80 flex flex-col items-center text-center",
        className
      )}
    >
      <AlertCircle className="w-8 h-8 text-red-500 mb-2" />
      <h4 className="text-sm font-semibold text-red-900 mb-1">{title}</h4>
      <p className="text-xs text-red-600 max-w-md mb-3">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-white hover:bg-slate-50 border border-red-200 text-red-700 text-xs font-medium transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Retry Connection
        </button>
      )}
    </div>
  );
}

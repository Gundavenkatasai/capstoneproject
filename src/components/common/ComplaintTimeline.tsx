import React from "react";
import { TimelineEvent } from "@/types";
import { StatusBadge } from "./StatusBadge";
import { formatDate, formatRelativeTime } from "@/lib/utils";
import { cn } from "@/lib/utils";
import { Clock, User, Shield, Bot, CheckCircle } from "lucide-react";

interface ComplaintTimelineProps {
  events: TimelineEvent[];
  className?: string;
}

export function ComplaintTimeline({ events, className }: ComplaintTimelineProps) {
  if (!events || events.length === 0) {
    return <p className="text-xs text-slate-400 italic">No timeline events recorded.</p>;
  }

  const getActorIcon = (role: string) => {
    const lower = role.toLowerCase();
    if (lower.includes("system") || lower.includes("ai") || lower.includes("router")) {
      return <Bot className="w-3 h-3 text-blue-600" />;
    }
    if (lower.includes("officer") || lower.includes("engineer") || lower.includes("inspector")) {
      return <Shield className="w-3 h-3 text-amber-600" />;
    }
    if (lower.includes("citizen")) {
      return <User className="w-3 h-3 text-slate-600" />;
    }
    return <CheckCircle className="w-3 h-3 text-emerald-600" />;
  };

  return (
    <div className={cn("relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200", className)}>
      {events.map((event, index) => {
        const isLatest = index === events.length - 1;

        return (
          <div key={event.id || index} className="relative group">
            {/* Timeline node icon */}
            <div
              className={cn(
                "absolute -left-6 top-0.5 w-5 h-5 rounded-full border-2 bg-white flex items-center justify-center transition-all",
                isLatest
                  ? "border-blue-600 shadow-sm ring-2 ring-blue-100"
                  : "border-slate-300 group-hover:border-slate-400"
              )}
            >
              <div
                className={cn(
                  "w-1.5 h-1.5 rounded-full",
                  isLatest ? "bg-blue-600" : "bg-slate-400"
                )}
              />
            </div>

            <div className="bg-white rounded border border-slate-200/80 p-3.5 shadow-subtle hover:border-slate-300 transition-colors">
              <div className="flex flex-wrap items-center justify-between gap-2 mb-1.5">
                <div className="flex items-center gap-2">
                  <h4 className="text-xs font-semibold text-slate-900">{event.title}</h4>
                  <StatusBadge status={event.status} showIcon={false} className="py-0 px-2 text-[10px]" />
                </div>
                <div className="flex items-center gap-1.5 text-[11px] text-slate-400 font-mono">
                  <Clock className="w-3 h-3" />
                  <span>{formatDate(event.timestamp, { hour: "numeric", minute: "numeric" })}</span>
                  <span className="text-slate-300">•</span>
                  <span>{formatRelativeTime(event.timestamp)}</span>
                </div>
              </div>

              <p className="text-xs text-slate-600 leading-relaxed">{event.description}</p>

              {event.notes && (
                <div className="mt-2 text-xs p-2 rounded bg-amber-50/60 border border-amber-200/60 text-amber-800 italic">
                  Note: {event.notes}
                </div>
              )}

              <div className="mt-2.5 pt-2 border-t border-slate-100 flex items-center gap-1.5 text-[11px] text-slate-500">
                {getActorIcon(event.actorRole)}
                <span className="font-medium text-slate-700">{event.actor}</span>
                <span className="text-slate-400 text-[10px]">({event.actorRole})</span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

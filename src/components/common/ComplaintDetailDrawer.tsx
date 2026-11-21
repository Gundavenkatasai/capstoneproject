import React from "react";
import { Link } from "react-router-dom";
import { Grievance } from "@/types";
import { StatusBadge } from "./StatusBadge";
import { PriorityBadge } from "./PriorityBadge";
import { ConfidenceIndicator } from "./ConfidenceIndicator";
import { ComplaintTimeline } from "./ComplaintTimeline";
import { AIInsightPanel } from "./AIInsightPanel";
import { formatDate } from "@/lib/utils";
import { X, ExternalLink, MapPin, Calendar, User, Building, Paperclip, AlertCircle } from "lucide-react";

interface ComplaintDetailDrawerProps {
  grievance: Grievance | null;
  open: boolean;
  onClose: () => void;
  baseRoute?: string; // '/admin' | '/officer' | '/citizen'
  onStatusChange?: (newStatus: any) => void;
}

export function ComplaintDetailDrawer({
  grievance,
  open,
  onClose,
  baseRoute = "/admin",
  onStatusChange,
}: ComplaintDetailDrawerProps) {
  if (!open || !grievance) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-slate-900/40 backdrop-blur-xs transition-opacity"
        onClick={onClose}
      />

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-2xl bg-white shadow-elevated border-l border-slate-200 flex flex-col">
          {/* Header */}
          <div className="px-6 py-4 border-b border-slate-200 bg-slate-50/70 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-slate-200/80 text-slate-800">
                {grievance.id}
              </span>
              <StatusBadge status={grievance.status} />
              <PriorityBadge priority={grievance.priority} />
            </div>

            <div className="flex items-center gap-2">
              <Link
                to={`${baseRoute}/grievances/${grievance.id}`}
                className="p-1.5 rounded hover:bg-slate-200 text-slate-500 hover:text-slate-700 transition-colors"
                title="Open Dedicated Full Page"
              >
                <ExternalLink className="w-4 h-4" />
              </Link>
              <button
                onClick={onClose}
                className="p-1.5 rounded hover:bg-slate-200 text-slate-500 hover:text-slate-700 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Drawer Body */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {/* Title & Core Metadata */}
            <div>
              <h2 className="text-base font-bold text-slate-900 leading-snug">
                {grievance.title}
              </h2>
              <div className="mt-3 grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs bg-slate-50 p-3.5 rounded border border-slate-200/70">
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-mono">Department</span>
                  <span className="font-semibold text-slate-800 mt-0.5 block truncate">
                    {grievance.departmentName}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-mono">Category</span>
                  <span className="font-semibold text-slate-800 mt-0.5 block truncate">
                    {grievance.category}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-mono">Filed Date</span>
                  <span className="font-semibold text-slate-800 mt-0.5 block font-mono">
                    {formatDate(grievance.submittedAt)}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-mono">Citizen</span>
                  <span className="font-semibold text-slate-800 mt-0.5 block">
                    {grievance.isAnonymous ? "Anonymous Citizen" : grievance.citizenName}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-mono">Ward / Zone</span>
                  <span className="font-semibold text-slate-800 mt-0.5 block">
                    {grievance.location.ward} ({grievance.location.zone})
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-mono">SLA Deadline</span>
                  <span className="font-semibold text-slate-800 mt-0.5 block font-mono">
                    {formatDate(grievance.slaDeadline)}
                  </span>
                </div>
              </div>
            </div>

            {/* Description */}
            <div>
              <h3 className="text-xs font-semibold text-slate-900 uppercase tracking-wider mb-2">
                Citizen Statement & Evidence
              </h3>
              <div className="p-4 rounded bg-white border border-slate-200 text-xs text-slate-700 leading-relaxed whitespace-pre-wrap">
                {grievance.description}
              </div>

              {/* Location Address Banner */}
              <div className="mt-2.5 flex items-center gap-2 text-xs text-slate-600 bg-slate-50 p-2.5 rounded border border-slate-200/60">
                <MapPin className="w-3.5 h-3.5 text-red-500 flex-shrink-0" />
                <span className="font-medium">{grievance.location.address}</span>
              </div>

              {/* Evidence attachments */}
              {grievance.evidence && grievance.evidence.length > 0 && (
                <div className="mt-3">
                  <span className="text-[11px] font-semibold text-slate-500 block mb-1.5">
                    Attached Files ({grievance.evidence.length})
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {grievance.evidence.map((ev) => (
                      <a
                        key={ev.id}
                        href={ev.url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-slate-50 hover:bg-slate-100 border border-slate-200 text-xs text-slate-700 transition-colors"
                      >
                        <Paperclip className="w-3 h-3 text-slate-400" />
                        <span className="font-medium truncate max-w-[140px]">{ev.name}</span>
                        <span className="text-[10px] text-slate-400">({ev.size})</span>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* AI Insight Panel */}
            <AIInsightPanel grievance={grievance} />

            {/* Resolution Report if available */}
            {grievance.resolutionReport && (
              <div className="p-4 rounded-md bg-emerald-50/70 border border-emerald-200">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-xs font-bold text-emerald-900">
                    Official Officer Resolution Report
                  </h4>
                  <span className="text-[10px] text-emerald-700 font-mono">
                    {formatDate(grievance.resolutionReport.resolvedAt)}
                  </span>
                </div>
                <p className="text-xs text-emerald-800 mb-2.5 leading-relaxed">
                  {grievance.resolutionReport.text}
                </p>
                {grievance.resolutionReport.citizenFeedbackComment && (
                  <div className="mt-2 pt-2 border-t border-emerald-200/70 text-xs text-emerald-900 italic">
                    Citizen Feedback ({grievance.resolutionReport.citizenFeedbackRating}/5 ★): "
                    {grievance.resolutionReport.citizenFeedbackComment}"
                  </div>
                )}
              </div>
            )}

            {/* Timeline */}
            <div>
              <h3 className="text-xs font-semibold text-slate-900 uppercase tracking-wider mb-3">
                Lifecycle & Audit Timeline
              </h3>
              <ComplaintTimeline events={grievance.timeline} />
            </div>
          </div>

          {/* Drawer Footer Actions */}
          <div className="px-6 py-3.5 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
            <Link
              to={`${baseRoute}/grievances/${grievance.id}`}
              className="text-xs text-blue-600 hover:text-blue-800 font-semibold"
            >
              Open Complete Grievance Record →
            </Link>

            <button
              onClick={onClose}
              className="px-3.5 py-1.5 text-xs font-medium bg-white hover:bg-slate-100 border border-slate-200 rounded text-slate-700 transition-colors"
            >
              Close Drawer
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { grievanceService } from "@/services/grievanceService";
import { Grievance } from "@/types";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { StatusBadge } from "@/components/common/StatusBadge";
import { PriorityBadge } from "@/components/common/PriorityBadge";
import { ConfirmationDialog } from "@/components/common/ConfirmationDialog";
import { LoadingSkeleton, EmptyState } from "@/components/common/EmptyState";
import { formatDate } from "@/lib/utils";
import {
  CheckSquare,
  ShieldCheck,
  AlertTriangle,
  RotateCcw,
  Sparkles,
  ExternalLink,
  Star,
  FileCheck,
  CheckCircle2,
} from "lucide-react";
import { cn } from "@/lib/utils";

export default function ResolutionVerificationPage() {
  const [grievances, setGrievances] = useState<Grievance[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCase, setSelectedCase] = useState<Grievance | null>(null);
  const [feedbackNotice, setFeedbackNotice] = useState<string | null>(null);

  // Modal actions
  const [confirmModalOpen, setConfirmModalOpen] = useState(false);
  const [actionType, setActionType] = useState<"approve" | "reopen" | "more_evidence">("approve");

  useEffect(() => {
    async function load() {
      setLoading(true);
      const all = await grievanceService.getAll();
      // Filter cases in resolution_submitted, closed or reopened
      const relevant = all.filter(
        (g) =>
          g.status === "resolution_submitted" ||
          g.status === "closed" ||
          g.status === "reopened"
      );
      setGrievances(relevant);
      if (relevant.length > 0) setSelectedCase(relevant[0]);
      setLoading(false);
    }
    load();
  }, []);

  const handleExecuteAction = async () => {
    if (!selectedCase) return;

    if (actionType === "approve") {
      await grievanceService.updateStatus(selectedCase.id, "closed", "Administrative verification completed: Ground-truth audit approved.", "Apex Auditor");
      setFeedbackNotice(`Case ${selectedCase.id} verified and officially closed.`);
    } else if (actionType === "reopen") {
      await grievanceService.updateStatus(selectedCase.id, "reopened", "Administrative verification failed: Inconsistent photographic proof. Reopened.", "Apex Auditor");
      setFeedbackNotice(`Case ${selectedCase.id} rejected and reopened for field correction.`);
    } else {
      setFeedbackNotice(`Additional proof of work requested from assigned officer for ${selectedCase.id}.`);
    }

    setConfirmModalOpen(false);
    const refreshed = await grievanceService.getAll();
    setGrievances(refreshed.filter((g) => g.status === "resolution_submitted" || g.status === "closed" || g.status === "reopened"));
    setTimeout(() => setFeedbackNotice(null), 4000);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Resolution Quality & Ground-Truth Verification"
        subtitle="Independent supervisory audit evaluating photographic evidence, AI consistency validation, and citizen satisfaction ratings before official closure."
        breadcrumbs={[
          { label: "Admin Portal", href: "/admin" },
          { label: "Resolution Verification", active: true },
        ]}
        badge="Zero-Tolerance Audit"
      />

      {feedbackNotice && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-md font-medium flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          {feedbackNotice}
        </div>
      )}

      {loading ? (
        <LoadingSkeleton count={3} />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Verification Queue (4 cols) */}
          <div className="lg:col-span-4 space-y-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-700 font-mono block">
              Auditable Case Queue ({grievances.length})
            </span>

            <div className="space-y-2.5">
              {grievances.map((g) => {
                const isSelected = selectedCase?.id === g.id;
                return (
                  <div
                    key={g.id}
                    onClick={() => setSelectedCase(g)}
                    className={cn(
                      "p-4 rounded-lg border text-xs cursor-pointer transition-all shadow-subtle",
                      isSelected
                        ? "bg-white border-blue-500 ring-2 ring-blue-100 shadow-card"
                        : "bg-white border-slate-200 hover:bg-slate-50"
                    )}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-mono font-bold text-slate-800">{g.id}</span>
                      <StatusBadge status={g.status} />
                    </div>

                    <h4 className="font-bold text-slate-900 line-clamp-1">{g.title}</h4>
                    <p className="text-[11px] text-slate-500 mt-1 truncate">{g.departmentName}</p>

                    <div className="mt-2 pt-2 border-t border-slate-100 flex items-center justify-between text-[10px] font-mono text-slate-400">
                      <span>AI Verification: 95%</span>
                      {g.resolutionReport?.citizenFeedbackRating && (
                        <span className="text-amber-600 font-bold flex items-center gap-0.5">
                          ★ {g.resolutionReport.citizenFeedbackRating}/5
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right Column: In-depth Verification Audit Dossier (8 cols) */}
          <div className="lg:col-span-8 space-y-6">
            {selectedCase && (
              <div className="bg-white rounded-lg border border-slate-200 p-6 shadow-subtle space-y-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
                  <div>
                    <span className="text-xs font-mono font-bold text-blue-600">
                      Case File: {selectedCase.id}
                    </span>
                    <h2 className="text-base font-bold text-slate-900 mt-0.5">
                      {selectedCase.title}
                    </h2>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => {
                        setActionType("approve");
                        setConfirmModalOpen(true);
                      }}
                      className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded text-xs font-semibold shadow-subtle flex items-center gap-1.5"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      Approve Closure
                    </button>
                    <button
                      onClick={() => {
                        setActionType("reopen");
                        setConfirmModalOpen(true);
                      }}
                      className="px-3 py-1.5 bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 rounded text-xs font-semibold flex items-center gap-1"
                    >
                      <RotateCcw className="w-3.5 h-3.5" />
                      Reject & Reopen
                    </button>
                  </div>
                </div>

                {/* AI Ground-Truth Consistency Card */}
                <div className="p-4 rounded-lg bg-blue-50/70 border border-blue-200 space-y-2 text-xs text-blue-900">
                  <div className="flex items-center justify-between">
                    <span className="font-bold flex items-center gap-1.5">
                      <Sparkles className="w-4 h-4 text-blue-600" />
                      AI Visual & Semantic Consistency Analysis
                    </span>
                    <span className="font-mono font-bold text-emerald-700 bg-white px-2 py-0.5 rounded border border-blue-200">
                      95.4% Consistency Score
                    </span>
                  </div>
                  <p className="text-blue-800 leading-relaxed text-[11px]">
                    Computer vision embedding confirms asphalt restoration texture corresponds directly with previous pothole coordinates at Pillar 42. No visual residue of oil spillage or structural depression remains.
                  </p>
                </div>

                {/* Compare Original Complaint vs Officer Report */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                  <div className="p-4 rounded-lg bg-slate-50 border border-slate-200 space-y-2">
                    <span className="font-bold text-slate-900 uppercase font-mono text-[10px] block">
                      Original Citizen Statement
                    </span>
                    <p className="text-slate-700 leading-relaxed max-h-36 overflow-y-auto">
                      {selectedCase.description}
                    </p>
                    <div className="pt-2 text-[11px] text-slate-500 font-mono">
                      Filed: {formatDate(selectedCase.submittedAt)}
                    </div>
                  </div>

                  <div className="p-4 rounded-lg bg-emerald-50/40 border border-emerald-200 space-y-2">
                    <span className="font-bold text-emerald-950 uppercase font-mono text-[10px] block">
                      Field Officer Resolution Report
                    </span>
                    <p className="text-emerald-900 leading-relaxed max-h-36 overflow-y-auto">
                      {selectedCase.resolutionReport?.text || "Work completed on site by maintenance division."}
                    </p>
                    <div className="pt-2 text-[11px] text-emerald-800 font-mono">
                      Resolved: {formatDate(selectedCase.resolutionReport?.resolvedAt || selectedCase.updatedAt)}
                    </div>
                  </div>
                </div>

                {/* Citizen Feedback Rating */}
                {selectedCase.resolutionReport?.citizenFeedbackRating && (
                  <div className="p-4 rounded-lg bg-amber-50/60 border border-amber-200 text-xs text-amber-900 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-bold">Citizen Verified Review</span>
                      <div className="flex items-center gap-1 text-amber-600 font-bold">
                        <Star className="w-4 h-4 fill-amber-400" />
                        <span>{selectedCase.resolutionReport.citizenFeedbackRating} / 5 Stars</span>
                      </div>
                    </div>
                    {selectedCase.resolutionReport.citizenFeedbackComment && (
                      <p className="text-amber-800 italic">
                        "{selectedCase.resolutionReport.citizenFeedbackComment}"
                      </p>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Confirmation Dialog */}
      <ConfirmationDialog
        open={confirmModalOpen}
        type={actionType === "approve" ? "success" : "danger"}
        title={
          actionType === "approve"
            ? "Approve Closure of Grievance?"
            : "Reject Resolution & Reopen Complaint?"
        }
        description={
          actionType === "approve"
            ? `Confirm that case ${selectedCase?.id} has been satisfactorily executed and verified on site.`
            : `Reopen case ${selectedCase?.id} and dispatch corrective work order to supervisory division.`
        }
        confirmLabel={actionType === "approve" ? "Authorize Closure" : "Reject & Reopen"}
        onConfirm={handleExecuteAction}
        onCancel={() => setConfirmModalOpen(false)}
      />
    </div>
  );
}

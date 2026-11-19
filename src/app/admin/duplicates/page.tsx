"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { duplicateService } from "@/services/duplicateService";
import { grievanceService } from "@/services/grievanceService";
import { DuplicateCluster, Grievance } from "@/types";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { ConfirmationDialog } from "@/components/common/ConfirmationDialog";
import { StatusBadge } from "@/components/common/StatusBadge";
import { PriorityBadge } from "@/components/common/PriorityBadge";
import { LoadingSkeleton, EmptyState } from "@/components/common/EmptyState";
import { formatDate } from "@/lib/utils";
import {
  Copy,
  CheckCircle2,
  XCircle,
  Share2,
  AlertTriangle,
  ArrowRight,
  GitMerge,
  MapPin,
  Clock,
  Sparkles,
  Info,
} from "lucide-react";
import { cn } from "@/lib/utils";

export default function DuplicateIntelligenceCenterPage() {
  const [clusters, setClusters] = useState<DuplicateCluster[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCluster, setSelectedCluster] = useState<DuplicateCluster | null>(null);
  const [clusterGrievances, setClusterGrievances] = useState<Grievance[]>([]);

  // Dialog state
  const [mergeDialogOpen, setMergeDialogOpen] = useState(false);
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false);
  const [actionFeedback, setActionFeedback] = useState<string | null>(null);

  useEffect(() => {
    async function loadClusters() {
      setLoading(true);
      const data = await duplicateService.getClusters();
      setClusters(data);
      if (data.length > 0) {
        setSelectedCluster(data[0]);
        const gList = await duplicateService.getClusterGrievances(data[0]);
        setClusterGrievances(gList);
      }
      setLoading(false);
    }
    loadClusters();
  }, []);

  const handleSelectCluster = async (c: DuplicateCluster) => {
    setSelectedCluster(c);
    const gList = await duplicateService.getClusterGrievances(c);
    setClusterGrievances(gList);
  };

  const handleApproveMerge = async () => {
    if (!selectedCluster) return;
    await duplicateService.approveMerge(selectedCluster.id, selectedCluster.masterGrievanceId);
    setMergeDialogOpen(false);
    setActionFeedback(`Cluster ${selectedCluster.clusterCode} merged under Master ${selectedCluster.masterGrievanceId}. Subordinate submitters notified.`);
    // Refresh clusters
    const updated = await duplicateService.getClusters();
    setClusters(updated);
    setTimeout(() => setActionFeedback(null), 4000);
  };

  const handleRejectDuplicate = async () => {
    if (!selectedCluster) return;
    await duplicateService.rejectDuplicate(selectedCluster.id);
    setRejectDialogOpen(false);
    setActionFeedback(`Cluster ${selectedCluster.clusterCode} rejected. Complaints confirmed as independent incidents.`);
    const updated = await duplicateService.getClusters();
    setClusters(updated);
    setTimeout(() => setActionFeedback(null), 4000);
  };

  const masterGrievance = clusterGrievances.find((g) => g.id === selectedCluster?.masterGrievanceId) || clusterGrievances[0];
  const candidateGrievance = clusterGrievances.find((g) => g.id !== selectedCluster?.masterGrievanceId) || clusterGrievances[1] || masterGrievance;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Duplicate Intelligence Center"
        subtitle="AI-assisted cross-encoder clustering of repetitive complaints with semantic similarity metrics, GPS proximity verification, and human-in-the-loop merge authorization."
        breadcrumbs={[
          { label: "Admin Portal", href: "/admin" },
          { label: "Duplicate Intelligence", active: true },
        ]}
        badge="Semantic Radar Active"
      />

      {actionFeedback && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-md font-medium flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          {actionFeedback}
        </div>
      )}

      {/* Human-in-the-loop governance reminder */}
      <div className="p-3.5 bg-blue-50/80 border border-blue-200 rounded-md flex items-start gap-3 text-xs text-blue-900">
        <Info className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">Human-in-the-Loop Governance Standard</span>
          <p className="mt-0.5 text-blue-800 leading-relaxed">
            In compliance with open municipal standards, CivicMind AI generates duplicate recommendations and similarity matrices, but <strong>never merges or suppresses citizen grievances automatically</strong> without deliberate administrative verification.
          </p>
        </div>
      </div>

      {loading ? (
        <LoadingSkeleton count={3} />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Duplicate Clusters List (4 cols) */}
          <div className="lg:col-span-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-900 uppercase tracking-wider font-mono">
                Active Clusters ({clusters.length})
              </span>
              <span className="text-[10px] text-slate-400 font-mono">SBERT Cross-Encoder</span>
            </div>

            <div className="space-y-2.5">
              {clusters.map((c) => {
                const isSelected = selectedCluster?.id === c.id;
                return (
                  <div
                    key={c.id}
                    onClick={() => handleSelectCluster(c)}
                    className={cn(
                      "p-4 rounded-lg border text-xs cursor-pointer transition-all shadow-subtle",
                      isSelected
                        ? "bg-white border-blue-500 ring-2 ring-blue-100 shadow-card"
                        : "bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50/60"
                    )}
                  >
                    <div className="flex items-center justify-between gap-1 mb-1">
                      <span className="font-mono font-bold text-slate-900">{c.clusterCode}</span>
                      <span
                        className={cn(
                          "px-2 py-0.5 rounded text-[10px] font-mono font-bold",
                          c.status === "merged"
                            ? "bg-purple-50 text-purple-700 border border-purple-200"
                            : c.status === "rejected"
                            ? "bg-slate-100 text-slate-600 border border-slate-200"
                            : "bg-amber-50 text-amber-800 border border-amber-200"
                        )}
                      >
                        {c.status.toUpperCase()}
                      </span>
                    </div>

                    <h4 className="font-bold text-slate-800 line-clamp-1">{c.title}</h4>

                    <div className="mt-2.5 pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500 font-mono">
                      <span>{c.grievanceIds.length} Linked Complaints</span>
                      <span className="text-blue-600 font-bold">
                        {Math.round(c.similarityScore * 100)}% Sim
                      </span>
                      <span>{c.geographicProximityMeters}m dist</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right Column: Side-by-Side Comparison & Actions (8 cols) */}
          <div className="lg:col-span-8 space-y-6">
            {selectedCluster && (
              <div className="bg-white rounded-lg border border-slate-200 p-6 shadow-subtle space-y-6">
                {/* Cluster Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-blue-600">
                        {selectedCluster.clusterCode}
                      </span>
                      <span className="text-xs font-bold text-slate-800">• {selectedCluster.category}</span>
                    </div>
                    <h2 className="text-base font-bold text-slate-900 mt-0.5">
                      {selectedCluster.title}
                    </h2>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      disabled={selectedCluster.status === "merged"}
                      onClick={() => setMergeDialogOpen(true)}
                      className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white rounded text-xs font-semibold shadow-subtle transition-colors flex items-center gap-1.5"
                    >
                      <GitMerge className="w-3.5 h-3.5" />
                      Approve Merge
                    </button>
                    <button
                      disabled={selectedCluster.status === "rejected"}
                      onClick={() => setRejectDialogOpen(true)}
                      className="px-3 py-1.5 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 rounded text-xs font-semibold shadow-subtle transition-colors"
                    >
                      Reject Duplicate
                    </button>
                  </div>
                </div>

                {/* AI Recommendation Box */}
                <div className="p-3.5 bg-blue-50/60 rounded border border-blue-200/80 text-xs text-blue-900 space-y-1.5">
                  <div className="flex items-center gap-1.5 font-bold">
                    <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                    AI Consolidation Recommendation:
                  </div>
                  <p className="leading-relaxed text-blue-800">
                    {selectedCluster.aiMergeRecommendation}
                  </p>
                  <ul className="list-disc list-inside text-[11px] text-blue-700 space-y-0.5 pt-1">
                    {selectedCluster.reasons.map((r, i) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                </div>

                {/* SIDE-BY-SIDE COMPLAINT COMPARISON */}
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3 font-mono">
                    Side-by-Side Incident Comparison View
                  </h3>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Master Complaint Box */}
                    <div className="p-4 rounded-lg border-2 border-blue-200 bg-blue-50/20 space-y-3 text-xs">
                      <div className="flex items-center justify-between pb-2 border-b border-blue-100">
                        <span className="font-bold text-blue-900 uppercase font-mono text-[10px] bg-blue-100 px-2 py-0.5 rounded">
                          Master Grievance (Primary)
                        </span>
                        <span className="font-mono font-bold text-slate-700">
                          {masterGrievance.id}
                        </span>
                      </div>

                      <h4 className="font-bold text-slate-900 leading-snug">
                        {masterGrievance.title}
                      </h4>

                      <div className="p-2.5 rounded bg-white border border-slate-200 text-slate-700 leading-relaxed max-h-32 overflow-y-auto">
                        {masterGrievance.description}
                      </div>

                      <div className="space-y-1 text-[11px] text-slate-600">
                        <div>
                          Location: <strong>{masterGrievance.location.address}</strong>
                        </div>
                        <div>
                          Citizen: <strong>{masterGrievance.citizenName}</strong>
                        </div>
                        <div>
                          Filed: <strong className="font-mono">{formatDate(masterGrievance.submittedAt)}</strong>
                        </div>
                      </div>

                      <Link
                        href={`/admin/grievances/${masterGrievance.id}`}
                        className="inline-flex items-center gap-1 text-[11px] text-blue-600 hover:underline font-semibold pt-1"
                      >
                        Inspect Master Record →
                      </Link>
                    </div>

                    {/* Candidate Duplicate Box */}
                    <div className="p-4 rounded-lg border border-slate-300 bg-slate-50/50 space-y-3 text-xs">
                      <div className="flex items-center justify-between pb-2 border-b border-slate-200">
                        <span className="font-bold text-amber-900 uppercase font-mono text-[10px] bg-amber-100 px-2 py-0.5 rounded">
                          Candidate Duplicate
                        </span>
                        <span className="font-mono font-bold text-slate-700">
                          {candidateGrievance.id}
                        </span>
                      </div>

                      <h4 className="font-bold text-slate-900 leading-snug">
                        {candidateGrievance.title}
                      </h4>

                      <div className="p-2.5 rounded bg-white border border-slate-200 text-slate-700 leading-relaxed max-h-32 overflow-y-auto">
                        {candidateGrievance.description}
                      </div>

                      <div className="space-y-1 text-[11px] text-slate-600">
                        <div>
                          Location: <strong>{candidateGrievance.location.address}</strong>
                        </div>
                        <div>
                          Citizen: <strong>{candidateGrievance.citizenName}</strong>
                        </div>
                        <div>
                          Filed: <strong className="font-mono">{formatDate(candidateGrievance.submittedAt)}</strong>
                        </div>
                      </div>

                      <Link
                        href={`/admin/grievances/${candidateGrievance.id}`}
                        className="inline-flex items-center gap-1 text-[11px] text-blue-600 hover:underline font-semibold pt-1"
                      >
                        Inspect Candidate Record →
                      </Link>
                    </div>
                  </div>
                </div>

                {/* Similarity Metrics Breakdown */}
                <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-3 text-xs">
                  <span className="font-bold text-slate-900 uppercase tracking-wider block font-mono text-[11px]">
                    Multi-Modal Similarity Evidence Metrics
                  </span>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <div className="bg-white p-2.5 rounded border border-slate-200">
                      <span className="text-slate-400 text-[10px] uppercase font-mono block">Cosine Semantic</span>
                      <span className="text-sm font-bold text-blue-600 font-mono">
                        {(selectedCluster.similarityScore).toFixed(2)}
                      </span>
                    </div>
                    <div className="bg-white p-2.5 rounded border border-slate-200">
                      <span className="text-slate-400 text-[10px] uppercase font-mono block">GPS Proximity</span>
                      <span className="text-sm font-bold text-slate-900 font-mono">
                        {selectedCluster.geographicProximityMeters}m
                      </span>
                    </div>
                    <div className="bg-white p-2.5 rounded border border-slate-200">
                      <span className="text-slate-400 text-[10px] uppercase font-mono block">Temporal Gap</span>
                      <span className="text-sm font-bold text-slate-900 font-mono">
                        {selectedCluster.timeSpanHours} Hours
                      </span>
                    </div>
                    <div className="bg-white p-2.5 rounded border border-slate-200">
                      <span className="text-slate-400 text-[10px] uppercase font-mono block">Category Match</span>
                      <span className="text-sm font-bold text-emerald-600 font-mono">
                        100% Exact
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Confirmation Dialogs */}
      <ConfirmationDialog
        open={mergeDialogOpen}
        type="info"
        title="Authorize Duplicate Cluster Consolidation?"
        description={`This action will consolidate all ${selectedCluster?.grievanceIds.length} complaints in ${selectedCluster?.clusterCode} under Master Grievance ${selectedCluster?.masterGrievanceId}. Submitting citizens will automatically receive synchronized status updates.`}
        confirmLabel="Confirm & Merge Complaints"
        onConfirm={handleApproveMerge}
        onCancel={() => setMergeDialogOpen(false)}
      />

      <ConfirmationDialog
        open={rejectDialogOpen}
        type="warning"
        title="Reject Duplicate Suggestion?"
        description="Mark this cluster as independent non-duplicate complaints. Each case will remain separate in the department dispatch queue."
        confirmLabel="Confirm Independent Cases"
        onConfirm={handleRejectDuplicate}
        onCancel={() => setRejectDialogOpen(false)}
      />
    </div>
  );
}

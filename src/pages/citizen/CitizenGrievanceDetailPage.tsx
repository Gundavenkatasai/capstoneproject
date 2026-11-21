import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { grievanceService } from "@/services/grievanceService";
import { Grievance } from "@/types";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { StatusBadge } from "@/components/common/StatusBadge";
import { PriorityBadge } from "@/components/common/PriorityBadge";
import { ComplaintTimeline } from "@/components/common/ComplaintTimeline";
import { AIInsightPanel } from "@/components/common/AIInsightPanel";
import { LoadingSkeleton, EmptyState } from "@/components/common/EmptyState";
import { formatDate } from "@/lib/utils";
import {
  MapPin,
  Clock,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  Star,
  Paperclip,
  Shield,
  Building,
} from "lucide-react";

export default function CitizenGrievanceDetailPage() {
  const params = useParams();
  const id = params?.id as string;
  const navigate = useNavigate();

  const [grievance, setGrievance] = useState<Grievance | null>(null);
  const [loading, setLoading] = useState(true);

  // Verification & feedback state
  const [rating, setRating] = useState(5);
  const [feedbackComment, setFeedbackComment] = useState("");
  const [isVerifying, setIsVerifying] = useState(false);
  const [appealReason, setAppealReason] = useState("");
  const [showAppealForm, setShowAppealForm] = useState(false);

  useEffect(() => {
    async function fetchGrievance() {
      setLoading(true);
      const data = await grievanceService.getById(id);
      setGrievance(data);
      setLoading(false);
    }
    fetchGrievance();
  }, [id]);

  const handleVerify = async (approved: boolean) => {
    if (!grievance) return;
    setIsVerifying(true);
    const updated = await grievanceService.verifyResolution(
      grievance.id,
      approved,
      {
        rating,
        comment: approved ? feedbackComment : appealReason,
      },
      "Citizen"
    );
    setGrievance(updated);
    setIsVerifying(false);
    setShowAppealForm(false);
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <LoadingSkeleton count={3} />
      </div>
    );
  }

  if (!grievance) {
    return (
      <EmptyState
        title="Grievance Record Not Found"
        description="The requested complaint identifier does not exist or you lack access permissions."
        actionLabel="Back to Complaints"
        onAction={() => navigate("/citizen/grievances")}
      />
    );
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <PageHeader
        title={grievance.title}
        subtitle={`Grievance ID: ${grievance.id} • Registered via CivicMind Citizen Portal`}
        breadcrumbs={[
          { label: "Citizen Portal", href: "/citizen/dashboard" },
          { label: "My Grievances", href: "/citizen/grievances" },
          { label: grievance.id, active: true },
        ]}
        actions={
          <div className="flex items-center gap-2">
            <StatusBadge status={grievance.status} />
            <PriorityBadge priority={grievance.priority} />
          </div>
        }
      />

      {/* RESOLUTION VERIFICATION BANNER IF IN RESOLUTION_SUBMITTED STATE */}
      {grievance.status === "resolution_submitted" && (
        <div className="p-5 rounded-lg bg-emerald-50 border border-emerald-200 shadow-subtle space-y-4">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center font-bold">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-emerald-950">
                  Officer Has Reported This Issue Resolved
                </h3>
                <p className="text-xs text-emerald-800 mt-0.5">
                  Please review the officer's work report and either verify satisfactory resolution or file an appeal.
                </p>
              </div>
            </div>
            <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold">
              Citizen Verification Required
            </span>
          </div>

          {grievance.resolutionReport && (
            <div className="p-3.5 bg-white rounded border border-emerald-200/80 text-xs text-slate-700">
              <span className="font-semibold text-slate-900 block mb-1">
                Official Officer Resolution Notes:
              </span>
              <p className="leading-relaxed">{grievance.resolutionReport.text}</p>
            </div>
          )}

          {!showAppealForm ? (
            <div className="bg-white/80 p-4 rounded border border-emerald-200/70 space-y-3">
              <span className="text-xs font-semibold text-slate-900 block">
                Rate the Quality of Resolution:
              </span>
              <div className="flex items-center gap-1.5">
                {[1, 2, 3, 4, 5].map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => setRating(s)}
                    className="p-1 hover:scale-110 transition-transform"
                  >
                    <Star
                      className={`w-5 h-5 ${
                        s <= rating ? "text-amber-400 fill-amber-400" : "text-slate-300"
                      }`}
                    />
                  </button>
                ))}
                <span className="text-xs font-semibold text-slate-700 ml-2">
                  ({rating} out of 5 stars)
                </span>
              </div>

              <div>
                <label className="block text-xs text-slate-600 mb-1">
                  Optional Feedback Comment:
                </label>
                <input
                  type="text"
                  value={feedbackComment}
                  onChange={(e) => setFeedbackComment(e.target.value)}
                  placeholder="e.g. Cleaned thoroughly, thank you for quick action."
                  className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded"
                />
              </div>

              <div className="flex items-center justify-between pt-2">
                <button
                  type="button"
                  onClick={() => setShowAppealForm(true)}
                  className="text-xs text-red-600 hover:text-red-800 font-semibold"
                >
                  Issue Not Fixed? File Citizen Appeal →
                </button>

                <button
                  type="button"
                  disabled={isVerifying}
                  onClick={() => handleVerify(true)}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded text-xs shadow-subtle transition-colors"
                >
                  {isVerifying ? "Confirming..." : "Confirm & Accept Resolution (Close)"}
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-white p-4 rounded border border-red-200 space-y-3">
              <span className="text-xs font-bold text-red-900 block">
                Citizen Appeal / Reject Resolution:
              </span>
              <p className="text-xs text-slate-600">
                State why the issue remains unresolved. This will automatically reopen the grievance and escalate it to the Senior Zonal Officer.
              </p>
              <textarea
                rows={3}
                value={appealReason}
                onChange={(e) => setAppealReason(e.target.value)}
                placeholder="Explain what was missed (e.g. water is still leaking, pothole was not filled completely)..."
                className="w-full px-3 py-2 text-xs border border-red-200 rounded text-slate-900 focus:outline-none focus:ring-1 focus:ring-red-500"
              />
              <div className="flex items-center justify-between pt-1">
                <button
                  type="button"
                  onClick={() => setShowAppealForm(false)}
                  className="text-xs text-slate-500 hover:text-slate-800"
                >
                  Cancel Appeal
                </button>
                <button
                  type="button"
                  disabled={isVerifying || !appealReason}
                  onClick={() => handleVerify(false)}
                  className="px-3.5 py-1.5 bg-red-600 hover:bg-red-700 text-white rounded text-xs font-bold shadow-subtle transition-colors"
                >
                  {isVerifying ? "Submitting Appeal..." : "Reject Resolution & Reopen"}
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Grid of Key Properties */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-white p-3.5 rounded border border-slate-200">
          <span className="text-[10px] font-mono text-slate-400 uppercase block">Department</span>
          <span className="text-xs font-bold text-slate-900 mt-1 block truncate">
            {grievance.departmentName}
          </span>
        </div>
        <div className="bg-white p-3.5 rounded border border-slate-200">
          <span className="text-[10px] font-mono text-slate-400 uppercase block">Assigned Officer</span>
          <span className="text-xs font-bold text-slate-900 mt-1 block truncate">
            {grievance.assignedOfficerName || "In Auto-Routing"}
          </span>
        </div>
        <div className="bg-white p-3.5 rounded border border-slate-200">
          <span className="text-[10px] font-mono text-slate-400 uppercase block">Target SLA Deadline</span>
          <span className="text-xs font-bold text-slate-900 mt-1 block font-mono">
            {formatDate(grievance.slaDeadline)}
          </span>
        </div>
        <div className="bg-white p-3.5 rounded border border-slate-200">
          <span className="text-[10px] font-mono text-slate-400 uppercase block">Location</span>
          <span className="text-xs font-bold text-slate-900 mt-1 block truncate">
            {grievance.location.address}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Details & Timeline */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-subtle space-y-4">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
              Grievance Description & Context
            </h3>
            <div className="p-3.5 bg-slate-50 rounded border border-slate-200 text-xs text-slate-700 leading-relaxed whitespace-pre-wrap">
              {grievance.description}
            </div>

            {grievance.evidence && grievance.evidence.length > 0 && (
              <div>
                <span className="text-xs font-semibold text-slate-700 block mb-2">
                  Uploaded Evidence ({grievance.evidence.length})
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {grievance.evidence.map((ev) => (
                    <a
                      key={ev.id}
                      href={ev.url}
                      target="_blank"
                      rel="noreferrer"
                      className="p-2.5 rounded bg-slate-50 border border-slate-200 hover:bg-slate-100 flex items-center justify-between text-xs"
                    >
                      <div className="flex items-center gap-2 truncate">
                        <Paperclip className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                        <span className="font-medium text-slate-700 truncate">{ev.name}</span>
                      </div>
                      <span className="text-[10px] font-mono text-slate-400 flex-shrink-0">
                        {ev.size}
                      </span>
                    </a>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Timeline */}
          <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-subtle space-y-4">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
              Real-Time Activity Timeline
            </h3>
            <ComplaintTimeline events={grievance.timeline} />
          </div>
        </div>

        {/* Right Col: AI Analysis & Location Pin */}
        <div className="space-y-6">
          <AIInsightPanel grievance={grievance} />

          <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-subtle space-y-3">
            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-red-500" />
              Geographic Pin & Ward
            </h4>
            <div className="p-3 bg-slate-50 rounded text-xs space-y-1">
              <p className="font-semibold text-slate-800">{grievance.location.address}</p>
              <p className="text-slate-500 font-mono text-[11px]">
                {grievance.location.ward} • {grievance.location.zone}
              </p>
              <p className="text-slate-400 font-mono text-[10px]">
                GPS: {grievance.location.lat.toFixed(4)}, {grievance.location.lng.toFixed(4)}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

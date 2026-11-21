import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { grievanceService } from "@/services/grievanceService";
import { Grievance, GrievanceStatus } from "@/types";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { StatusBadge } from "@/components/common/StatusBadge";
import { PriorityBadge } from "@/components/common/PriorityBadge";
import { ComplaintTimeline } from "@/components/common/ComplaintTimeline";
import { AIInsightPanel } from "@/components/common/AIInsightPanel";
import { LoadingSkeleton, EmptyState } from "@/components/common/EmptyState";
import { formatDate } from "@/lib/utils";
import {
  Wrench,
  CheckCircle2,
  AlertTriangle,
  Upload,
  FileText,
  MapPin,
  Clock,
  Shield,
  Send,
  Building,
} from "lucide-react";

export default function OfficerGrievanceActionPage() {
  const params = useParams();
  const id = params?.id as string;
  const navigate = useNavigate();

  const [grievance, setGrievance] = useState<Grievance | null>(null);
  const [loading, setLoading] = useState(true);

  // Form states
  const [internalNote, setInternalNote] = useState("");
  const [resolutionText, setResolutionText] = useState("");
  const [evidenceUrl, setEvidenceUrl] = useState("https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=600&auto=format&fit=crop&q=80");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedbackMsg, setFeedbackMsg] = useState<string | null>(null);

  // Reassignment modal
  const [showReassignModal, setShowReassignModal] = useState(false);
  const [reassignDept, setReassignDept] = useState("dept_pwd");
  const [reassignReason, setReassignReason] = useState("");

  useEffect(() => {
    async function fetchGrievance() {
      setLoading(true);
      const data = await grievanceService.getById(id);
      setGrievance(data);
      setLoading(false);
    }
    fetchGrievance();
  }, [id]);

  const handleUpdateStatus = async (newStatus: GrievanceStatus) => {
    if (!grievance) return;
    setIsSubmitting(true);
    const updated = await grievanceService.updateStatus(
      grievance.id,
      newStatus,
      internalNote || `Officer updated status to ${newStatus}`,
      "Duty Officer"
    );
    setGrievance(updated);
    setInternalNote("");
    setIsSubmitting(false);
    setFeedbackMsg(`Status successfully transitioned to ${newStatus.toUpperCase()}`);
    setTimeout(() => setFeedbackMsg(null), 3000);
  };

  const handleSubmitResolutionReport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!grievance || !resolutionText) return;
    setIsSubmitting(true);
    const updated = await grievanceService.submitResolution(
      grievance.id,
      {
        text: resolutionText,
        officerEvidence: [evidenceUrl],
      },
      "Er. Rajesh Verma (Field Officer)"
    );
    setGrievance(updated);
    setIsSubmitting(false);
    setFeedbackMsg("Resolution report successfully submitted for citizen sign-off!");
    setTimeout(() => setFeedbackMsg(null), 3000);
  };

  const handleReassign = async () => {
    if (!grievance || !reassignReason) return;
    setIsSubmitting(true);
    const updated = await grievanceService.reassignDepartment(
      grievance.id,
      reassignDept,
      reassignReason,
      "Duty Officer"
    );
    setGrievance(updated);
    setIsSubmitting(false);
    setShowReassignModal(false);
    setFeedbackMsg("Reassignment request processed.");
    setTimeout(() => setFeedbackMsg(null), 3000);
  };

  if (loading) return <LoadingSkeleton count={3} />;
  if (!grievance) {
    return (
      <EmptyState
        title="Grievance Not Found"
        description="The grievance record could not be found."
        actionLabel="Back to Assigned Caseload"
        onAction={() => navigate("/officer/assigned")}
      />
    );
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <PageHeader
        title={grievance.title}
        subtitle={`Case ID: ${grievance.id} • Assigned to ${grievance.departmentName}`}
        breadcrumbs={[
          { label: "Officer Portal", href: "/officer/dashboard" },
          { label: "Assigned Caseload", href: "/officer/assigned" },
          { label: grievance.id, active: true },
        ]}
        actions={
          <div className="flex items-center gap-2">
            <StatusBadge status={grievance.status} />
            <PriorityBadge priority={grievance.priority} />
          </div>
        }
      />

      {feedbackMsg && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-md font-medium flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          {feedbackMsg}
        </div>
      )}

      {/* OFFICER INTERACTIVE ACTION PANEL */}
      <div className="bg-white rounded-lg border border-blue-200 p-5 shadow-card space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded bg-blue-600 text-white flex items-center justify-center font-bold text-xs">
              <Wrench className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                Field Officer Action Console
              </h3>
              <p className="text-[11px] text-slate-500">Update case lifecycle or submit resolution report</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {grievance.status === "assigned" && (
              <button
                type="button"
                disabled={isSubmitting}
                onClick={() => handleUpdateStatus("in_progress")}
                className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded shadow-subtle transition-colors"
              >
                Accept & Start Field Work
              </button>
            )}

            <button
              type="button"
              onClick={() => setShowReassignModal(true)}
              className="px-3 py-1.5 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 text-xs font-medium rounded transition-colors"
            >
              Request Department Reassignment
            </button>
          </div>
        </div>

        {/* Submit Resolution Form */}
        <form onSubmit={handleSubmitResolutionReport} className="space-y-3 pt-1">
          <label className="block text-xs font-bold text-slate-800">
            Submit Officer Resolution Report & Photo Evidence
          </label>
          <textarea
            rows={3}
            required
            value={resolutionText}
            onChange={(e) => setResolutionText(e.target.value)}
            placeholder="Document corrective actions taken, materials applied, team dispatched, and final ground condition..."
            className="w-full px-3 py-2 text-xs border border-slate-200 rounded text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                Proof of Work Photo URL / Reference
              </label>
              <input
                type="text"
                value={evidenceUrl}
                onChange={(e) => setEvidenceUrl(e.target.value)}
                className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded text-slate-900"
              />
            </div>
            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                Internal Case Log Notes (Optional)
              </label>
              <input
                type="text"
                value={internalNote}
                onChange={(e) => setInternalNote(e.target.value)}
                placeholder="Log internal crew ID, truck #, contractor name..."
                className="w-full px-3 py-1.5 text-xs border border-slate-200 rounded text-slate-900"
              />
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <button
              type="submit"
              disabled={isSubmitting || !resolutionText}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white text-xs font-bold rounded shadow-subtle transition-colors flex items-center gap-1.5"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              {isSubmitting ? "Submitting..." : "Submit Official Resolution for Citizen Verification"}
            </button>
          </div>
        </form>
      </div>

      {/* Grievance Details & AI Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Citizen Description Card */}
          <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-subtle space-y-3">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
              Citizen Statement & Field Coordinates
            </h3>
            <div className="p-3.5 bg-slate-50 rounded border border-slate-200 text-xs text-slate-700 leading-relaxed whitespace-pre-wrap">
              {grievance.description}
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-600 pt-1">
              <MapPin className="w-4 h-4 text-red-500 flex-shrink-0" />
              <span>{grievance.location.address} ({grievance.location.ward})</span>
            </div>
          </div>

          {/* Timeline */}
          <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-subtle space-y-3">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
              Operational Timeline
            </h3>
            <ComplaintTimeline events={grievance.timeline} />
          </div>
        </div>

        {/* Right Rail: AI Insights */}
        <div className="space-y-6">
          <AIInsightPanel grievance={grievance} />

          <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-subtle space-y-2 text-xs">
            <span className="font-bold text-slate-900 uppercase block">Citizen Contact Details</span>
            <p className="text-slate-700">
              Name: <strong>{grievance.isAnonymous ? "Anonymous Resident" : grievance.citizenName}</strong>
            </p>
            {grievance.citizenPhone && (
              <p className="text-slate-700 font-mono">
                Phone: <strong>{grievance.citizenPhone}</strong>
              </p>
            )}
            <p className="text-slate-400 text-[11px] pt-1">
              SLA Countdown: {formatDate(grievance.slaDeadline)}
            </p>
          </div>
        </div>
      </div>

      {/* Reassignment Modal */}
      {showReassignModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
          <div className="bg-white rounded-lg shadow-elevated border border-slate-200 p-6 max-w-md w-full space-y-4">
            <h3 className="text-sm font-bold text-slate-900">
              Department Reassignment Request
            </h3>
            <p className="text-xs text-slate-600">
              If this incident does not fall under your department's jurisdiction, select the appropriate authority.
            </p>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Target Department
              </label>
              <select
                value={reassignDept}
                onChange={(e) => setReassignDept(e.target.value)}
                className="w-full px-3 py-2 text-xs border border-slate-200 rounded"
              >
                <option value="dept_pwd">Public Works Department (PWD)</option>
                <option value="dept_wssb">Water Supply & Sewerage Board</option>
                <option value="dept_swm">Solid Waste Management</option>
                <option value="dept_elec">Urban Electricity & Street Lighting</option>
                <option value="dept_health">Public Health & Sanitation</option>
                <option value="dept_parks">Parks & Horticulture</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Justification / Reason
              </label>
              <textarea
                rows={3}
                required
                value={reassignReason}
                onChange={(e) => setReassignReason(e.target.value)}
                placeholder="e.g. Pipeline leak is on private colony connection, requires water board excavation crew..."
                className="w-full px-3 py-2 text-xs border border-slate-200 rounded"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShowReassignModal(false)}
                className="px-3 py-1.5 border border-slate-200 text-slate-700 rounded text-xs"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={!reassignReason}
                onClick={handleReassign}
                className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-semibold"
              >
                Confirm Reassignment
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

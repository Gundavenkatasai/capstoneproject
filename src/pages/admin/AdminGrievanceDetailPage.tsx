import React, { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { grievanceService } from "@/services/grievanceService";
import { Grievance, GrievanceStatus } from "@/types";
import { PageHeader } from "@/components/common/Breadcrumbs";
import { StatusBadge } from "@/components/common/StatusBadge";
import { PriorityBadge } from "@/components/common/PriorityBadge";
import { ConfidenceIndicator } from "@/components/common/ConfidenceIndicator";
import { ComplaintTimeline } from "@/components/common/ComplaintTimeline";
import { AIInsightPanel } from "@/components/common/AIInsightPanel";
import { LoadingSkeleton, EmptyState } from "@/components/common/EmptyState";
import { formatDate } from "@/lib/utils";
import {
  FileText,
  Sparkles,
  Copy,
  Clock,
  Paperclip,
  TrendingUp,
  ScrollText,
  MapPin,
  Building,
  User,
  Shield,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  ExternalLink,
} from "lucide-react";
import { cn } from "@/lib/utils";

type TabKey =
  | "overview"
  | "ai_analysis"
  | "similar"
  | "timeline"
  | "evidence"
  | "prediction"
  | "audit_history";

export default function AdminGrievanceDetailPage() {
  const params = useParams();
  const id = params?.id as string;
  const navigate = useNavigate();

  const [grievance, setGrievance] = useState<Grievance | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabKey>("overview");

  // Reassignment & Status modal states
  const [statusModalOpen, setStatusModalOpen] = useState(false);
  const [newStatus, setNewStatus] = useState<GrievanceStatus>("in_progress");
  const [statusNotes, setStatusNotes] = useState("");

  const [reassignModalOpen, setReassignModalOpen] = useState(false);
  const [targetDept, setTargetDept] = useState("dept_pwd");
  const [reassignReason, setReassignReason] = useState("");

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await grievanceService.getById(id);
      setGrievance(data);
      setLoading(false);
    }
    load();
  }, [id]);

  const handleUpdateStatus = async () => {
    if (!grievance) return;
    const updated = await grievanceService.updateStatus(
      grievance.id,
      newStatus,
      statusNotes || `Administrator updated status to ${newStatus}`,
      "Apex Administrator"
    );
    setGrievance(updated);
    setStatusModalOpen(false);
    setStatusNotes("");
  };

  const handleReassign = async () => {
    if (!grievance || !reassignReason) return;
    const updated = await grievanceService.reassignDepartment(
      grievance.id,
      targetDept,
      reassignReason,
      "Apex Administrator"
    );
    setGrievance(updated);
    setReassignModalOpen(false);
    setReassignReason("");
  };

  if (loading) return <LoadingSkeleton count={3} />;
  if (!grievance) {
    return (
      <EmptyState
        title="Grievance Record Not Found"
        description="The grievance identifier could not be retrieved from the central registry."
        actionLabel="Back to All Grievances"
        onAction={() => navigate("/admin/grievances")}
      />
    );
  }

  const tabs: Array<{ key: TabKey; label: string; icon: React.ComponentType<{ className?: string }> }> = [
    { key: "overview", label: "Overview", icon: FileText },
    { key: "ai_analysis", label: "AI Analysis", icon: Sparkles },
    { key: "similar", label: "Similar Complaints", icon: Copy },
    { key: "timeline", label: "Timeline", icon: Clock },
    { key: "evidence", label: "Evidence", icon: Paperclip },
    { key: "prediction", label: "Prediction", icon: TrendingUp },
    { key: "audit_history", label: "Audit History", icon: ScrollText },
  ];

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <PageHeader
        title={grievance.title}
        subtitle={`Grievance Master Record: ${grievance.id} • Registered ${formatDate(grievance.submittedAt)}`}
        breadcrumbs={[
          { label: "Admin Portal", href: "/admin" },
          { label: "All Grievances", href: "/admin/grievances" },
          { label: grievance.id, active: true },
        ]}
        actions={
          <div className="flex items-center gap-2">
            <StatusBadge status={grievance.status} />
            <PriorityBadge priority={grievance.priority} />
            <button
              onClick={() => setStatusModalOpen(true)}
              className="px-3 py-1.5 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 text-xs font-semibold rounded shadow-subtle transition-colors ml-2"
            >
              Update Status
            </button>
            <button
              onClick={() => setReassignModalOpen(true)}
              className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded shadow-subtle transition-colors"
            >
              Reassign Dept
            </button>
          </div>
        }
      />

      {/* Tabs Navigation Header */}
      <div className="border-b border-slate-200 bg-white rounded-t-lg shadow-subtle px-4">
        <nav className="flex space-x-6 overflow-x-auto text-xs font-semibold">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.key;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={cn(
                  "py-3 px-1 border-b-2 inline-flex items-center gap-2 transition-colors whitespace-nowrap",
                  isActive
                    ? "border-blue-600 text-blue-600"
                    : "border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300"
                )}
              >
                <Icon className={cn("w-3.5 h-3.5", isActive ? "text-blue-600" : "text-slate-400")} />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* TAB 1: OVERVIEW */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-white p-3.5 rounded border border-slate-200">
              <span className="text-[10px] uppercase font-mono text-slate-400 block">Department</span>
              <p className="font-semibold text-slate-900 mt-1">{grievance.departmentName}</p>
            </div>
            <div className="bg-white p-3.5 rounded border border-slate-200">
              <span className="text-[10px] uppercase font-mono text-slate-400 block">Assigned Officer</span>
              <p className="font-semibold text-slate-900 mt-1">
                {grievance.assignedOfficerName || "Auto-Dispatching..."}
              </p>
            </div>
            <div className="bg-white p-3.5 rounded border border-slate-200">
              <span className="text-[10px] uppercase font-mono text-slate-400 block">SLA Target</span>
              <p className="font-semibold text-slate-900 mt-1 font-mono">
                {formatDate(grievance.slaDeadline)}
              </p>
            </div>
            <div className="bg-white p-3.5 rounded border border-slate-200">
              <span className="text-[10px] uppercase font-mono text-slate-400 block">Ward Jurisdiction</span>
              <p className="font-semibold text-slate-900 mt-1">{grievance.location.ward}</p>
            </div>
          </div>

          <div className="bg-white rounded-lg border border-slate-200 p-6 space-y-4">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
              Citizen Statement & Location
            </h3>
            <div className="p-4 bg-slate-50 rounded border border-slate-200 text-xs text-slate-700 leading-relaxed whitespace-pre-wrap">
              {grievance.description}
            </div>
            <div className="p-3 bg-slate-50 rounded border border-slate-200 text-xs flex items-center justify-between">
              <div className="flex items-center gap-2 text-slate-700">
                <MapPin className="w-4 h-4 text-red-500" />
                <span className="font-medium">{grievance.location.address}</span>
              </div>
              <span className="font-mono text-[11px] text-slate-400">
                [{grievance.location.lat.toFixed(4)}, {grievance.location.lng.toFixed(4)}]
              </span>
            </div>
          </div>

          {/* Quick AI Snippet */}
          <AIInsightPanel grievance={grievance} />
        </div>
      )}

      {/* TAB 2: AI ANALYSIS */}
      {activeTab === "ai_analysis" && (
        <div className="space-y-6">
          <AIInsightPanel grievance={grievance} />

          {/* Semantic Routing Decision Trace */}
          <div className="bg-white rounded-lg border border-slate-200 p-6 space-y-4">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
              Routing Decision Trace & Lexical Matches
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="p-3.5 bg-slate-50 rounded border border-slate-200 space-y-2">
                <span className="font-semibold text-slate-800 block">Matched Civic Ontology Keywords</span>
                <div className="flex flex-wrap gap-1.5">
                  {(grievance.routingTrace?.keywordsMatched || ["pipeline", "rupture", "flooding"]).map((kw, i) => (
                    <span key={i} className="px-2 py-0.5 rounded bg-blue-100 text-blue-800 font-mono text-[11px]">
                      "{kw}"
                    </span>
                  ))}
                </div>
              </div>

              <div className="p-3.5 bg-slate-50 rounded border border-slate-200 space-y-2">
                <span className="font-semibold text-slate-800 block">Department Fit Score</span>
                <div className="flex items-center gap-2">
                  <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
                    <div
                      className="bg-emerald-500 h-full rounded-full"
                      style={{ width: `${Math.round((grievance.routingTrace?.departmentFitScore || 0.94) * 100)}%` }}
                    />
                  </div>
                  <span className="font-mono font-bold text-emerald-700">
                    {Math.round((grievance.routingTrace?.departmentFitScore || 0.94) * 100)}%
                  </span>
                </div>
                <p className="text-[11px] text-slate-500">
                  Second Choice: {grievance.routingTrace?.secondChoiceDepartment || "Public Works Department"} (52% fit)
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: SIMILAR COMPLAINTS */}
      {activeTab === "similar" && (
        <div className="bg-white rounded-lg border border-slate-200 p-6 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h3 className="text-sm font-bold text-slate-900">
                Spatial & Semantic Duplicate Cluster
              </h3>
              <p className="text-xs text-slate-500">Cross-encoder vector similarity matching within 1.0 km radius</p>
            </div>
            <Link
              to="/admin/duplicates"
              className="text-xs text-blue-600 hover:text-blue-800 font-semibold"
            >
              Open Duplicate Intelligence Center →
            </Link>
          </div>

          <div className="space-y-3">
            <div className="p-4 rounded bg-slate-50 border border-slate-200 flex items-center justify-between text-xs">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono font-bold text-slate-900">GRV-2026-8933</span>
                  <span className="font-mono text-emerald-700 font-bold bg-emerald-50 px-1.5 py-0.2 rounded border border-emerald-200">
                    89% Semantic Similarity
                  </span>
                  <span className="text-slate-400 font-mono text-[11px]">280m distance</span>
                </div>
                <p className="font-semibold text-slate-800 mt-1">Non-potable muddy water supply coming from municipal taps</p>
                <p className="text-[11px] text-slate-500">Pocket 7, Sector B, Vasant Kunj, Delhi</p>
              </div>
              <Link
                to="/admin/grievances/GRV-2026-8933"
                className="px-2.5 py-1 rounded bg-white hover:bg-slate-100 border border-slate-200 font-medium text-slate-700"
              >
                Inspect
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: TIMELINE */}
      {activeTab === "timeline" && (
        <div className="bg-white rounded-lg border border-slate-200 p-6 space-y-4">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
            Complete Grievance Lifecycle Trace
          </h3>
          <ComplaintTimeline events={grievance.timeline} />
        </div>
      )}

      {/* TAB 5: EVIDENCE */}
      {activeTab === "evidence" && (
        <div className="bg-white rounded-lg border border-slate-200 p-6 space-y-4">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
            Citizen & Officer Evidence Files
          </h3>

          {grievance.evidence && grievance.evidence.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {grievance.evidence.map((ev) => (
                <div key={ev.id} className="p-4 rounded-lg border border-slate-200 bg-slate-50 space-y-3">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-slate-900 truncate">{ev.name}</span>
                    <span className="font-mono text-[10px] text-slate-400">({ev.size})</span>
                  </div>
                  {ev.type === "image" && (
                    <div className="h-44 rounded bg-slate-200 overflow-hidden">
                      <img src={ev.url} alt={ev.name} className="w-full h-full object-cover" />
                    </div>
                  )}
                  <a
                    href={ev.url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-blue-600 hover:underline font-semibold"
                  >
                    Open Full High-Resolution File <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-400 italic">No evidence attachments filed.</p>
          )}
        </div>
      )}

      {/* TAB 6: PREDICTION */}
      {activeTab === "prediction" && (
        <div className="bg-white rounded-lg border border-slate-200 p-6 space-y-5">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
            Predictive Model Telemetry (LightGBM & DeBERTa)
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div className="p-3.5 bg-slate-50 rounded border border-slate-200">
              <span className="text-slate-400 font-mono text-[10px] uppercase block">Predicted Duration</span>
              <p className="text-lg font-bold text-slate-900 mt-1 font-mono">
                {grievance.predictedDurationDays} Days
              </p>
              <p className="text-[10px] text-slate-400">Model MAE: ±0.68 days</p>
            </div>

            <div className="p-3.5 bg-slate-50 rounded border border-slate-200">
              <span className="text-slate-400 font-mono text-[10px] uppercase block">SLA Breach Risk Tier</span>
              <p className="text-lg font-bold text-amber-700 mt-1 uppercase font-mono">
                {grievance.slaBreachRisk}
              </p>
              <p className="text-[10px] text-slate-400">Probability: 68%</p>
            </div>

            <div className="p-3.5 bg-slate-50 rounded border border-slate-200">
              <span className="text-slate-400 font-mono text-[10px] uppercase block">Cluster ID</span>
              <p className="text-xs font-bold text-slate-900 mt-1 font-mono">
                {grievance.duplicateClusterId || "None (Unique Incident)"}
              </p>
              <p className="text-[10px] text-slate-400">Similarity: {Math.round(grievance.duplicateProbability * 100)}%</p>
            </div>
          </div>
        </div>
      )}

      {/* TAB 7: AUDIT HISTORY */}
      {activeTab === "audit_history" && (
        <div className="bg-white rounded-lg border border-slate-200 p-6 space-y-4">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
            Cryptographic Audit Ledger & State Changes
          </h3>
          <div className="divide-y divide-slate-100 text-xs">
            <div className="py-2.5 flex items-center justify-between">
              <div>
                <p className="font-semibold text-slate-800">STATE_MUTATION: in_progress</p>
                <p className="text-[11px] text-slate-400">By Field Officer Er. Rajesh Verma</p>
              </div>
              <span className="font-mono text-[10px] text-slate-400">2026-11-19T06:30:00Z</span>
            </div>
            <div className="py-2.5 flex items-center justify-between">
              <div>
                <p className="font-semibold text-slate-800">AI_TRIAGE_CLASSIFIED</p>
                <p className="text-[11px] text-slate-400">Model CivicDeBERTa-v4.2 confidence 0.96</p>
              </div>
              <span className="font-mono text-[10px] text-slate-400">2026-11-18T08:15:12Z</span>
            </div>
            <div className="py-2.5 flex items-center justify-between">
              <div>
                <p className="font-semibold text-slate-800">GRIEVANCE_INGESTED</p>
                <p className="text-[11px] text-slate-400">Citizen Mobile Web submission</p>
              </div>
              <span className="font-mono text-[10px] text-slate-400">2026-11-18T08:15:00Z</span>
            </div>
          </div>
        </div>
      )}

      {/* Status Modal */}
      {statusModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
          <div className="bg-white rounded-lg p-6 max-w-md w-full shadow-elevated border border-slate-200 space-y-4">
            <h3 className="text-sm font-bold text-slate-900">Administrator Status Transition</h3>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">New Status</label>
              <select
                value={newStatus}
                onChange={(e) => setNewStatus(e.target.value as any)}
                className="w-full px-3 py-2 text-xs border border-slate-200 rounded"
              >
                <option value="in_progress">In Progress</option>
                <option value="resolution_submitted">Resolution Submitted</option>
                <option value="closed">Closed</option>
                <option value="escalated">Escalated</option>
                <option value="reopened">Reopened</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Audit Notes</label>
              <input
                type="text"
                value={statusNotes}
                onChange={(e) => setStatusNotes(e.target.value)}
                placeholder="Reason for manual administrative transition..."
                className="w-full px-3 py-2 text-xs border border-slate-200 rounded"
              />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setStatusModalOpen(false)}
                className="px-3 py-1.5 border border-slate-200 rounded text-xs text-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={handleUpdateStatus}
                className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-semibold"
              >
                Apply State Transition
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Reassign Modal */}
      {reassignModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
          <div className="bg-white rounded-lg p-6 max-w-md w-full shadow-elevated border border-slate-200 space-y-4">
            <h3 className="text-sm font-bold text-slate-900">Inter-Departmental Reassignment</h3>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Target Department</label>
              <select
                value={targetDept}
                onChange={(e) => setTargetDept(e.target.value)}
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
              <label className="block text-xs font-semibold text-slate-700 mb-1">Administrative Justification</label>
              <textarea
                rows={3}
                required
                value={reassignReason}
                onChange={(e) => setReassignReason(e.target.value)}
                placeholder="Specify the inter-departmental mandate or misrouting correction..."
                className="w-full px-3 py-2 text-xs border border-slate-200 rounded"
              />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setReassignModalOpen(false)}
                className="px-3 py-1.5 border border-slate-200 rounded text-xs text-slate-700"
              >
                Cancel
              </button>
              <button
                disabled={!reassignReason}
                onClick={handleReassign}
                className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-semibold"
              >
                Authorize Reassignment
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

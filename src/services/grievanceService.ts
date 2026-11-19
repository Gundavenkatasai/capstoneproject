import {
  Grievance,
  GrievanceStatus,
  GrievancePriority,
  ResolutionReport,
} from "@/types";
import { MOCK_GRIEVANCES, MOCK_DEPARTMENTS } from "@/mocks/mockData";
import { mockDelay, USE_MOCK, apiClient } from "./apiClient";

// Local in-memory store for state mutations during user session
let localGrievances: Grievance[] = [...MOCK_GRIEVANCES];

export interface GrievanceFilterParams {
  search?: string;
  status?: string;
  priority?: string;
  departmentId?: string;
  category?: string;
  ward?: string;
  slaBreachRisk?: string;
  citizenId?: string;
  assignedOfficerId?: string;
}

export const grievanceService = {
  async getAll(params?: GrievanceFilterParams): Promise<Grievance[]> {
    if (!USE_MOCK) {
      try {
        const response = await apiClient.get<Grievance[]>("/grievances", { params });
        return response.data;
      } catch (err) {
        console.warn("API request failed, falling back to local dataset:", err);
      }
    }

    let filtered = [...localGrievances];
    if (params) {
      if (params.search) {
        const q = params.search.toLowerCase();
        filtered = filtered.filter(
          (g) =>
            g.id.toLowerCase().includes(q) ||
            g.title.toLowerCase().includes(q) ||
            g.description.toLowerCase().includes(q) ||
            g.location.address.toLowerCase().includes(q) ||
            g.citizenName.toLowerCase().includes(q)
        );
      }
      if (params.status && params.status !== "all") {
        filtered = filtered.filter((g) => g.status === params.status);
      }
      if (params.priority && params.priority !== "all") {
        filtered = filtered.filter((g) => g.priority === params.priority);
      }
      if (params.departmentId && params.departmentId !== "all") {
        filtered = filtered.filter((g) => g.departmentId === params.departmentId);
      }
      if (params.category && params.category !== "all") {
        filtered = filtered.filter((g) => g.category.toLowerCase().includes(params.category!.toLowerCase()));
      }
      if (params.ward && params.ward !== "all") {
        filtered = filtered.filter((g) => g.location.ward === params.ward);
      }
      if (params.citizenId) {
        filtered = filtered.filter((g) => g.citizenId === params.citizenId);
      }
      if (params.assignedOfficerId) {
        filtered = filtered.filter((g) => g.assignedOfficerId === params.assignedOfficerId);
      }
    }

    return mockDelay(filtered, 150);
  },

  async getById(id: string): Promise<Grievance | null> {
    if (!USE_MOCK) {
      try {
        const response = await apiClient.get<Grievance>(`/grievances/${id}`);
        return response.data;
      } catch (err) {
        console.warn("API request failed, checking local dataset:", err);
      }
    }

    const item = localGrievances.find((g) => g.id === id) || null;
    return mockDelay(item, 100);
  },

  async create(newGrievanceData: Partial<Grievance>): Promise<Grievance> {
    const id = `GRV-2026-${Math.floor(1000 + Math.random() * 9000)}`;
    const now = new Date().toISOString();

    const created: Grievance = {
      id,
      title: newGrievanceData.title || "Citizen Grievance",
      description: newGrievanceData.description || "",
      citizenId: newGrievanceData.citizenId || "usr_citizen_1",
      citizenName: newGrievanceData.citizenName || "Aarav Sharma",
      category: newGrievanceData.category || "General Municipal Services",
      subcategory: newGrievanceData.subcategory || "Other Civic Issue",
      departmentId: newGrievanceData.departmentId || "dept_pwd",
      departmentName: newGrievanceData.departmentName || "Public Works Department (PWD)",
      location: newGrievanceData.location || {
        address: "Civic Center District, Delhi",
        ward: "Ward 14",
        zone: "Central Zone",
        lat: 28.6139,
        lng: 77.209,
      },
      priority: newGrievanceData.priority || "medium",
      status: "submitted",
      aiConfidence: newGrievanceData.aiConfidence || 0.94,
      submittedAt: now,
      updatedAt: now,
      expectedResolutionDate: new Date(Date.now() + 4 * 86400000).toISOString(),
      slaDeadline: new Date(Date.now() + 5 * 86400000).toISOString(),
      slaBreached: false,
      slaBreachRisk: "low",
      duplicateProbability: newGrievanceData.duplicateProbability || 0.08,
      evidence: newGrievanceData.evidence || [],
      timeline: [
        {
          id: `tl_${Date.now()}`,
          status: "submitted",
          title: "Complaint Lodged",
          description: "Registered by citizen via CivicMind AI portal.",
          timestamp: now,
          actor: newGrievanceData.citizenName || "Citizen",
          actorRole: "Citizen",
        },
        {
          id: `tl_ai_${Date.now()}`,
          status: "analyzed",
          title: "AI Semantic Classification",
          description: `Assigned to ${newGrievanceData.departmentName || "Department"} with ${Math.round(
            (newGrievanceData.aiConfidence || 0.94) * 100
          )}% confidence.`,
          timestamp: new Date(Date.now() + 10000).toISOString(),
          actor: "CivicMind NLP Classifier v4.2",
          actorRole: "System AI",
        },
      ],
      predictedDurationDays: 3.5,
      ...newGrievanceData,
    };

    localGrievances.unshift(created);
    return mockDelay(created, 250);
  },

  async updateStatus(
    id: string,
    status: GrievanceStatus,
    notes?: string,
    actor = "Officer"
  ): Promise<Grievance | null> {
    const item = localGrievances.find((g) => g.id === id);
    if (!item) return null;

    item.status = status;
    item.updatedAt = new Date().toISOString();
    item.timeline.push({
      id: `tl_${Date.now()}`,
      status,
      title: `Status updated to ${status.replace("_", " ").toUpperCase()}`,
      description: notes || `Grievance status changed by ${actor}.`,
      timestamp: new Date().toISOString(),
      actor,
      actorRole: "Authority",
      notes,
    });

    return mockDelay({ ...item }, 200);
  },

  async reassignDepartment(
    id: string,
    newDepartmentId: string,
    reason: string,
    actor = "Admin"
  ): Promise<Grievance | null> {
    const item = localGrievances.find((g) => g.id === id);
    if (!item) return null;

    const dept = MOCK_DEPARTMENTS.find((d) => d.id === newDepartmentId);
    item.departmentId = newDepartmentId;
    item.departmentName = dept ? dept.name : newDepartmentId;
    item.updatedAt = new Date().toISOString();
    item.timeline.push({
      id: `tl_${Date.now()}`,
      status: item.status,
      title: `Reassigned to ${item.departmentName}`,
      description: `Department transfer initiated by ${actor}. Reason: ${reason}`,
      timestamp: new Date().toISOString(),
      actor,
      actorRole: "Administrator",
    });

    return mockDelay({ ...item }, 200);
  },

  async submitResolution(
    id: string,
    report: { text: string; officerEvidence: string[] },
    actor = "Field Officer"
  ): Promise<Grievance | null> {
    const item = localGrievances.find((g) => g.id === id);
    if (!item) return null;

    item.status = "resolution_submitted";
    item.actualResolutionDate = new Date().toISOString();
    item.updatedAt = new Date().toISOString();
    item.resolutionReport = {
      text: report.text,
      resolvedAt: new Date().toISOString(),
      officerEvidence: report.officerEvidence,
      aiVerificationConfidence: 0.94,
    };

    item.timeline.push({
      id: `tl_${Date.now()}`,
      status: "resolution_submitted",
      title: "Resolution Report Submitted",
      description: report.text,
      timestamp: new Date().toISOString(),
      actor,
      actorRole: "Department Officer",
    });

    return mockDelay({ ...item }, 250);
  },

  async verifyResolution(
    id: string,
    approved: boolean,
    feedback?: { rating?: number; comment?: string },
    actor = "Citizen"
  ): Promise<Grievance | null> {
    const item = localGrievances.find((g) => g.id === id);
    if (!item) return null;

    if (approved) {
      item.status = "closed";
      if (item.resolutionReport) {
        item.resolutionReport.verifiedByAdmin = true;
        if (feedback?.rating) item.resolutionReport.citizenFeedbackRating = feedback.rating;
        if (feedback?.comment) item.resolutionReport.citizenFeedbackComment = feedback.comment;
      }
      item.timeline.push({
        id: `tl_${Date.now()}`,
        status: "closed",
        title: "Resolution Verified & Closed",
        description: feedback?.comment || "Resolution inspected and accepted.",
        timestamp: new Date().toISOString(),
        actor,
        actorRole: "Citizen / Verifier",
      });
    } else {
      item.status = "reopened";
      item.timeline.push({
        id: `tl_${Date.now()}`,
        status: "reopened",
        title: "Resolution Rejected - Reopened",
        description: feedback?.comment || "Citizen reported incomplete resolution.",
        timestamp: new Date().toISOString(),
        actor,
        actorRole: "Citizen Appeal",
      });
    }

    item.updatedAt = new Date().toISOString();
    return mockDelay({ ...item }, 200);
  },

  // Realistic mock AI Analysis simulation for user complaints
  async analyzeWithAI(text: string, locationStr?: string) {
    await new Promise((r) => setTimeout(r, 600)); // Brief simulated inference

    const lower = text.toLowerCase();
    let predictedCategory = "Public Works Department";
    let predictedSubcategory = "Pothole & Road Deterioration";
    let recommendedDept = "Public Works Department (PWD)";
    let deptId = "dept_pwd";
    let priority: GrievancePriority = "medium";
    let duplicateProbability = 0.08;
    let estimatedDurationDays = 3.5;
    let similarComplaints: Array<{ id: string; title: string; similarity: number; status: string }> = [];

    if (lower.includes("water") || lower.includes("pipe") || lower.includes("sewage") || lower.includes("drain") || lower.includes("leak") || lower.includes("paani")) {
      predictedCategory = "Water Supply & Sanitation";
      predictedSubcategory = lower.includes("sewage") || lower.includes("drain") ? "Sewerage Line Clog & Overflow" : "Pipeline Rupture & Leakage";
      recommendedDept = "Water Supply & Sewerage Board";
      deptId = "dept_wssb";
      priority = lower.includes("burst") || lower.includes("flood") || lower.includes("drinking") ? "critical" : "high";
      duplicateProbability = 0.84;
      estimatedDurationDays = 2.0;
      similarComplaints = [
        { id: "GRV-2026-8941", title: "Major water pipeline rupture causing localized flooding", similarity: 0.89, status: "in_progress" },
        { id: "GRV-2026-8933", title: "Non-potable muddy water supply coming from municipal taps", similarity: 0.74, status: "assigned" },
      ];
    } else if (lower.includes("garbage") || lower.includes("trash") || lower.includes("waste") || lower.includes("dump") || lower.includes("kachra") || lower.includes("safai")) {
      predictedCategory = "Solid Waste Management";
      predictedSubcategory = "Garbage Bin Overflow";
      recommendedDept = "Solid Waste Management";
      deptId = "dept_swm";
      priority = "medium";
      duplicateProbability = 0.22;
      estimatedDurationDays = 1.5;
      similarComplaints = [
        { id: "GRV-2026-8940", title: "Uncollected commercial garbage dump attracting stray animals", similarity: 0.82, status: "resolution_submitted" },
      ];
    } else if (lower.includes("light") || lower.includes("electric") || lower.includes("pole") || lower.includes("dark") || lower.includes("wire") || lower.includes("bijli")) {
      predictedCategory = "Electricity & Street Lighting";
      predictedSubcategory = lower.includes("wire") ? "Sagging / Exposed Live Cables" : "Dark Spots & Failed Fixtures";
      recommendedDept = "Urban Electricity & Street Lighting";
      deptId = "dept_elec";
      priority = lower.includes("wire") || lower.includes("spark") ? "critical" : "high";
      duplicateProbability = 0.42;
      estimatedDurationDays = 2.5;
      similarComplaints = [
        { id: "GRV-2026-8939", title: "12 consecutive streetlights non-functional on Sector Road", similarity: 0.86, status: "in_progress" },
      ];
    } else if (lower.includes("pothole") || lower.includes("road") || lower.includes("traffic") || lower.includes("footpath") || lower.includes("sadak")) {
      predictedCategory = "Roads & Traffic Infrastructure";
      predictedSubcategory = "Pothole & Road Deterioration";
      recommendedDept = "Public Works Department (PWD)";
      deptId = "dept_pwd";
      priority = lower.includes("accident") || lower.includes("injury") ? "high" : "medium";
      duplicateProbability = 0.78;
      estimatedDurationDays = 3.2;
      similarComplaints = [
        { id: "GRV-2026-8942", title: "Severe deep pothole causing two-wheeler accidents at night", similarity: 0.91, status: "assigned" },
      ];
    }

    return {
      summary: text.length > 90 ? text.slice(0, 90) + "..." : text,
      predictedCategory,
      predictedSubcategory,
      recommendedDepartment: recommendedDept,
      departmentId: deptId,
      priority,
      confidence: 0.94,
      duplicateProbability,
      estimatedDurationDays,
      slaDeadline: new Date(Date.now() + (priority === "critical" ? 48 : 96) * 3600000).toISOString(),
      similarComplaints,
      shapExplanation: [
        { feature: `Key lexical terms: "${lower.split(" ").slice(0, 3).join(", ")}"`, weight: 0.45, effect: "positive" as const, description: `Matches ontology for ${predictedCategory}` },
        { feature: `Geographic proximity to active cluster`, weight: 0.32, effect: "positive" as const, description: `Matches historical municipal incidents in zone` },
      ],
    };
  },
};

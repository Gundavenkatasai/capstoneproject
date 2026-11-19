export type UserRole = "citizen" | "officer" | "admin";

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  department?: string;
  phone?: string;
  ward?: string;
  avatar?: string;
  badge?: string;
}

export type GrievanceStatus =
  | "submitted"
  | "analyzed"
  | "assigned"
  | "in_progress"
  | "resolution_submitted"
  | "citizen_verified"
  | "closed"
  | "escalated"
  | "reopened";

export type GrievancePriority = "critical" | "high" | "medium" | "low";

export interface EvidenceItem {
  id: string;
  type: "image" | "document" | "audio";
  url: string;
  name: string;
  size: string;
}

export interface TimelineEvent {
  id: string;
  status: GrievanceStatus;
  title: string;
  description: string;
  timestamp: string;
  actor: string;
  actorRole: string;
  notes?: string;
}

export interface SHAPFactor {
  feature: string;
  weight: number; // positive or negative
  effect: "positive" | "negative";
  description: string;
}

export interface ResolutionReport {
  text: string;
  resolvedAt: string;
  officerEvidence: string[];
  citizenFeedbackRating?: number; // 1 to 5
  citizenFeedbackComment?: string;
  aiVerificationConfidence: number; // 0.0 to 1.0
  flaggedDiscrepancy?: string;
  verifiedByAdmin?: boolean;
}

export interface GrievanceLocation {
  address: string;
  ward: string;
  zone: string;
  lat: number;
  lng: number;
}

export interface Grievance {
  id: string;
  title: string;
  description: string;
  citizenId: string;
  citizenName: string;
  citizenPhone?: string;
  category: string;
  subcategory: string;
  departmentId: string;
  departmentName: string;
  assignedOfficerId?: string;
  assignedOfficerName?: string;
  location: GrievanceLocation;
  priority: GrievancePriority;
  status: GrievanceStatus;
  aiConfidence: number;
  submittedAt: string;
  updatedAt: string;
  expectedResolutionDate: string;
  actualResolutionDate?: string;
  slaDeadline: string;
  slaBreached: boolean;
  slaBreachRisk: "low" | "medium" | "high" | "critical";
  duplicateProbability: number;
  duplicateClusterId?: string;
  isAnonymous?: boolean;
  language?: "en" | "hi" | "hinglish";
  evidence: EvidenceItem[];
  timeline: TimelineEvent[];
  resolutionReport?: ResolutionReport;
  predictedDurationDays: number;
  shapFactors?: SHAPFactor[];
  routingTrace?: {
    keywordsMatched: string[];
    sentimentScore: number;
    recommendedDepartment: string;
    secondChoiceDepartment?: string;
    departmentFitScore: number;
  };
}

export interface Department {
  id: string;
  name: string;
  code: string;
  head: string;
  officerCount: number;
  activeGrievances: number;
  avgResolutionDays: number;
  satisfactionRate: number;
  slaComplianceRate: number;
  zone: string;
  workloadStatus: "optimal" | "heavy" | "critical_overload";
}

export interface Officer {
  id: string;
  name: string;
  email: string;
  phone: string;
  departmentId: string;
  departmentName: string;
  assignedWard: string;
  activeCases: number;
  resolvedThisMonth: number;
  avgResolutionHours: number;
  slaCompliancePct: number;
  status: "active" | "on_field" | "on_leave";
  rating: number;
}

export interface DuplicateCluster {
  id: string;
  clusterCode: string;
  title: string;
  category: string;
  masterGrievanceId: string;
  grievanceIds: string[];
  similarityScore: number;
  geographicProximityMeters: number;
  timeSpanHours: number;
  status: "pending_review" | "merged" | "rejected" | "split";
  aiMergeRecommendation: string;
  reasons: string[];
}

export interface Hotspot {
  id: string;
  title: string;
  category: string;
  zone: string;
  ward: string;
  lat: number;
  lng: number;
  radiusMeters: number;
  complaintCount: number;
  riskLevel: "low" | "medium" | "high" | "critical";
  riskScore: number;
  trend: "increasing" | "stable" | "decreasing";
  summary: string;
  recommendedAction: string;
  relatedComplaintIds: string[];
  detectedAt: string;
  historicalVelocity: number[]; // e.g. last 7 days count
}

export interface KnowledgeGraphNode {
  id: string;
  label: string;
  type: "department" | "category" | "asset" | "jurisdiction" | "procedure" | "officer";
  group: string;
  color?: string;
  properties?: Record<string, any>;
  x?: number;
  y?: number;
}

export interface KnowledgeGraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  relation: "handles" | "located_in" | "related_to" | "escalates_to" | "resolves" | "belongs_to";
}

export interface SimulatorInput {
  additionalOfficers: number;
  departmentCapacityMultiplier: number;
  workloadRedistributionPct: number;
  routingWeightAIFactor: number;
  escalationThresholdHours: number;
}

export interface SimulatorResult {
  currentBacklog: number;
  simulatedBacklog: number;
  currentAvgResolutionDays: number;
  simulatedAvgResolutionDays: number;
  currentSlaBreachRate: number;
  simulatedSlaBreachRate: number;
  departmentWorkload: Array<{
    department: string;
    currentLoad: number;
    projectedLoad: number;
    capacity: number;
  }>;
  summary: string;
}

export interface NotificationItem {
  id: string;
  title: string;
  message: string;
  timestamp: string;
  type: "info" | "warning" | "success" | "critical";
  read: boolean;
  link?: string;
}

export interface AuditLogItem {
  id: string;
  timestamp: string;
  action: string;
  entityType: "grievance" | "officer" | "cluster" | "model" | "system";
  entityId: string;
  performedBy: string;
  userRole: UserRole;
  details: string;
  ipAddress: string;
}

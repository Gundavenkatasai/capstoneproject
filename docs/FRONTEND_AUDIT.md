# Frontend Technical Audit & Codebase Inventory
**Project**: CivicMind AI — AI-Powered Citizen Grievance Intelligence and Resolution Prediction Platform  
**Audit Date**: November 2026  
**Auditor**: Principal Frontend Architect & Senior Product Designer  
**Repository State**: Frontend Complete, Production-Ready, 0 TypeScript Errors, 33 Optimized Routes

---

## 1. Executive Summary

This audit assesses the current state of the CivicMind AI frontend codebase before commencing backend engineering and AI/ML model integration. The frontend has been implemented in Next.js 14 App Router, TypeScript, and Tailwind CSS. It is structured into three role-isolated applications (**Citizen**, **Department Officer**, and **Administrator Intelligence**) along with a public landing page and authentication module.

Currently, all views consume a centralized mock service layer (`src/services/` backed by `src/mocks/mockData.ts`). All forms, tables, metric cards, charts, drawers, and modal dialogs are fully interactive. The application compiles cleanly with zero TypeScript errors (`npx tsc --noEmit` exit code 0) and builds an optimized production bundle (`npm run build` exit code 0).

---

## 2. Technology Stack & Dependencies

| Layer | Technology | Version | Purpose in Application |
|---|---|---|---|
| **Framework** | Next.js (App Router) | `14.2.24` | React server/client rendering, file-based routing |
| **Language** | TypeScript | `^5.6.3` | End-to-end type safety, interfaces |
| **Runtime / UI** | React & React DOM | `^18.3.1` | Component architecture, state hooks |
| **Styling** | Tailwind CSS | `^3.4.15` | Enterprise design tokens, responsive utilities |
| **Class Utilities** | `clsx` & `tailwind-merge` | `^2.1.1` / `^2.5.4` | Dynamic conditional class merging (`cn` helper) |
| **Icons** | Lucide React | `^0.460.0` | Enterprise iconography across all portals |
| **Data Viz** | Recharts | `^2.13.3` | Responsive Area, Bar, Line, and Pie charts |
| **State Management** | Zustand | `^5.0.1` | Client auth state, roles, notifications |
| **HTTP Client** | Axios | `^1.7.7` | Centralized API client with JWT interceptors |
| **Validation** | Zod | `^3.23.8` | Schema validation definitions |
| **Forms** | React Hook Form | `^7.53.2` | Multi-step form controllers & resolvers |
| **Tables** | TanStack React Table | `^8.20.5` | Headless table architecture support |
| **GIS Mapping** | Leaflet & React Leaflet | `^1.9.4` / `^4.2.1` | Interactive GIS city mapping & spatial projection |
| **Animation** | Framer Motion | `^11.11.17` | Restrained UI transitions & slideout drawers |

---

## 3. Directory & File Inventory

```
c:\Users\venka\OneDrive\Desktop\capstone project\
├── .env.local                          # Environment config (API Base URL, Mock toggle)
├── .gitignore                          # Git ignore (node_modules, .next, local envs)
├── next.config.mjs                     # Next.js configuration (images domain whitelist)
├── package.json                        # Node dependencies & execution scripts
├── package-lock.json                   # Deterministic package dependency tree
├── postcss.config.js                   # PostCSS Tailwind plugins
├── tailwind.config.ts                  # Enterprise design tokens (navy, civic, status colors)
├── tsconfig.json                       # Path aliases (@/* -> ./src/*), strict mode
├── README.md                           # Project overview, credentials & setup guide
├── docs/                               # Architectural & integration specifications
│   ├── FRONTEND_AUDIT.md               # [This Document] Comprehensive frontend audit
│   ├── API_REQUIREMENTS.md             # REST API specifications for FastAPI
│   ├── DATABASE_DESIGN.md              # PostgreSQL + pgvector schema & relations
│   ├── SYSTEM_ARCHITECTURE.md          # Full-stack system topology & data pipelines
│   └── IMPLEMENTATION_ROADMAP.md       # Phased backend integration plan
└── src/
    ├── app/                            # Next.js 14 App Router routes (33 routes)
    ├── components/                     # Modular component hierarchy
    │   ├── common/                     # Reusable design system components
    │   ├── layout/                     # Role layout wrappers & headers
    │   └── maps/                       # GIS MapView SVG/Canvas component
    ├── lib/                            # Utility functions (cn, date helpers, exportToCsv)
    ├── mocks/                          # Deterministic municipal mock data
    ├── services/                       # Centralized API service abstractions
    ├── stores/                         # Zustand global state stores
    └── types/                          # Domain TypeScript entity interfaces
```

---

## 4. Route Inventory & Component Mapping

| Route | Page Type | Layout Used | Key Components Rendered | Current Data Source |
|---|---|---|---|---|
| `/` | Public Landing | `PublicHeader` + `PublicFooter` | Hero preview, Pipeline cards, Capabilities, Stats | Static & Inline Demo Telemetry |
| `/login` | Public Auth | Standalone Shell | Role switcher, Form, 1-Click demo accounts | `authService.login()`, `authStore` |
| `/register` | Public Auth | Standalone Shell | Citizen registration form, Ward selector | `authStore.setUser()` |
| `/forgot-password` | Public Auth | Standalone Shell | Email recovery form, Confirmation view | Static Simulated Callback |
| **Citizen Portal** | | | | |
| `/citizen/dashboard` | Portal View | `CitizenLayout` (`AppSidebar`, `AppHeader`) | `MetricCard`, Active progress bar, Recent grievances | `grievanceService.getAll()` |
| `/citizen/submit` | Wizard | `CitizenLayout` | 5-step wizard, Voice UI, Map picker, `AIInsightPanel` | `grievanceService.analyzeWithAI()`, `create()` |
| `/citizen/grievances` | List View | `CitizenLayout` | `SearchInput`, `FilterDropdown`, Status badges | `grievanceService.getAll()` |
| `/citizen/grievances/[id]` | Detail View | `CitizenLayout` | `ComplaintTimeline`, `AIInsightPanel`, Verification form | `grievanceService.getById()`, `verifyResolution()` |
| `/citizen/notifications` | List View | `CitizenLayout` | Notification cards, Unread markers, Direct links | `useNotificationStore` |
| `/citizen/appeals` | List View | `CitizenLayout` | Contested complaints queue, Audit review links | `grievanceService.getAll()` (reopened/escalated) |
| `/citizen/profile` | Form View | `CitizenLayout` | Profile form, Ward selector, Contact editor | `useAuthStore` |
| **Officer Portal** | | | | |
| `/officer/dashboard` | Dashboard | `OfficerLayout` (`AppSidebar`, `AppHeader`) | 6 KPI `MetricCard`s, Priority assigned list | `grievanceService.getAll()` |
| `/officer/assigned` | Data Table | `OfficerLayout` | Caseload table, Filters, `ComplaintDetailDrawer`, CSV | `grievanceService.getAll()` |
| `/officer/grievances/[id]`| Action Console | `OfficerLayout` | Action console, Resolution form, Reassign modal | `grievanceService.getById()`, `submitResolution()` |
| `/officer/escalations` | List View | `OfficerLayout` | SLA breach alerts, Expedite buttons | `grievanceService.getAll()` (breached/escalated) |
| `/officer/performance` | Analytics | `OfficerLayout` | 4 `MetricCard`s, Weekly BarChart, Velocity LineChart | Hardcoded Benchmark Telemetry |
| `/officer/profile` | Detail View | `OfficerLayout` | Official credentials, Ward jurisdiction card | `useAuthStore` |
| **Admin Portal** | | | | |
| `/admin` | Dashboard | `AdminLayout` (`AppSidebar`, `AppHeader`) | 8 KPI cards, 4 Recharts charts, Risk queue | `grievanceService.getAll()`, `earlyWarningService` |
| `/admin/grievances` | Data Table | `AdminLayout` | 12-column table, Multi-filter, Bulk actions, CSV | `grievanceService.getAll()` |
| `/admin/grievances/[id]`| 7-Tab Dossier | `AdminLayout` | Tabs: Overview, AI, Duplicates, Timeline, Evidence, Prediction, Audit | `grievanceService.getById()`, `updateStatus()` |
| `/admin/duplicates` | Comparison | `AdminLayout` | Cluster list, Side-by-side comparison, Merge/Reject | `duplicateService.getClusters()`, `approveMerge()` |
| `/admin/early-warning` | GIS Radar | `AdminLayout` | `MapView`, Hotspot selector, Velocity chart, Dispatch | `earlyWarningService.getHotspots()`, `acknowledge()` |
| `/admin/predictions` | Predictive UI | `AdminLayout` | 4 KPIs, Duration BarChart, Capacity BarChart, SLA Queue | `predictionService.getSlaBreachQueue()`, forecast |
| `/admin/explainability` | XAI Dashboard | `AdminLayout` | Case dropdown, SHAP BarChart, Decision trace | `MOCK_GRIEVANCES` shapFactors |
| `/admin/knowledge-graph`| Graph UI | `AdminLayout` | Interactive SVG graph, Zoom controls, Node details | `knowledgeGraphService.getGraphData()` |
| `/admin/resolution-verification`| Audit UI | `AdminLayout` | Case queue, Original vs Report, Consistency score | `grievanceService.getAll()` |
| `/admin/workload` | Analytics | `AdminLayout` | 4 KPIs, Department BarChart, Staffing scorecard | `MOCK_DEPARTMENTS`, `MOCK_OFFICERS` |
| `/admin/simulator` | Sandbox | `AdminLayout` | 5 Range sliders, Outcome cards, Before/After chart | `simulatorService.runSimulation()` |
| `/admin/models` | Research | `AdminLayout` | Confusion matrix, Classification, Regression metrics | `MOCK_RESEARCH_METRICS` |
| `/admin/datasets` | Explorer | `AdminLayout` | 4 KPIs, Language PieChart, Provenance metadata | `MOCK_RESEARCH_METRICS.datasetStats` |
| `/admin/experiments` | Benchmarks | `AdminLayout` | Model comparisons BarChart, Architecture specs | Hardcoded Experiment Trial Array |
| `/admin/audit-logs` | Data Table | `AdminLayout` | Audit table, Entity filter, Search, CSV export | `MOCK_AUDIT_LOGS`, `exportToCsv()` |
| `/admin/settings` | Settings Form | `AdminLayout` | API URL input, Mock toggle, Test connectivity button | React local state |

---

## 5. Audit of All Forms & Expected Backend Operations

| Page Route | Form Description | Form Fields | Client-side Validation | Target Backend API Operation | Expected Request Payload | Expected Response Payload |
|---|---|---|---|---|---|---|
| `/login` | User Authentication | Email, Password, Role, RememberMe | Valid email format, min 6 char password | `POST /api/v1/auth/login` | `{ email, password, role }` | `{ user: User, token: string }` |
| `/register` | Citizen Registration | Full Name, Email, Phone, Ward, Password | All required, phone regex | `POST /api/v1/auth/register` | `{ name, email, phone, ward, password }` | `{ user: User, token: string }` |
| `/forgot-password` | Password Recovery | Email | Email format | `POST /api/v1/auth/forgot-password` | `{ email }` | `{ success: boolean, message: string }` |
| `/citizen/submit` | Multi-Step Wizard (Step 1-5) | Title, Statement, Language, Anonymous, Address, Ward, Zone, Lat, Lng, Category, Subcategory, Files | Min 15 chars statement, valid coordinates | `POST /api/v1/grievances` | Multipart form or JSON with evidence file IDs | `Grievance` entity with ID, status `submitted` |
| `/citizen/submit` (Step 1 blur) | AI Real-Time Triage | Text description, Address string | Min 15 chars | `POST /api/v1/ai/triage-preview` | `{ text: string, location_text?: string }` | `{ predictedCategory, subcategory, recommendedDepartment, priority, confidence, similarComplaints: [], estimatedDurationDays }` |
| `/citizen/grievances/[id]` | Citizen Verification Form | Rating (1-5), Feedback comment | Rating required if approving | `POST /api/v1/grievances/{id}/verify` | `{ approved: true, rating: number, comment?: string }` | Updated `Grievance` (status `closed`) |
| `/citizen/grievances/[id]` | Citizen Appeal Form | Appeal justification | Required text | `POST /api/v1/grievances/{id}/appeal` | `{ reason: string }` | Updated `Grievance` (status `reopened`) |
| `/citizen/profile` | Citizen Profile Editor | Name, Phone, Ward | Valid phone format | `PUT /api/v1/users/me` | `{ name, phone, ward }` | Updated `User` object |
| `/officer/grievances/[id]` | Status Transition | New status, Internal note | Status enum | `PATCH /api/v1/grievances/{id}/status` | `{ status: GrievanceStatus, notes?: string }` | Updated `Grievance` |
| `/officer/grievances/[id]` | Resolution Report Submission | Resolution text, Evidence photo URL/upload, Internal note | Required resolution text | `POST /api/v1/grievances/{id}/resolution` | `{ report_text: string, evidence_urls: string[], notes?: string }` | Updated `Grievance` (status `resolution_submitted`) |
| `/officer/grievances/[id]` | Reassignment Request | Target department ID, Justification text | Required reason | `POST /api/v1/grievances/{id}/reassign` | `{ target_department_id: string, reason: string }` | Updated `Grievance` |
| `/admin/grievances/[id]` | Admin Status Override Modal | New status, Audit notes | Status enum | `PATCH /api/v1/grievances/{id}/status` | `{ status: GrievanceStatus, notes: string }` | Updated `Grievance` |
| `/admin/grievances/[id]` | Admin Reassign Department | Target department ID, Administrative justification | Required justification | `POST /api/v1/grievances/{id}/reassign` | `{ target_department_id: string, justification: string }` | Updated `Grievance` |
| `/admin/duplicates` | Approve Cluster Merge | Master grievance ID, Cluster ID | Admin confirmation | `POST /api/v1/duplicates/clusters/{id}/merge` | `{ master_grievance_id: string }` | Updated `DuplicateCluster` (status `merged`) |
| `/admin/duplicates` | Reject Duplicate Cluster | Cluster ID, Optional reason | Admin confirmation | `POST /api/v1/duplicates/clusters/{id}/reject` | `{ reason?: string }` | Updated `DuplicateCluster` (status `rejected`) |
| `/admin/early-warning` | Acknowledge Hotspot / Dispatch | Hotspot ID, Operational notes | None | `POST /api/v1/early-warning/hotspots/{id}/acknowledge` | `{ notes?: string }` | Updated `Hotspot` record |
| `/admin/simulator` | Workload Simulator Input | 5 Slider inputs (officers, capacity, redistribution, AI weight, threshold) | Slider step constraints | `POST /api/v1/simulator/simulate` | `SimulatorInput` schema | `SimulatorResult` schema |
| `/admin/settings` | System Settings & Health Check | API Gateway URL, Mock Toggle | Valid URL format | `GET /api/v1/health` (Ping) | None | `{ status: "ok", version: string, database: "connected" }` |

---

## 6. Audit of Dashboards, Metrics, Charts, Filters, and Tables

### 6.1. Metric Cards Inventory
- **Citizen Dashboard**:
  1. `Total Complaints Filed` (Count)
  2. `In Resolution Pipeline` (Pending status count)
  3. `Successfully Resolved` (Closed / Verified count)
  4. `Action Required` (Complaints with status `resolution_submitted`)
- **Officer Dashboard**:
  1. `Assigned Cases` (Total officer caseload)
  2. `Pending Action` (`submitted` / `assigned` count)
  3. `In Progress` (`in_progress` count)
  4. `Resolved (Mtd)` (Monthly completed count)
  5. `Overdue SLA` (`slaBreached == true` count)
  6. `High/Critical` (`priority in ['critical', 'high']` count)
- **Officer Performance**:
  1. `Citizen Satisfaction` (Average rating e.g., 4.8 / 5.0)
  2. `SLA Compliance Rate` (Percentage e.g., 94.2%)
  3. `Avg Resolution Speed` (Hours e.g., 42 Hours)
  4. `Resolved This Month` (Case count)
- **Admin Intelligence Overview**:
  1. `Total Caseload` (Total complaints in system)
  2. `Pending Queue` (Open/active complaints)
  3. `Resolved` (Closed complaints)
  4. `High Priority` (Critical/High triage count)
  5. `Duplicates` (Complaints with duplicateProbability > 0.6)
  6. `Mean Days` (Average predicted/actual duration e.g., 3.4d)
  7. `SLA Breaches` (Breached or critical risk count)
  8. `Radar Hotspots` (Active geographic clusters)
- **Predictive Analytics**:
  1. `Predicted SLA Breaches` (Flagged imminent breach count)
  2. `Overall Model MAE` (Duration error e.g., 0.68 Days)
  3. `Forecast Overload Depts` (Departments > 100% capacity)
  4. `PR-AUC Accuracy` (Precision-Recall score e.g., 0.904)
- **Explainable AI (XAI)**:
  1. `Predicted Category` (e.g., Water Supply)
  2. `AI Confidence` (Percentage e.g., 96.4%)
  3. `Recommended Dept` (Code e.g., WSSB)
  4. `Triage Priority` (e.g., Critical)
- **Workload Management**:
  1. `Total Field Officers` (Headcount across divisions)
  2. `Active Municipal Backlog` (Cases)
  3. `Bottleneck Department` (Overloaded department)
  4. `Optimal Department` (Highest compliance department)
- **Simulator Outcomes**:
  1. `Active Backlog` (Baseline vs Simulated projection)
  2. `Avg Resolution Speed` (Baseline vs Projected duration)
  3. `Projected SLA Breach Rate` (Baseline vs Simulated %)
- **Model Performance**:
  1. `Overall Accuracy`, `Macro Precision`, `Macro Recall`, `Macro F1-Score`
  2. `Precision@K`, `Recall@K`, `Duplicate F1`, `mAP Score`
  3. `MAE`, `RMSE`, `MedAE`, `R²`
  4. `Breach Precision`, `Breach Recall`, `PR-AUC`, `Brier Score`
- **Dataset Explorer**:
  1. `Total Corpus Records` (142,500)
  2. `Supervised Labeled Set` (138,200)
  3. `Geographic Wards Covered` (64)
  4. `Corpus Integrity` (99.4%)
- **Experiments**:
  1. `Leading Model` (DeBERTa-v4.2)
  2. `Accuracy Improvement` (+13.4% over baseline)
  3. `Inference Latency` (42 ms)
  4. `Model Parameter Size` (125M)

---

### 6.2. Interactive Charts Inventory

| Page Route | Chart Title | Chart Type | Library Used | Data Dimension / Series |
|---|---|---|---|---|
| `/admin` | Grievance Submission & Resolution Trend | AreaChart | Recharts | Incoming complaints vs Resolved cases over time |
| `/admin` | Complaint Distribution by Category | PieChart | Recharts | Category shares (% breakdown, 5 colored segments) |
| `/admin` | Department Active Load vs Capacity | BarChart | Recharts | Active Backlog vs Resolved MTD across 6 departments |
| `/officer/performance` | Weekly Case Throughput | BarChart | Recharts | Incoming vs Resolved by day of week (Mon-Sun) |
| `/officer/performance` | Historical Resolution Time Trend | LineChart | Recharts | Average resolution hours per month (Jun-Nov) |
| `/admin/early-warning` | Incident Inundation Velocity | LineChart | Recharts | Complaints per day across 6 time slices for selected hotspot |
| `/admin/predictions` | Actual vs Predicted Resolution Duration | BarChart | Recharts | Actual Mean Days vs Predicted Mean Days per category |
| `/admin/predictions` | Projected 7-Day Capacity Utilization | BarChart | Recharts | Capacity % per department (identifying >100% strains) |
| `/admin/explainability` | SHAP Feature Importance & Contribution | Horizontal BarChart | Recharts | Shapley values (-0.10 to +0.45) for tokens & spatial attributes |
| `/admin/workload` | Department Backlog vs Field Officer Distribution | BarChart | Recharts | Active Complaints vs Officer Headcount by department code |
| `/admin/simulator` | Department Caseload: Baseline vs Simulated | BarChart | Recharts | Current Load vs Projected Load vs Capacity per department |
| `/admin/datasets` | Language Representation in Corpus | PieChart | Recharts | English (58%), Hindi (31%), Hinglish (11%) |
| `/admin/experiments` | Comparative Model Accuracy & Macro F1 | BarChart | Recharts | Accuracy % and Macro F1 % across 4 architectures |
| `/admin/early-warning` | Live Civic GIS Radar | SVG / Canvas Projection | Custom MapView | Geographic coordinates, 5 radial hotspot centroids, pins |
| `/admin/knowledge-graph` | Civic Entity Relationship Network | SVG Graph Network | Custom KnowledgeGraph | Nodes (Depts, Cats, Assets, SOPs), Edges, Zoom scale |

---

### 6.3. Interactive Tables Inventory

| Page Route | Table Description | Columns | Interactive Features |
|---|---|---|---|
| `/officer/dashboard` | Priority Assigned Cases | ID, Status, Priority, SLA Deadline, Title, Ward, Action | Direct link to action console |
| `/officer/assigned` | Assigned Field Queue | ID, Title & Category, Ward & Location, Priority, Status, SLA Target, Actions | Search, Priority filter, Status filter, CSV Export, Drawer Inspect |
| `/admin` | Critical SLA Risk Queue | ID, Priority, Breach Status, Title, Department, Ward, Action | Quick manage links |
| `/admin/grievances` | All Grievances Ledger | Checkbox, ID, Citizen, Description, Department, Location, Priority, AI Confidence, Status, Submitted, SLA Target, Actions | Global Search, Multi-Filter, Multi-select checkboxes, Bulk escalation, Pagination, CSV Export, Drawer Inspect |
| `/admin/predictions` | SLA Breach Risk Queue | ID, Department, Breach Probability (Bar), Risk Tier, Time Remaining, Contributing Factors, Action | Direct link to grievance record |
| `/admin/resolution-verification` | Auditable Case Queue | ID, Status, Title, Department, AI Score, Citizen Rating | Selection clicks to load comparison dossier |
| `/admin/workload` | Operational Health Scorecard | Department, Head, Officers, Active Caseload, Avg Resolution, SLA Compliance, Load Status | Status badges |
| `/admin/models` | Multi-Class Confusion Matrix | Actual Category (rows), Predicted Categories (columns, 6x6) | Matrix diagonal highlighting |
| `/admin/experiments` | Formal Experiment Log | Model Architecture, Parameters, Latency, Accuracy, Macro F1, Status | Winning model highlight |
| `/admin/audit-logs` | Immutable Audit Ledger | Timestamp, Action Type, Entity Target, Actor/Role, Details, IP Origin | Search, Entity filter, CSV Export |

---

## 7. Review of Services, Stores, and Mock Layer

### 7.1. API Client (`src/services/apiClient.ts`)
- Configured with Axios base instance targeting `process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"`.
- Contains request interceptor reading `civicmind_auth_token` from `localStorage` and injecting `Authorization: Bearer <token>`.
- Contains `USE_MOCK` boolean flag and `mockDelay()` utility (150ms-300ms simulated latency).

### 7.2. State Stores (`src/stores/`)
- `authStore.ts` (Zustand):
  - Stores `user: User | null`, `role: UserRole`, `isAuthenticated: boolean`, `isLoading: boolean`.
  - Methods: `setUser()`, `switchRole(role)`, `login(creds)`, `logout()`, `initAuth()`.
  - Persists session user and token into `localStorage`.
- `notificationStore.ts` (Zustand):
  - Stores `notifications: NotificationItem[]`, `unreadCount: number`.
  - Methods: `markAsRead(id)`, `markAllAsRead()`, `addNotification()`, `removeNotification()`.

### 7.3. Services Abstraction (`src/services/`)
- `authService.ts`: Handles session tokens and role identification.
- `grievanceService.ts`: Handles CRUD, status changes, reassignments, resolution submissions, and mock NLP inference.
- `duplicateService.ts`: Handles duplicate clusters, SBERT similarity scores, merge/reject actions.
- `earlyWarningService.ts`: Handles GIS hotspots, radial coordinates, and task force acknowledgment.
- `predictionService.ts`: Handles resolution time comparisons, SLA risk queue, and 7-day department workload forecasts.
- `simulatorService.ts`: Computes counterfactual queue outcomes using mathematical policy equations.
- `knowledgeGraphService.ts`: Manages node/edge graph queries and entity search.

---

## 8. Role-Based Access Control (RBAC) Requirements

| Role | Accessible Route Prefixes | Prohibited Route Prefixes | Key Permissions & Constraints |
|---|---|---|---|
| **Citizen** | `/citizen/*`, `/login`, `/register`, `/forgot-password`, `/` | `/officer/*`, `/admin/*` | Can file complaints, view own complaints, rate resolutions (1-5 stars), file appeals for reopened cases. Cannot modify department assignments, merge duplicates, or inspect officer internal notes. |
| **Department Officer** | `/officer/*`, `/login`, `/` | `/citizen/submit`, `/admin/*` | Can view assigned ward queue, update status to `in_progress`, submit resolution reports with photo evidence, add internal case notes, request reassignment. Cannot merge duplicate clusters or execute workload simulations. |
| **Administrator** | `/admin/*`, `/officer/*`, `/citizen/*`, `/` | *None (Apex Access)* | Full supervisory and operational access across all 6 departments. Can approve/reject duplicate merges, execute counterfactual simulations, reassign departments, audit ML model metrics, inspect SHAP feature charts, and trigger emergency radar task forces. |

---

## 9. Code Quality, TypeScript & Build Health

- **TypeScript Compilation**: `npx tsc --noEmit` executed with exit code `0`. Zero type errors.
- **Production Build**: `npm run build` completed successfully with exit code `0`.
- **Bundle Metrics**: First Load JS shared by all routes is `87.5 kB`. All individual pages range between `1.39 kB` and `11 kB`, ensuring fast page transitions and low latency.
- **Dead Buttons / Broken Routes**: Zero. Every visible button has an attached click handler, modal trigger, or navigation destination.

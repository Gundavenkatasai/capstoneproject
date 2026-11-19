# CivicMind AI — Citizen Grievance Intelligence and Resolution Prediction Platform

> **Advanced AI-Powered Civic Decision-Support Platform**  
> Built for municipal governance, predictive triage, cross-encoder duplicate intelligence, and transparent citizen services.

---

## 🏛️ Executive Overview

**CivicMind AI** is an enterprise-grade government technology intelligence and operational decision-support platform designed for modern municipal corporations and public service authorities. The platform transforms unorganized citizen grievance filings into actionable intelligence through predictive machine learning, multilingual semantic classification, spatial density anomaly detection, and human-in-the-loop verification.

---

## 🚀 Key Platform Portals & Experiences

### 1. Citizen Portal (`/citizen`)
- **Dashboard (`/citizen/dashboard`)**: Welcome header, active complaint tracking, resolution progress bar, and emergency hotlines.
- **Complaint Submission Wizard (`/citizen/submit`)**: 5-step wizard with text input, simulated voice-to-text recording in English, Hindi, and Hinglish, interactive GPS coordinate pin picker, photo/document upload validation, anonymous filing option, and live AI confidence preview.
- **Duplicate Prevention Warning**: In-flight semantic matching alerts citizens if a duplicate issue has already been reported nearby.
- **My Grievances & Real-Time Tracking (`/citizen/grievances`, `/citizen/grievances/[id]`)**: Full lifecycle timeline from submission to closure, officer photo evidence inspection, 5-star resolution rating, and citizen right-of-appeal reopening.
- **Appeals & Reviews (`/citizen/appeals`)**: Contested resolutions escalated to senior supervisory oversight.

### 2. Department Officer Workspace (`/officer`)
- **Officer Dashboard (`/officer/dashboard`)**: Live caseload metrics, SLA countdowns, priority triage, and direct action triggers.
- **Assigned Queue (`/officer/assigned`)**: Comprehensive table with ward filtering, quick-inspect drawer, and status management.
- **Case Execution Console (`/officer/grievances/[id]`)**: Accept assignments, log internal field notes, upload proof-of-work photographs, submit official resolution reports, and request inter-departmental reassignments.
- **Performance & SLA Scorecard (`/officer/performance`)**: Weekly throughput charts, mean resolution velocity, and citizen satisfaction ratings.

### 3. Administrator Intelligence Command Center (`/admin`)
- **Intelligence Overview Dashboard (`/admin`)**: 8 KPI executive metrics, Area and Bar chart telemetry, live AI operational insight alerts, and critical SLA risk queue.
- **All Grievances Ledger (`/admin/grievances`)**: Multi-column data table with global search, status/priority/department filtering, CSV export, bulk escalation, and slide-out inspection drawer.
- **Grievance Dossier (`/admin/grievances/[id]`)**: 7 dedicated tabs (Overview, AI Analysis, Similar Complaints, Timeline, Evidence, Prediction, and Audit History).
- **Duplicate Intelligence Center (`/admin/duplicates`)**: Cross-encoder semantic clustering, side-by-side complaint comparison, and human-approved merge operations.
- **Civic Issue Early-Warning Radar (`/admin/early-warning`)**: Interactive GIS city radar map with radial hotspot clustering, incident velocity trends, and rapid task force dispatching.
- **Predictive Analytics & SLA Forecaster (`/admin/predictions`)**: Actual vs. predicted resolution durations, SLA breach risk queue, and 7-day departmental workload forecasting.
- **Explainable AI (XAI) (`/admin/explainability`)**: TreeSHAP and KernelSHAP feature contribution charts, lexical token attributions, and cryptographic decision traces.
- **Civic Entity Knowledge Graph (`/admin/knowledge-graph`)**: Interactive graph ontology linking departments, categories, assets, jurisdictions, and standard operating procedures.
- **Resolution Quality Verification (`/admin/resolution-verification`)**: Independent audit verifying photographic evidence and AI consistency before closing cases.
- **Workload Management (`/admin/workload`)**: Cross-departmental capacity comparisons and staffing utilization.
- **Counterfactual Workload Simulator (`/admin/simulator`)**: "What-if" scenario simulator modeling staffing changes, capacity multipliers, and SLA threshold adjustments.
- **Scientific Benchmarks & Datasets (`/admin/models`, `/admin/datasets`, `/admin/experiments`)**: Multiclass confusion matrix, Precision@K, PR-AUC, and 142.5K corpus exploration.
- **Immutable Audit Logs (`/admin/audit-logs`)**: WORM tamper-evident transaction logs.

---

## 🛠️ Technology Stack

- **Framework**: [Next.js](https://nextjs.org/) (App Router, React 18, TypeScript)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/) with enterprise design tokens
- **Icons**: [Lucide React](https://lucide.dev/)
- **Charts**: [Recharts](https://recharts.org/) (Responsive Area, Bar, Line, Pie)
- **GIS Mapping**: Dynamic SVG GIS Canvas with radar clustering
- **State Management**: [Zustand](https://github.com/pmndrs/zustand)
- **HTTP Client**: [Axios](https://axios-http.com/) with deterministic mock service layer

---

## 💻 Running the Application

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Run production build
npm run build

# Start production server
npm start
```

Default local URL: `http://localhost:3000`

---

## 👤 Demo Login Credentials

Quick one-click access is available on the `/login` screen or via the bottom **Role Switcher** in the sidebar:

| Role | Name | Email | Default Portal |
|---|---|---|---|
| **Citizen** | Aarav Sharma | `aarav.sharma@example.com` | `/citizen/dashboard` |
| **Officer** | Er. Rajesh Verma | `rajesh.verma@pwd.gov.in` | `/officer/dashboard` |
| **Administrator** | Dr. Sunita Rao, IAS | `commissioner.grievance@gov.in` | `/admin` |

---

## 🔬 Ethical Governance & Scientific Notice

*CivicMind AI adheres to human-in-the-loop decision-support principles. No citizen complaint is automatically merged or closed without human verification. Simulated radar feeds and benchmark scores are cataloged for university research and prototype validation.*

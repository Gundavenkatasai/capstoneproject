# API Requirements Specification (FastAPI / REST)
**Project**: CivicMind AI — AI-Powered Citizen Grievance Intelligence and Resolution Prediction Platform  
**Target Backend**: Python FastAPI, Pydantic v2, PostgreSQL, Redis, Celery  
**Base Path**: `/api/v1`

---

## 1. Authentication & User Management Endpoints

### 1.1. User Login
- **Method**: `POST`
- **Path**: `/api/v1/auth/login`
- **Authentication**: None (Public)
- **Required Role**: None
- **Frontend Page**: `/login`
- **Request Schema**:
  ```json
  {
    "email": "string (email format)",
    "password": "string (min 6 chars)",
    "role": "string (enum: citizen | officer | admin)"
  }
  ```
- **Response Schema** (`200 OK`):
  ```json
  {
    "token": "string (JWT Bearer Token)",
    "token_type": "bearer",
    "expires_in": 86400,
    "user": {
      "id": "string (UUID)",
      "name": "string",
      "email": "string",
      "role": "citizen | officer | admin",
      "department": "string | null",
      "phone": "string | null",
      "ward": "string | null",
      "avatar": "string (URL) | null",
      "badge": "string | null"
    }
  }
  ```

---

### 1.2. Citizen Registration
- **Method**: `POST`
- **Path**: `/api/v1/auth/register`
- **Authentication**: None (Public)
- **Required Role**: None
- **Frontend Page**: `/register`
- **Request Schema**:
  ```json
  {
    "name": "string (min 2 chars)",
    "email": "string (email format)",
    "phone": "string (phone format)",
    "ward": "string",
    "password": "string (min 6 chars)"
  }
  ```
- **Response Schema** (`201 Created`): Same as login response (`token` + `user`).

---

### 1.3. Get Current User Profile
- **Method**: `GET`
- **Path**: `/api/v1/auth/me`
- **Authentication**: Required (`Bearer <JWT>`)
- **Required Role**: Any authenticated user
- **Frontend Page**: Global Header (`AppHeader`), `/citizen/profile`, `/officer/profile`
- **Request Schema**: None (Headers: `Authorization: Bearer <token>`)
- **Response Schema** (`200 OK`): `User` object schema.

---

### 1.4. Update Profile Preferences
- **Method**: `PUT`
- **Path**: `/api/v1/users/me`
- **Authentication**: Required (`Bearer <JWT>`)
- **Required Role**: Any authenticated user
- **Frontend Page**: `/citizen/profile`, `/officer/profile`
- **Request Schema**:
  ```json
  {
    "name": "string | null",
    "phone": "string | null",
    "ward": "string | null",
    "avatar_url": "string | null"
  }
  ```
- **Response Schema** (`200 OK`): Updated `User` object schema.

---

## 2. Grievance Management Endpoints

### 2.1. List Grievances (Filtered & Paginated)
- **Method**: `GET`
- **Path**: `/api/v1/grievances`
- **Authentication**: Required (`Bearer <JWT>`)
- **Required Role**: Any (Role-scoped: Citizens see only their submissions; Officers see only their assigned department/ward; Admins see system-wide)
- **Frontend Page**: `/admin/grievances`, `/officer/assigned`, `/citizen/grievances`, `/admin`, `/officer/dashboard`, `/citizen/dashboard`
- **Query Parameters**:
  - `search`: string (optional)
  - `status`: string (enum: `submitted`, `analyzed`, `assigned`, `in_progress`, `resolution_submitted`, `citizen_verified`, `closed`, `escalated`, `reopened`)
  - `priority`: string (enum: `critical`, `high`, `medium`, `low`)
  - `department_id`: string (optional)
  - `category`: string (optional)
  - `ward`: string (optional)
  - `page`: integer (default: `1`)
  - `page_size`: integer (default: `10`, max: `100`)
- **Response Schema** (`200 OK`):
  ```json
  {
    "items": [
      {
        "id": "string (e.g. GRV-2026-8941)",
        "title": "string",
        "description": "string",
        "citizen_id": "string",
        "citizen_name": "string",
        "category": "string",
        "subcategory": "string",
        "department_id": "string",
        "department_name": "string",
        "assigned_officer_id": "string | null",
        "assigned_officer_name": "string | null",
        "location": {
          "address": "string",
          "ward": "string",
          "zone": "string",
          "lat": "float",
          "lng": "float"
        },
        "priority": "critical | high | medium | low",
        "status": "string",
        "ai_confidence": "float (0.0 to 1.0)",
        "submitted_at": "string (ISO8601)",
        "updated_at": "string (ISO8601)",
        "expected_resolution_date": "string (ISO8601)",
        "sla_deadline": "string (ISO8601)",
        "sla_breached": "boolean",
        "sla_breach_risk": "low | medium | high | critical",
        "duplicate_probability": "float (0.0 to 1.0)",
        "duplicate_cluster_id": "string | null",
        "is_anonymous": "boolean",
        "evidence": [
          { "id": "string", "name": "string", "size": "string", "type": "image | document | audio", "url": "string" }
        ]
      }
    ],
    "total": 1127,
    "page": 1,
    "page_size": 10,
    "total_pages": 113
  }
  ```

---

### 2.2. Get Grievance by ID (Dossier View)
- **Method**: `GET`
- **Path**: `/api/v1/grievances/{id}`
- **Authentication**: Required (`Bearer <JWT>`)
- **Required Role**: Any (Citizens restricted to own ID or public redacted view)
- **Frontend Page**: `/admin/grievances/[id]`, `/officer/grievances/[id]`, `/citizen/grievances/[id]`
- **Response Schema** (`200 OK`): Complete `Grievance` object including:
  - Base fields
  - `timeline`: array of `{ id, status, title, description, timestamp, actor, actorRole, notes }`
  - `resolution_report`: `{ text, resolved_at, officer_evidence: [], citizen_feedback_rating, citizen_feedback_comment, ai_verification_confidence, verified_by_admin }`
  - `shap_factors`: array of `{ feature, weight, effect, description }`
  - `routing_trace`: `{ keywords_matched: [], sentiment_score, recommended_department, second_choice_department, department_fit_score }`

---

### 2.3. Submit New Grievance (Citizen Filing)
- **Method**: `POST`
- **Path**: `/api/v1/grievances`
- **Authentication**: Required (`Bearer <JWT>`)
- **Required Role**: `citizen` or `admin`
- **Frontend Page**: `/citizen/submit`
- **Request Schema**:
  ```json
  {
    "title": "string",
    "description": "string (min 15 chars)",
    "language": "en | hi | hinglish",
    "is_anonymous": "boolean",
    "category": "string",
    "subcategory": "string",
    "location": {
      "address": "string",
      "ward": "string",
      "zone": "string",
      "lat": "float",
      "lng": "float"
    },
    "evidence_file_ids": ["string (UUID)"]
  }
  ```
- **Response Schema** (`201 Created`): `Grievance` object with auto-generated ID (e.g., `GRV-2026-XXXX`), initial status `submitted`, and queued background Celery task for NLP classification.

---

### 2.4. Transition Grievance Status
- **Method**: `PATCH`
- **Path**: `/api/v1/grievances/{id}/status`
- **Authentication**: Required (`Bearer <JWT>`)
- **Required Role**: `officer` or `admin`
- **Frontend Page**: `/officer/grievances/[id]`, `/admin/grievances/[id]`, `/admin/resolution-verification`
- **Request Schema**:
  ```json
  {
    "status": "in_progress | resolution_submitted | closed | escalated | reopened",
    "notes": "string (optional reason/log)"
  }
  ```
- **Response Schema** (`200 OK`): Updated `Grievance` object with new timeline entry appended.

---

### 2.5. Submit Officer Resolution Report
- **Method**: `POST`
- **Path**: `/api/v1/grievances/{id}/resolution`
- **Authentication**: Required (`Bearer <JWT>`)
- **Required Role**: `officer` or `admin`
- **Frontend Page**: `/officer/grievances/[id]`
- **Request Schema**:
  ```json
  {
    "report_text": "string (detailed corrective actions taken)",
    "officer_evidence_urls": ["string (image URLs)"],
    "internal_notes": "string (optional crew/equipment log)"
  }
  ```
- **Response Schema** (`200 OK`): Updated `Grievance` object with status `resolution_submitted` and queued computer-vision resolution verification task.

---

### 2.6. Verify Resolution (Citizen Sign-Off)
- **Method**: `POST`
- **Path**: `/api/v1/grievances/{id}/verify`
- **Authentication**: Required (`Bearer <JWT>`)
- **Required Role**: `citizen` (owner of complaint) or `admin`
- **Frontend Page**: `/citizen/grievances/[id]`
- **Request Schema**:
  ```json
  {
    "approved": "boolean",
    "rating": "integer (1 to 5, required if approved is true)",
    "comment": "string (optional feedback comment)"
  }
  ```
- **Response Schema** (`200 OK`): Updated `Grievance` object with status `closed` (if approved) or `reopened` (if rejected).

---

### 2.7. File Citizen Appeal / Reopen Grievance
- **Method**: `POST`
- **Path**: `/api/v1/grievances/{id}/appeal`
- **Authentication**: Required (`Bearer <JWT>`)
- **Required Role**: `citizen` or `admin`
- **Frontend Page**: `/citizen/grievances/[id]`, `/citizen/appeals`
- **Request Schema**:
  ```json
  {
    "reason": "string (detailed explanation of unresolved ground condition)"
  }
  ```
- **Response Schema** (`200 OK`): Updated `Grievance` object with status `reopened`, flagged for supervisory review.

---

### 2.8. Reassign Department
- **Method**: `POST`
- **Path**: `/api/v1/grievances/{id}/reassign`
- **Authentication**: Required (`Bearer <JWT>`)
- **Required Role**: `officer` (request) or `admin` (authorize)
- **Frontend Page**: `/officer/grievances/[id]`, `/admin/grievances/[id]`
- **Request Schema**:
  ```json
  {
    "target_department_id": "string",
    "reason": "string (mandate or misrouting justification)"
  }
  ```
- **Response Schema** (`200 OK`): Updated `Grievance` object with new `department_id`, timeline note, and recalculated SLA.

---

## 3. AI & ML Inference Endpoints

### 3.1. Real-Time Triage & Routing Preview
- **Method**: `POST`
- **Path**: `/api/v1/ai/triage-preview`
- **Authentication**: Optional / Required (`Bearer <JWT>`)
- **Required Role**: Any
- **Frontend Page**: `/citizen/submit` (invoked on step 1 blur/click)
- **Request Schema**:
  ```json
  {
    "text": "string (min 15 chars)",
    "location_text": "string (optional street/ward name)"
  }
  ```
- **Response Schema** (`200 OK`):
  ```json
  {
    "summary": "string",
    "predicted_category": "string",
    "predicted_subcategory": "string",
    "recommended_department_id": "string",
    "recommended_department_name": "string",
    "priority": "critical | high | medium | low",
    "confidence": 0.94,
    "duplicate_probability": 0.84,
    "estimated_duration_days": 2.2,
    "sla_deadline": "string (ISO8601)",
    "similar_complaints": [
      { "id": "string", "title": "string", "similarity": 0.89, "status": "string" }
    ],
    "shap_explanation": [
      { "feature": "string", "weight": "float", "effect": "positive | negative", "description": "string" }
    ]
  }
  ```

---

### 3.2. Explainable AI (SHAP & Routing Attribution)
- **Method**: `GET`
- **Path**: `/api/v1/ai/explainability/{grievance_id}`
- **Authentication**: Required (`Bearer <JWT>`)
- **Required Role**: `admin`
- **Frontend Page**: `/admin/explainability`, `/admin/grievances/[id]`
- **Response Schema** (`200 OK`):
  ```json
  {
    "grievance_id": "string",
    "model_name": "CivicDeBERTa-v4.2",
    "baseline_bias": 0.052,
    "predicted_category": "string",
    "confidence": 0.964,
    "features": [
      { "feature": "Lexical 'flooding / burst'", "impact": 0.38, "type": "positive", "category": "Keyword Ontology" },
      { "feature": "Asset 'main feeder line'", "impact": 0.31, "type": "positive", "category": "Knowledge Entity" },
      { "feature": "Language Complexity (Short)", "impact": -0.06, "type": "negative", "category": "Syntactic Form" }
    ],
    "decision_trace": [
      "1. Token extraction matched node 'Hydraulic Asset #4' in Civic Knowledge Graph",
      "2. 'flooding basement' triggered Life-Safety Triage Clause #14-B",
      "3. Incident GPS within 280m of pipeline pressure anomaly"
    ],
    "decision_hash": "string (SHA256)"
  }
  ```

---

## 4. Duplicate Intelligence Endpoints

### 4.1. List Duplicate Clusters
- **Method**: `GET`
- **Path**: `/api/v1/duplicates/clusters`
- **Authentication**: Required (`Bearer <JWT>`)
- **Required Role**: `admin`
- **Frontend Page**: `/admin/duplicates`
- **Response Schema** (`200 OK`):
  ```json
  {
    "clusters": [
      {
        "id": "string (UUID)",
        "cluster_code": "CLUS-WSSB-2026-08",
        "title": "string",
        "category": "string",
        "master_grievance_id": "GRV-2026-8941",
        "grievance_ids": ["GRV-2026-8941", "GRV-2026-8933"],
        "similarity_score": 0.89,
        "geographic_proximity_meters": 280,
        "time_span_hours": 18,
        "status": "pending_review | merged | rejected | split",
        "ai_merge_recommendation": "string",
        "reasons": ["string"]
      }
    ]
  }
  ```

---

### 4.2. Approve Duplicate Cluster Merge
- **Method**: `POST`
- **Path**: `/api/v1/duplicates/clusters/{id}/merge`
- **Authentication**: Required (`Bearer <JWT>`)
- **Required Role**: `admin`
- **Frontend Page**: `/admin/duplicates`
- **Request Schema**:
  ```json
  {
    "master_grievance_id": "string"
  }
  ```
- **Response Schema** (`200 OK`): Updated cluster status (`merged`) and audit trail record.

---

### 4.3. Reject Duplicate Cluster
- **Method**: `POST`
- **Path**: `/api/v1/duplicates/clusters/{id}/reject`
- **Authentication**: Required (`Bearer <JWT>`)
- **Required Role**: `admin`
- **Frontend Page**: `/admin/duplicates`
- **Request Schema**:
  ```json
  {
    "reason": "string (optional reason)"
  }
  ```
- **Response Schema** (`200 OK`): Updated cluster status (`rejected`).

---

## 5. Civic Issue Early-Warning Radar Endpoints

### 5.1. List Radar Hotspots
- **Method**: `GET`
- **Path**: `/api/v1/early-warning/hotspots`
- **Authentication**: Required (`Bearer <JWT>`)
- **Required Role**: `admin`
- **Frontend Page**: `/admin/early-warning`, `/admin`
- **Query Parameters**: `category`, `risk_level`
- **Response Schema** (`200 OK`):
  ```json
  {
    "hotspots": [
      {
        "id": "hotspot_1",
        "title": "string",
        "category": "string",
        "zone": "South Zone",
        "ward": "Ward 14",
        "lat": 28.5244,
        "lng": 77.1558,
        "radius_meters": 650,
        "complaint_count": 18,
        "risk_level": "critical | high | medium | low",
        "risk_score": 92,
        "trend": "increasing | stable | decreasing",
        "summary": "string",
        "recommended_action": "string",
        "related_complaint_ids": ["string"],
        "detected_at": "string (ISO8601)",
        "historical_velocity": [2, 3, 5, 8, 12, 18]
      }
    ]
  }
  ```

---

### 5.2. Acknowledge Hotspot / Dispatch Inspection Force
- **Method**: `POST`
- **Path**: `/api/v1/early-warning/hotspots/{id}/acknowledge`
- **Authentication**: Required (`Bearer <JWT>`)
- **Required Role**: `admin`
- **Frontend Page**: `/admin/early-warning`
- **Request Schema**:
  ```json
  {
    "notes": "string (dispatch order / crew details)"
  }
  ```
- **Response Schema** (`200 OK`): Updated `Hotspot` record with acknowledged status.

---

## 6. Predictive Analytics & Workload Simulator Endpoints

### 6.1. Get SLA Breach Queue
- **Method**: `GET`
- **Path**: `/api/v1/predictions/sla-breach-queue`
- **Authentication**: Required (`Bearer <JWT>`)
- **Required Role**: `admin` or `officer`
- **Frontend Page**: `/admin/predictions`, `/admin`, `/officer/dashboard`
- **Response Schema** (`200 OK`):
  ```json
  {
    "items": [
      {
        "grievance_id": "string",
        "title": "string",
        "department": "string",
        "breach_probability": 0.94,
        "risk_tier": "critical | high | medium | low",
        "hours_remaining": -14,
        "contributing_factors": ["string"],
        "recommended_action": "string"
      }
    ]
  }
  ```

---

### 6.2. Get Department 7-Day Forecast
- **Method**: `GET`
- **Path**: `/api/v1/predictions/department-forecast`
- **Authentication**: Required (`Bearer <JWT>`)
- **Required Role**: `admin`
- **Frontend Page**: `/admin/predictions`
- **Response Schema** (`200 OK`): Array of `{ department, current_active, projected_incoming_7d, projected_resolved_7d, net_backlog_change, capacity_utilization_pct, risk_level }`.

---

### 6.3. Execute Counterfactual Workload Simulation
- **Method**: `POST`
- **Path**: `/api/v1/simulator/simulate`
- **Authentication**: Required (`Bearer <JWT>`)
- **Required Role**: `admin`
- **Frontend Page**: `/admin/simulator`
- **Request Schema**:
  ```json
  {
    "additional_officers": 15,
    "department_capacity_multiplier": 1.25,
    "workload_redistribution_pct": 20,
    "routing_weight_ai_factor": 0.85,
    "escalation_threshold_hours": 36
  }
  ```
- **Response Schema** (`200 OK`):
  ```json
  {
    "current_backlog": 1127,
    "simulated_backlog": 718,
    "current_avg_resolution_days": 4.3,
    "simulated_avg_resolution_days": 2.7,
    "current_sla_breach_rate": 12.8,
    "simulated_sla_breach_rate": 5.4,
    "department_workload": [
      { "department": "Water Supply", "current_load": 312, "projected_load": 198, "capacity": 325 }
    ],
    "summary": "string"
  }
  ```

---

## 7. Knowledge Graph & Research Endpoints

### 7.1. Query Knowledge Graph Network
- **Method**: `GET`
- **Path**: `/api/v1/knowledge-graph/data`
- **Authentication**: Required (`Bearer <JWT>`)
- **Required Role**: `admin`
- **Frontend Page**: `/admin/knowledge-graph`
- **Query Parameters**: `search`, `type_filter`
- **Response Schema** (`200 OK`):
  ```json
  {
    "nodes": [
      { "id": "node_dept_pwd", "label": "Public Works Department", "type": "department", "group": "dept", "color": "#1E6BE6" }
    ],
    "edges": [
      { "id": "e1", "source": "node_dept_pwd", "target": "node_cat_pothole", "label": "handles", "relation": "handles" }
    ]
  }
  ```

---

### 7.2. Model Benchmark & Research Metrics
- **Method**: `GET`
- **Path**: `/api/v1/research/metrics`
- **Authentication**: Required (`Bearer <JWT>`)
- **Required Role**: `admin`
- **Frontend Page**: `/admin/models`, `/admin/datasets`, `/admin/experiments`
- **Response Schema** (`200 OK`): Full evaluation object containing `classification` (accuracy, confusion matrix), `duplicate` (P@K, mAP), `regression` (MAE, RMSE), `sla_breach` (PR-AUC, Brier score), and `dataset_stats`.

---

### 7.3. File Upload (Evidence Attachments)
- **Method**: `POST`
- **Path**: `/api/v1/uploads/evidence`
- **Authentication**: Required (`Bearer <JWT>`)
- **Required Role**: Any authenticated user
- **Frontend Page**: `/citizen/submit`, `/officer/grievances/[id]`
- **Request Format**: `multipart/form-data` (file: Binary, max 25MB, whitelist: `image/jpeg`, `image/png`, `application/pdf`)
- **Response Schema** (`201 Created`):
  ```json
  {
    "id": "string (UUID)",
    "name": "photo_burst.jpg",
    "size": "2.4 MB",
    "type": "image",
    "url": "https://storage.civicmind.gov/evidence/..."
  }
  ```

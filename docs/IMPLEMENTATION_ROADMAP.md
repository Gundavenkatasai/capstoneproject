# CivicMind AI — Backend Implementation Roadmap & Execution Plan

## 1. Roadmap Overview & Dependency Graph

This implementation roadmap outlines the ordered, milestone-driven execution plan for building the complete backend and AI/ML services for **CivicMind AI**. Each phase builds strictly upon the completed foundation of prior phases, eliminating circular dependencies and ensuring production stability.

```
+--------------------------------------------------------------------------------+
| PHASE 1: Core Backend Scaffold, PostgreSQL 16 + pgvector, Alembic Migrations   |
+---------------------------------------+----------------------------------------+
                                        |
                                        v
+--------------------------------------------------------------------------------+
| PHASE 2: Authentication, JWT Security, RBAC & User Identity Infrastructure     |
+---------------------------------------+----------------------------------------+
                                        |
                                        v
+--------------------------------------------------------------------------------+
| PHASE 3: Core Grievance Management, Lifecycle Engine & Multipart Evidence API  |
+---------------------------------------+----------------------------------------+
                                        |
                                        v
+--------------------------------------------------------------------------------+
| PHASE 4: Celery Background Workers, Redis Broker & Asynchronous Pipelines      |
+---------------------------------------+----------------------------------------+
                                        |
                                        v
+--------------------------------------------------------------------------------+
| PHASE 5: ML Inference Engines (NLP Categorization, pgvector HNSW, SLA Risk)    |
+---------------------------------------+----------------------------------------+
                                        |
                                        v
+--------------------------------------------------------------------------------+
| PHASE 6: Civic Early-Warning Radar, Spatial DBSCAN & Anomaly Detection         |
+---------------------------------------+----------------------------------------+
                                        |
                                        v
+--------------------------------------------------------------------------------+
| PHASE 7: Knowledge Graph, Counterfactual Simulator & Explainable AI (TreeSHAP) |
+---------------------------------------+----------------------------------------+
                                        |
                                        v
+--------------------------------------------------------------------------------+
| PHASE 8: Frontend-to-Backend Integration, Zero-Mock Validation & Full E2E Test |
+--------------------------------------------------------------------------------+
```

---

## 2. Phase-by-Phase Execution Plan

### Phase 1: Core Backend Scaffold & Relational Database Layer
**Prerequisites**: Python 3.11+, Docker, PostgreSQL 16 with `pgvector`.  
**Goal**: Establish the running FastAPI application server, asynchronous database engine, and database schema migrations.

- [ ] **1.1. Project Initialization & Dependency Management**
  - Create directory `backend/` with standard FastAPI project structure.
  - Configure `pyproject.toml` / `requirements.txt` with core dependencies:
    - `fastapi`, `uvicorn[standard]`, `pydantic>=2.0`, `pydantic-settings`
    - `sqlalchemy[asyncio]>=2.0`, `asyncpg`, `psycopg2-binary`, `alembic`
    - `pgvector`, `redis`, `celery`, `python-jose[cryptography]`, `passlib[bcrypt]`
    - `python-multipart`, `pillow`, `httpx`
- [ ] **1.2. Containerized Infrastructure (Docker Compose)**
  - Author `docker-compose.yml` defining:
    - Service `postgres`: `ankane/pgvector:v0.5.1` (PostgreSQL 16 with pgvector extension pre-installed) exposing port `5432`.
    - Service `redis`: `redis:7-alpine` exposing port `6379`.
- [ ] **1.3. Application Configuration & Asynchronous Database Session**
  - Implement `app/core/config.py` using Pydantic `BaseSettings` to parse `.env` (database URLs, JWT secrets, CORS origins).
  - Implement `app/db/session.py` with SQLAlchemy 2 `create_async_engine` and `async_sessionmaker`.
- [ ] **1.4. Declarative ORM Models (SQLAlchemy 2)**
  - Implement all 15 relational entities in `app/models/`:
    - `users.py`, `departments.py`, `officers.py`, `grievances.py`, `grievance_embeddings.py`
    - `grievance_evidence.py`, `grievance_timeline.py`, `resolution_reports.py`
    - `duplicate_clusters.py`, `cluster_memberships.py`, `hotspots.py`
    - `knowledge_nodes.py`, `knowledge_edges.py`, `audit_logs.py`
- [ ] **1.5. Alembic Migrations Setup**
  - Initialize Alembic with async environment template.
  - Enable `vector` and `pg_trgm` extensions in the initial migration script.
  - Generate and run baseline migration (`0001_initial_schema.py`) to create all tables and indexes (including HNSW vector index).
- [ ] **1.6. Database Seeder Script**
  - Create `app/db/seed.py` to populate initial departments (Sanitation, Public Works, Water Supply, Electricity, Transport) and administrative zones matching the frontend sample data.

---

### Phase 2: Authentication, Security & Role-Based Access Control (RBAC)
**Prerequisites**: Phase 1 completed (Users and Departments tables active).  
**Goal**: Provide secure JWT-based authentication and role-based route guards matching the frontend auth store.

- [ ] **2.1. Cryptographic Security Utilities**
  - Implement `app/core/security.py`:
    - Password hashing and verification using `passlib.context.CryptContext(schemes=["bcrypt"])`.
    - JWT token generation (Access token: 60m TTL, Refresh token: 7d TTL) using `python-jose`.
- [ ] **2.2. Fastapi Security Dependencies & RBAC Guards**
  - Implement `app/core/dependencies.py`:
    - `get_current_user`: Validates `Authorization: Bearer <token>` header, extracts user claims, checks database.
    - `require_role(allowed_roles: list[UserRole])`: Enforces role-based boundaries (`CITIZEN`, `DEPARTMENT_OFFICER`, `ADMINISTRATOR`).
- [ ] **2.3. Authentication Endpoints (`/api/v1/auth`)**
  - `POST /api/v1/auth/login`: Validates credentials, issues JWT token pair, returns user profile and permissions.
  - `POST /api/v1/auth/register`: Creates new citizen accounts with password hashing.
  - `GET /api/v1/auth/me`: Returns the authenticated user's current session and profile.
  - `POST /api/v1/auth/refresh`: Issues refreshed access tokens.
  - `POST /api/v1/auth/logout`: Blacklists token in Redis.
- [ ] **2.4. Default Demo Accounts Seed**
  - Seed predefined credentials in the database matching the frontend login options:
    - Admin: `admin@civicmind.gov` / `admin123`
    - Officer: `officer@civicmind.gov` / `officer123`
    - Citizen: `citizen@civicmind.gov` / `citizen123`

---

### Phase 3: Core Grievance Management, Lifecycle Engine & Multipart API
**Prerequisites**: Phase 2 completed (User authentication and roles).  
**Goal**: Implement the complete CRUD and state machine for grievances, timeline events, evidence uploads, and resolution workflows.

- [ ] **3.1. Grievance Tracking ID Generator**
  - Implement sequence generator producing human-readable IDs matching frontend format: `GRV-YYYY-XXXXX` (e.g., `GRV-2026-08421`).
- [ ] **3.2. Citizen Submission & Management Endpoints (`/api/v1/grievances`)**
  - `POST /api/v1/grievances`: Accepts complaint submission (title, description, location, category, anonymous flag). Auto-creates initial timeline event `SUBMITTED`.
  - `GET /api/v1/grievances`: Filterable list query (status, department, priority, category, date range, pagination, sorting). Citizen role filters automatically by `citizen_id`.
  - `GET /api/v1/grievances/{id}`: Returns complete grievance record, joined with evidence, timeline events, and resolution report.
- [ ] **3.3. Multipart Evidence Upload Handling**
  - Implement local disk / S3 evidence storage service (`app/services/storage.py`).
  - `POST /api/v1/grievances/{id}/evidence`: Uploads images/documents, extracts EXIF coordinates if available, creates `grievance_evidence` records.
- [ ] **3.4. Officer Operational Workflow Endpoints**
  - `PATCH /api/v1/grievances/{id}/status`: Transitions grievance states (`IN_PROGRESS`, `UNDER_REVIEW`, `ESCALATED`). Appends timeline record.
  - `POST /api/v1/grievances/{id}/resolve`: Officer submits resolution report with before/after photos, labor hours, and contractor notes. Transitions status to `RESOLVED`.
- [ ] **3.5. Citizen Feedback & Verification Endpoints**
  - `POST /api/v1/grievances/{id}/feedback`: Citizen rates resolution (1-5 stars) and leaves comments. Transitions status to `CLOSED`.
  - `POST /api/v1/grievances/{id}/appeal`: Citizen rejects resolution with rationale. Reopens grievance and transitions status to `ESCALATED`.

---

### Phase 4: Celery Background Task Processing & Message Queue Setup
**Prerequisites**: Phase 3 completed (Core DB & API operations).  
**Goal**: Offload heavy computations, model inference, and recurring monitoring to a distributed worker pool.

- [ ] **4.1. Celery Application Configuration**
  - Configure `app/workers/celery_app.py` with Redis broker (`redis://localhost:6379/0`) and result backend (`redis://localhost:6379/1`).
  - Configure distinct queues: `ml_triage`, `duplicate_scan`, `sla_monitor`, `analytics`.
- [ ] **4.2. Asynchronous Triage Dispatch Pipeline**
  - Connect grievance submission hook to dispatch `tasks_ml.process_grievance_triage.delay(grievance_id)`.
- [ ] **4.3. Celery Beat Periodic Scheduler**
  - Configure recurring tasks:
    - `tasks_sla.check_sla_deadlines`: Runs every 5 minutes to detect approaching or breached SLAs.
    - `tasks_spatial.scan_radar_anomalies`: Runs every 15 minutes to refresh spatial hotspot clusters.
    - `tasks_analytics.compute_daily_department_metrics`: Runs daily at midnight.

---

### Phase 5: Python Machine Learning Inference Services
**Prerequisites**: Phase 4 completed (Celery worker pool operational).  
**Goal**: Deploy and serve the primary ML models: NLP categorization, SBERT dense vectors, pgvector HNSW search, LightGBM duration regression, and XGBoost SLA risk forecasting.

- [ ] **5.1. Semantic Vector Embedding Service**
  - Package `sentence-transformers/all-mpnet-base-v2` or `paraphrase-multilingual-mpnet-base-v2` in `app/ml/embeddings/`.
  - Implement batch vectorizer generating 768-dimensional normalized float vectors.
  - Store vector embeddings in `grievance_embeddings` table upon triage execution.
- [ ] **5.2. Semantic Duplicate Detection & Clustering Engine**
  - Implement vector similarity query using pgvector HNSW cosine distance (`<=>` operator).
  - Cross-Encoder reranker to verify borderline candidate matches (similarity 0.78 - 0.88).
  - Implement cluster assignment logic: attach to existing `duplicate_clusters` or initiate new cluster.
  - Endpoints:
    - `GET /api/v1/duplicates/clusters`: Retrieve high-density duplicate groups.
    - `POST /api/v1/duplicates/merge`: Merge duplicate complaints into master record.
- [ ] **5.3. Multi-Task NLP Categorization & Priority Classifier**
  - Implement transformer inference pipeline in `app/ml/classifiers/`:
    - Predicts category (Sanitation, Roads, Water, etc.) and fine-grained subcategory.
    - Predicts priority score (Low, Medium, High, Critical) based on semantic urgency keywords and sentiment.
  - Endpoint:
    - `POST /api/v1/triage/preview`: Real-time debounced preview endpoint consumed by the citizen submission wizard.
- [ ] **5.4. Resolution Duration Regressor & SLA Breach Predictor**
  - Implement LightGBM regressor (`app/ml/regression/`) trained on category, officer active load, time-of-day, and ward density.
  - Implement XGBoost binary classifier (`app/ml/forecasting/`) estimating $P(\text{SLA Breach})$.
  - Integrate **TreeSHAP** (`shap.TreeExplainer`) to compute top risk factor contributions.
  - Endpoints:
    - `GET /api/v1/predictions/sla-risk`: Query citywide and department SLA risk queues.
    - `GET /api/v1/predictions/grievances/{id}`: Grievance-specific SLA prediction and TreeSHAP waterfall values.

---

### Phase 6: Spatial GIS Analytics & Civic Early-Warning Radar
**Prerequisites**: Phase 5 completed (Embeddings and DB records populated).  
**Goal**: Detect emerging geographic outbreaks, recurring infrastructure failures, and anomalous complaint surges.

- [ ] **6.1. Spatial-Temporal DBSCAN Clustering Pipeline**
  - Implement scikit-learn `DBSCAN(eps=0.5/6371.0, min_samples=4, metric='haversine')` over 72-hour sliding coordinate windows.
  - Calculate cluster convex hulls, geographic centroids, and radius.
- [ ] **6.2. Anomaly Scoring & Velocity Surge Metrics**
  - Compute historical baseline complaint volume per ward/zone.
  - Calculate growth rate percentage ($\Delta \% = \frac{V_{\text{current}} - V_{\text{baseline}}}{V_{\text{baseline}}} \times 100$).
  - Assign threat severity levels (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- [ ] **6.3. Radar Persistence & API Endpoints**
  - Synchronize active clusters into `hotspots` table.
  - `GET /api/v1/radar/hotspots`: Returns list of geographic clusters with severity, coordinates, and affected categories.
  - `GET /api/v1/radar/summary`: Aggregated early-warning indicators (active hotspots, emerging clusters, critical risks).

---

### Phase 7: Knowledge Graph & Counterfactual Workload Simulator
**Prerequisites**: Phase 3 and Phase 5 completed.  
**Goal**: Power administrative intelligence tools for root-cause discovery and operational resource reallocation.

- [ ] **7.1. Public Service Knowledge Graph Engine**
  - Implement graph traversal module (`app/ml/graph/` or NetworkX service).
  - Graph entities: Departments, Categories, Infrastructure Assets, Regulations, Failure Patterns.
  - Endpoints:
    - `GET /api/v1/knowledge-graph/nodes`: Query entities and metadata.
    - `GET /api/v1/knowledge-graph/edges`: Query relationships, edge weights, and dependencies.
    - `GET /api/v1/knowledge-graph/path`: Shortest dependency or escalation path between two entities.
- [ ] **7.2. Counterfactual What-If Workload Simulator**
  - Implement discrete-event Monte Carlo simulation engine (`app/services/simulator_service.py`).
  - Inputs: Percentage budget change, staff reallocation between departments, priority shifts, seasonal surge factor.
  - Simulates 30-day resolution velocity, projected SLA compliance rate, and officer burnout indices.
  - Endpoint:
    - `POST /api/v1/simulator/run`: Returns counterfactual projections alongside baseline metrics.

---

### Phase 8: Operational Support, Model Research & Audit Logging
**Prerequisites**: Phase 3 through Phase 7 completed.  
**Goal**: Finalize administrative management, model evaluation dashboards, and regulatory compliance logs.

- [ ] **8.1. Department & Officer Management Endpoints**
  - `GET /api/v1/departments`: Department directory, SLA performance %, and open grievance counts.
  - `GET /api/v1/officers`: Officer directory, current active workload, capacity %, and historical resolution speed.
  - `POST /api/v1/officers/reassign`: Bulk transfer or rebalance grievance queues between officers.
- [ ] **8.2. Machine Learning Research & Benchmarking Endpoints**
  - `GET /api/v1/research/models`: Active model metadata, versions, F1-scores, accuracy, and inference latencies.
  - `GET /api/v1/research/metrics`: Model drift, precision/recall curves, and cross-validation statistics.
- [ ] **8.3. Immutable Audit Logging Middleware**
  - Implement FastAPI middleware capturing administrative actions (overrides, merges, reassignments, role modifications).
  - Write immutable entries into `audit_logs` table (timestamp, user, action, target entity, client IP, metadata).
  - `GET /api/v1/audit/logs`: Filterable audit trail viewer for administrators.

---

### Phase 9: Frontend-to-Backend Integration, Verification & Production Readiness
**Prerequisites**: All backend endpoints active.  
**Goal**: Connect the Next.js frontend directly to the live FastAPI backend, disable mock adapters, and perform end-to-end acceptance testing.

- [ ] **9.1. Mock Adapter Deactivation**
  - Update `.env.local` in Next.js frontend:
    ```env
    NEXT_PUBLIC_USE_MOCK_API="false"
    NEXT_PUBLIC_API_BASE_URL="http://localhost:8000/api/v1"
    ```
- [ ] **9.2. End-to-End Route Verification**
  - Execute automated and manual smoke tests across all 33 Next.js routes:
    - Public: Landing page `/`, `/login`, `/register`.
    - Citizen: Wizard submission `/citizen/submit`, Tracking `/citizen/grievances/[id]`, Feedback & Appeals.
    - Officer: Workload queue `/officer/grievances`, Status updates, Resolution upload `/officer/grievances/[id]/resolve`.
    - Administrator: Radar `/admin/radar`, Duplicates `/admin/duplicates`, SLA Risk `/admin/sla-risk`, Simulator `/admin/simulator`, Knowledge Graph `/admin/knowledge-graph`.
- [ ] **9.3. Production Dockerization & Orchestration**
  - Multi-stage Dockerfile for Next.js (`frontend/Dockerfile`).
  - Production Dockerfile for FastAPI (`backend/Dockerfile`).
  - Unified `docker-compose.prod.yml` with Nginx reverse proxy, SSL termination, and health checks.

---

## 3. Milestones & Verification Checklist

| Milestone | Key Deliverable | Verification Criteria | Status |
| :--- | :--- | :--- | :---: |
| **M0** | Frontend Design & Audit Specifications | 33 routes working, 5 technical audit documents created | **COMPLETED** |
| **M1** | Database & Core FastAPI Scaffold | Postgres 16 + pgvector running, Alembic migrations clean | Pending |
| **M2** | Authentication & RBAC Layer | JWT token issuance, password hashing, role guards verified | Pending |
| **M3** | Grievance Lifecycle & Evidence API | Grievance submission, evidence upload, officer resolution functional | Pending |
| **M4** | Celery & Redis Task Architecture | Background workers consume async triage tasks without errors | Pending |
| **M5** | ML Inference & Semantic Vector Search | pgvector HNSW cosine duplicate scan < 50ms, DeBERTa NLP live | Pending |
| **M6** | Civic Early-Warning Radar | Spatial DBSCAN generates active hotspot anomalies | Pending |
| **M7** | Simulator & Knowledge Graph | Monte Carlo simulation returns counterfactual metrics | Pending |
| **M8** | Live End-to-End Integration | Frontend `USE_MOCK_API=false` passes full submission-to-resolution flow | Pending |

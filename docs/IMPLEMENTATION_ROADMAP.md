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
### Phase 1: Core Backend Scaffold, PostgreSQL 16 + pgvector, Alembic Migrations
**Status**: COMPLETED (See `docs/PHASE_1_IMPLEMENTATION_REPORT.md`)

- [x] **1.1. FastAPI Project Structure & Async Lifecycle**
- [x] **1.2. Environment Configuration (`app/core/config.py`)**
- [x] **1.3. Asynchronous SQLAlchemy 2.0 Engine & Session Manager**
- [x] **1.4. SQLAlchemy 2.0 ORM Entity Definitions**
- [x] **1.5. Alembic Database Migrations**
- [x] **1.6. Database Seeder Script**

---

### Phase 2: Authentication, Security & Role-Based Access Control (RBAC)
**Status**: COMPLETED (See `docs/PHASE_2_IMPLEMENTATION_REPORT.md`)

- [x] **2.1. Cryptographic Security Utilities (Argon2id + PyJWT)**
- [x] **2.2. FastAPI Security Dependencies & RBAC Guards**
- [x] **2.3. Authentication Endpoints (`/api/v1/auth`) & Google OAuth2 SSO**
- [x] **2.4. Default Demo Accounts Seed**

---

### Phase 3: Core Grievance Management, Lifecycle Engine & Multipart API
**Status**: COMPLETED (See `docs/PHASE_3_IMPLEMENTATION_REPORT.md`)

- [x] **3.1. Grievance Tracking ID Generator (Sequence-based GRV-YYYY-XXXXX)**
- [x] **3.2. Citizen Submission & Management Endpoints (`/api/v1/grievances`)**
- [x] **3.3. Multipart Evidence Upload Handling with Magic-byte Validation**
- [x] **3.4. Officer Operational Workflow Endpoints & Field Resolution**
- [x] **3.5. Citizen Feedback & Verification Endpoints (Accept/Reject & Appeals)**

---

### Phase 4: Celery Background Task Processing & Message Queue Setup
**Status**: COMPLETED (See `docs/PHASE_4_IMPLEMENTATION_REPORT.md`)

- [x] **4.1. Celery Application Configuration (`app/core/celery_app.py`)**
  - Redis broker and result backend (`redis://localhost:6379/0`), JSON-only task serialization, UTC scheduling.
  - Dedicated logical queues: `default`, `notifications`, `grievance_processing`, `maintenance`.
- [x] **4.2. Transactional Outbox Pattern & At-Least-Once Delivery**
  - Alembic migration `0005_outbox_events.py` and `outbox_events` table.
  - Automatic ACID outbox event registration inside `create_grievance` and `record_transition`.
  - Batch outbox dispatcher (`dispatch_outbox_events_task`) and stale recovery (`reconcile_stale_outbox_events_task`).
- [x] **4.3. Pluggable Notification Provider & Idempotency**
  - `LoggingNotificationProvider` with structured logging.
  - Redis idempotency guards (`civicmind:idemp:notif:...`) with 24-hour expiration preventing duplicate delivery.
- [x] **4.4. Safe Unattached Evidence Cleanup**
  - `cleanup_abandoned_evidence_task` purges unattached uploads older than 24h.
  - Enforces strict safety invariant: NEVER touches files attached to active grievances.
- [x] **4.5. Celery Beat Periodic Scheduler & Admin Observability API**
  - Celery Beat schedule for outbox dispatch (15s), reconciliation (5m), health check (5m), evidence cleanup (24h).
  - Admin endpoints (`/api/v1/admin/tasks/health`, `/outbox`, `/dispatch`, `/cleanup`).
  - 16 new automated tests in `tests/test_tasks.py` (86 tests total, 100% pass rate).

---

### Phase 5: Python Machine Learning Inference Services
**Status**: COMPLETED (See `docs/PHASE_5_IMPLEMENTATION_REPORT.md`, `docs/PHASE_5_MODEL_EVALUATION.md`, `docs/PHASE_5_DATASET_READINESS.md`, and `docs/PHASE_5_ML_ARCHITECTURE.md`)

- [x] **5.1. Empirical Dataset Readiness Gate Audit**
  - Audited PostgreSQL tables: 12 test fixtures, 0 completed resolutions, 0 breaches (`insufficient_data`).
  - Implemented empirical gate with graceful fallback to municipal rule-based engines.
  - Provided segregated benchmark research dataset (`BENCHMARK_RESEARCH_DATASET_v1`, 500 cases) for offline training and evaluation.
- [x] **5.2. Semantic Vector Embedding Service (`backend/ml/embeddings/`)**
  - Dense 768-dimensional vector generator strictly satisfying `len(embedding) == 768` (pgvector `vector(768)`).
  - Sentence-BERT support with fast deterministic 768-dim semantic projection fallback.
  - Outbox-driven asynchronous background generation via Celery.
- [x] **5.3. Semantic Duplicate Detection & Clustering Engine (`backend/ml/duplicates/`)**
  - Vector similarity query using pgvector HNSW cosine distance (`cosine_distance(embedding, query)`).
  - Geospatial Haversine distance gating (<= 1000m) and temporal windowing (<= 30d).
  - Non-destructive candidate cluster generation (`DuplicateCluster` in `pending_review`).
- [x] **5.4. Multi-Task NLP Categorization & Department Routing (`backend/ml/classification/`)**
  - N-gram sublinear TF-IDF + calibrated Logistic Regression across 8 municipal categories and 6 departments.
  - Endpoints: `POST /api/v1/ai/classify`, `POST /api/v1/ai/department-recommendation`, `POST /api/v1/ai/triage-preview`.
- [x] **5.5. Resolution Duration Regressor & SLA Breach Predictor (`backend/ml/resolution/`, `backend/ml/sla/`)**
  - HistGradientBoostingRegressor predicting duration in days (MAE = 0.6093 days vs. 1.1520 median baseline) with positive bounds [0.5, 30.0].
  - Calibrated SLA Classifier predicting breach probability (ROC-AUC = 0.9570, PR-AUC = 0.8858) and assigning risk tiers.
- [x] **5.6. Explainability Engine & Unified Model Registry (`backend/ml/explainability/`, `backend/ml/registry/`)**
  - TreeSHAP feature attributions (`SHAPFactor`) and token-level lexical attributions.
  - Versioned model registry with `joblib` artifact persistence in `backend/ml/artifacts/`.
  - Comprehensive automated test suite: 101/101 tests passing (100% pass rate).

---

### Phase 6: Spatial GIS Analytics & Civic Early-Warning Radar
**Prerequisites**: Phase 5 completed (Embeddings and DB records populated).  
**Goal**: Detect emerging geographic outbreaks, recurring infrastructure failures, and anomalous complaint surges.

- [x] **6.1. Spatial-Temporal DBSCAN Clustering Pipeline**
  - Implement scikit-learn `DBSCAN(eps=0.5/6371.0, min_samples=2, metric='haversine')` over coordinate windows.
  - Calculate cluster convex hulls, geographic centroids, and radius in meters.
  - Strict segregation: synthetic benchmark records quarantined from operational hotspots.
- [x] **6.2. Anomaly Scoring & Velocity Surge Metrics**
  - Compute historical baseline complaint volume per ward/zone.
  - Calculate growth rate percentage ($\Delta \% = \frac{V_{\text{current}} - V_{\text{baseline}}}{V_{\text{baseline}}} \times 100$).
  - Assign threat severity levels (`low`, `medium`, `high`, `critical`) and domain-specific intervention actions.
- [x] **6.3. Radar Persistence & API Endpoints**
  - Synchronize active clusters into `hotspots` PostgreSQL table.
  - `GET /api/v1/early-warning/hotspots` (and alias `/radar/hotspots`): Returns list of geographic clusters with severity, coordinates, and affected categories.
  - `GET /api/v1/early-warning/summary` (and alias `/radar/summary`): Aggregated early-warning indicators (active hotspots, emerging clusters, critical risks).
  - `POST /api/v1/early-warning/hotspots/{id}/acknowledge`: Task force dispatch acknowledgement.
  - `POST /api/v1/simulator/run` & `GET /api/v1/simulator/baseline`: Counterfactual Workload Simulator.

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

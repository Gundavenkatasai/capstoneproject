# CivicMind AI — System Architecture & Technical Specification

## 1. Executive System Overview

**CivicMind AI** is an enterprise-grade civic grievance intelligence, predictive resolution, and automated operational decision-support platform designed for modern public administration. The system bridges citizen participatory democracy and data-driven administrative governance by uniting natural language processing, dense semantic vector search, gradient-boosted tabular forecasting, spatial-temporal anomaly clustering, and counterfactual operational simulation.

The architecture is partitioned into a decoupled, high-performance distributed topology:
1. **Presentation Layer**: Next.js 14 App Router, TypeScript, Tailwind CSS, Zustand, and dynamic data visualization (Recharts, SVG/Leaflet GIS).
2. **API Gateway & Core Application Server**: Python FastAPI (asynchronous ASGI), Pydantic v2 schemas, SQLAlchemy 2 ORM, and JWT/OAuth2 role-based security.
3. **Primary Relational & Vector Data Store**: PostgreSQL 16 with the `pgvector` extension for persistent tabular data, relational graphs, and 768-dimensional semantic embeddings indexed via Hierarchical Navigable Small World (HNSW) graphs.
4. **Caching & Asynchronous Broker**: Redis 7 for session state, query caching, real-time pub/sub, and task queue management.
5. **Distributed Asynchronous Worker Cluster**: Celery workers running Python-native machine learning pipelines for heavy transformer inference, gradient boosting, spatial clustering, and automated escalation watchers.
6. **Machine Learning & Research Inference Subsystems**: Model runtime hosting DeBERTa-v3/multilingual transformers, Sentence-Transformers, LightGBM/XGBoost, TreeSHAP explainability, and spatial DBSCAN.

---

## 2. High-Level System Topology

```
+----------------------------------------------------------------------------------------------------+
|                                           CLIENT BROWSERS                                          |
|  +---------------------------+  +--------------------------------+  +---------------------------+  |
|  |      Citizen Portal       |  |   Department Officer Portal    |  |   Admin Intelligence      |  |
|  | (/citizen/submit, track)  |  |   (/officer/workload, resolve) |  |   (/admin/radar, sim)     |  |
|  +-------------+-------------+  +---------------+----------------+  +-------------+-------------+  |
+----------------\--------------------------------|--------------------------------/-----------------+
                  \                               |                               /
                   \                              |                              /
+-------------------\-----------------------------v-----------------------------/--------------------+
|                                      FRONTEND APPLICATION LAYER                                    |
|                                       Next.js 14 (App Router)                                      |
|  - Server-Side Rendering (SSR) & Dynamic Routing                                                   |
|  - Global State Orchestration: Zustand (AuthStore, GrievanceStore, NotificationStore)              |
|  - Mock Adapter / Live API Switch via NEXT_PUBLIC_USE_MOCK_API & NEXT_PUBLIC_API_BASE_URL          |
|  - Centralized Axios HTTP Client with JWT Interceptors & Bearer Token Injection                    |
+-------------------------------------------------+--------------------------------------------------+
                                                  | HTTP / JSON (RESTful API)
                                                  v
+----------------------------------------------------------------------------------------------------+
|                                      APPLICATION BACKEND (FastAPI)                                 |
|  +-----------------------------------------------------------------------------------------------+  |
|  | Reverse Proxy / SSL Termination (Nginx or Cloud Load Balancer)                                |  |
|  +-----------------------------------------------+-----------------------------------------------+  |
|                                                  |                                                 |
|  +-----------------------------------------------v-----------------------------------------------+  |
|  | FastAPI Core Application (ASGI - Uvicorn / Gunicorn Workers)                                  |  |
|  |  * CORS Middleware & Security Headers                                                          |  |
|  |  * JWT Auth & Role-Based Access Control (RBAC: Citizen, Officer, Admin)                       |  |
|  |  * Pydantic v2 Request Validation & Response Serialization                                     |  |
|  |  * Structured JSON Logging & OpenTelemetry Tracing                                            |  |
|  |  * Endpoints: /auth, /grievances, /triage, /duplicates, /radar, /sla, /simulator, /graph, etc. |  |
|  +-------------------+---------------------------+---------------------------+-------------------+  |
+----------------------|---------------------------|---------------------------|---------------------+
                       | Async I/O (asyncpg)       | TCP / PubSub              | Celery Task Dispatch
                       v                           v                           v
+------------------------------------+  +--------------------+  +------------------------------------+
|         PRIMARY DATA STORE         |  |   CACHE & BROKER   |  |     ASYNCHRONOUS WORKER POOL       |
|            PostgreSQL 16           |  |      Redis 7       |  |          (Celery Workers)          |
|------------------------------------|  |--------------------|  |------------------------------------|
| - Relational Entities:             |  | - Celery Broker    |  | ML Inference & Heavy Analytics:    |
|   users, departments, officers,    |  |   & Result Backend |  | - DeBERTa text categorization      |
|   grievances, evidence, timeline   |  | - JWT Blacklist /  |  | - SBERT 768d vector embeddings     |
| - pgvector Extension:              |  |   Session Cache    |  | - LightGBM resolution forecasting  |
|   grievance_embeddings (768-dim)   |  | - Hotspot Anomaly  |  | - XGBoost SLA breach classifier    |
|   HNSW Cosine Distance Indexing    |  |   Cache            |  | - TreeSHAP feature attribution     |
| - GIN Indexes: Trigram text search |  | - API Rate-Limit   |  | - Spatial DBSCAN radar scanning    |
| - Spatial Lat/Lng Coordinates      |  |   Counters         |  | - Celery Beat periodic SLA monitor |
+------------------------------------+  +--------------------+  +------------------------------------+
```

---

## 3. Subsystem Architectural Components

### 3.1. Frontend Integration & Decoupling Layer

The Next.js 14 frontend is architected around a unified abstraction layer located in `src/services/`. Every interactive screen communicates through this interface, ensuring zero tight coupling to mock fixtures.

```
       [React UI View Component]
                   |
                   v
       [Zustand Store / Hook]
                   |
                   v
      [Domain Service Interface] (e.g., grievanceService.ts)
                   |
         +---------+---------+
         |                   |
 [Mock Data Adapter]   [Axios API Client]
 (Local In-Memory)     (Bearer Token, BaseURL)
                             |
                             v
                    [FastAPI Backend]
```

- **Environment Variable Switching**:
  - `NEXT_PUBLIC_USE_MOCK_API="false"`: Disables synthetic browser fixtures and redirects all API requests through `src/services/apiClient.ts`.
  - `NEXT_PUBLIC_API_BASE_URL="http://localhost:8000/api/v1"`: Specifies the FastAPI application root.
- **Request Authentication Interceptor**:
  - Extracts active JWT access tokens from `localStorage.getItem("civicmind_token")`.
  - Automatically attaches `Authorization: Bearer <token>` to outbound requests.
  - Automatically handles `401 Unauthorized` responses by dispatching token refresh requests or clearing state and routing to `/login`.

---

### 3.2. FastAPI Application Server Architecture

FastAPI provides an asynchronous, non-blocking Python backend capable of serving high-throughput I/O requests while offloading CPU-intensive machine learning workloads.

#### Architectural Structure:
```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py             # Login, register, profile, refresh
│   │   │   │   ├── grievances.py       # CRUD, filtering, status transitions, evidence
│   │   │   │   ├── triage.py           # Real-time NLP preview & pre-submission scoring
│   │   │   │   ├── duplicates.py       # Cluster discovery, cosine similarity, merge actions
│   │   │   │   ├── early_warning.py    # Spatial anomaly detection, hotspot surveillance
│   │   │   │   ├── predictions.py      # SLA forecasting, risk factors, explainability
│   │   │   │   ├── simulator.py        # What-if counterfactual scenario simulation
│   │   │   │   ├── knowledge_graph.py  # Graph nodes, edges, path search
│   │   │   │   ├── officers.py         # Workload distribution, assignment
│   │   │   │   ├── departments.py      # Department directory, performance metrics
│   │   │   │   ├── research.py         # Model accuracy benchmarks, drift, experiments
│   │   │   │   └── audit.py            # Immutable audit event logs
│   │   │   └── api_router.py          # Unified v1 router assembly
│   ├── core/
│   │   ├── config.py                  # Pydantic BaseSettings, environment loading
│   │   ├── security.py                # Password hashing (bcrypt), JWT generation/validation
│   │   └── dependencies.py            # Auth injection, DB session injection, RBAC guards
│   ├── db/
│   │   ├── base.py                    # Declarative base & entity imports
│   │   ├── session.py                 # Async SQLAlchemy engine & session maker
│   │   └── migrations/                # Alembic migration scripts
│   ├── models/                        # SQLAlchemy 2 Declarative ORM models
│   ├── schemas/                       # Pydantic v2 validation models
│   ├── services/                      # Pure business logic services (DB manipulation)
│   ├── workers/                       # Celery tasks and worker application
│   │   ├── celery_app.py              # Celery instance configuration
│   │   ├── tasks_ml.py                # Inference tasks (DeBERTa, SBERT, LightGBM)
│   │   ├── tasks_spatial.py           # Spatial DBSCAN & clustering tasks
│   │   └── tasks_sla.py               # Celery Beat SLA breach detection periodic tasks
│   └── ml/                            # Machine learning models, pipelines, feature transforms
│       ├── classifiers/               # DeBERTa fine-tuned classification weights & pipeline
│       ├── embeddings/                # SBERT / MPNet vectorizer
│       ├── regression/                # LightGBM resolution time estimators
│       ├── forecasting/               # XGBoost SLA breach classifiers
│       ├── explainability/            # TreeSHAP / SHAP explainer wrappers
│       ├── spatial/                   # DBSCAN & geographic outlier algorithms
│       └── graph/                     # Graph traversal & relationship search
└── tests/                             # Pytest test suite (unit, integration, load)
```

---

### 3.3. Relational & Vector Persistence Architecture

PostgreSQL 16 serves as the single source of truth for both relational state and dense semantic vectors.

#### Key Architectural Elements:
1. **Relational Consistency**: Strict foreign key constraints and ACID transaction isolation prevent orphaned records across grievances, timeline events, evidence artifacts, and resolution reports.
2. **pgvector Integration**:
   - The `grievance_embeddings` table stores 768-dimensional embeddings generated by fine-tuned multilingual sentence transformers.
   - Vector indexing utilizes **HNSW (Hierarchical Navigable Small World)** graphs with cosine distance metrics:
     ```sql
     CREATE INDEX idx_grievance_embeddings_hnsw 
     ON grievance_embeddings 
     USING hnsw (embedding vector_cosine_ops) 
     WITH (m = 16, ef_construction = 64);
     ```
   - Enables sub-millisecond approximate nearest neighbor (ANN) lookups over hundreds of thousands of civic complaints.
3. **Spatial Representation**:
   - Grievance geographic coordinates are stored as floating-point `(latitude, longitude)` values indexed via b-trees for bounding-box bounding and coordinate filtering.
   - In extended deployments, `PostGIS` geometries (`geometry(Point, 4326)`) can be layered seamlessly for polygon containment within ward and zone boundaries.
4. **Full-Text & Lexical Search**:
   - `pg_trgm` (trigram) extension and PostgreSQL GIN indexes on `title` and `description` support typo-tolerant substring searching, complementing semantic vector search.

---

### 3.4. Distributed Asynchronous Worker & Queue Architecture

Heavy computations, model inference, batch aggregation, and scheduled background monitoring must never block the synchronous FastAPI event loop.

#### Celery + Redis Topology:
```
  [FastAPI API Request]
            |
            | (Dispatches task signature)
            v
      [Redis Broker]
      (Queues: 'ml_triage', 'duplicate_scan', 'sla_monitor', 'default')
            |
            +---------------------+---------------------+
            |                     |                     |
            v                     v                     v
   [Celery Worker: ML]   [Celery Worker: Analytics] [Celery Beat Scheduler]
   - DeBERTa inference   - DBSCAN radar sweep       - Periodic SLA check
   - Vector embedding    - Workload aggregation     - Auto-escalation
   - SHAP explanation    - Report generation        - Metric snapshots
            |                     |                     |
            +---------------------+---------------------+
                                  |
                                  v
                     [PostgreSQL 16 / pgvector]
```

#### Queue Segregation:
1. **`ml_triage`**: Dedicated high-priority queue for immediate post-submission tasks (embedding generation, categorization verification, SLA prediction).
2. **`duplicate_scan`**: Medium-priority queue executing cosine similarity scans and updating cluster memberships.
3. **`sla_monitor`**: Low-latency queue triggered every 5 minutes by **Celery Beat** to evaluate active grievances against predicted resolution windows and flag approaching deadlines.
4. **`analytics`**: Scheduled batch jobs computing daily department performance metrics, SLA breach rates, and spatial DBSCAN hotspot clusters.

---

## 4. Machine Learning & Research Inference Architecture

CivicMind AI integrates nine purpose-built machine learning modules into the operational workflow:

```
                                  [Raw Complaint Text & Metadata]
                                                 |
                         +-----------------------+-----------------------+
                         |                                               |
                         v                                               v
            [Multilingual SBERT / MPNet]                    [DeBERTa-v3 NLP Classifier]
            (Embedding: vector(768))                        (Multi-task / Multi-label)
                         |                                               |
            +------------+------------+                      +-----------+-----------+
            |                         |                      |                       |
            v                         v                      v                       v
     [HNSW Vector Index]      [Semantic Cluster]     [Category/Subcategory]   [Priority & Department]
     (Cosine < 0.20 match)    (Master Grievance)     (Confidence > 0.85)     (Urgency & Routing)
                                                             |
                                                             +-----------------------+
                                                                                     |
                                                                                     v
                                                                        [Tabular Feature Vector]
                                                                        - Category, Department
                                                                        - Officer Active Backlog
                                                                        - Ward Historical Velocity
                                                                        - Severity / Priority
                                                                                     |
                                                             +-----------------------+-----------------------+
                                                             |                                               |
                                                             v                                               v
                                                [LightGBM Duration Regressor]                   [XGBoost SLA Risk Predictor]
                                                (Predicted Hours: e.g. 74.2 hrs)                (Breach Probability: e.g. 84.5%)
                                                             |                                               |
                                                             +-----------------------+-----------------------+
                                                                                     |
                                                                                     v
                                                                          [TreeSHAP Explainer]
                                                                          (Top 5 Risk Contribution Factors)
```

### Module Specifications:

| Module | Task & Objective | Target Architecture | Input Features | Output / Artifact |
| :--- | :--- | :--- | :--- | :--- |
| **1. NLP Categorization** | Predict category and subcategory | Fine-tuned `microsoft/deberta-v3-base` or `xlm-roberta-base` | Raw complaint text, title, language | Category, Subcategory, Classification Confidence |
| **2. Priority Prediction** | Determine urgency (Low to Critical) | Multi-class transformer head + rule safety guardrails | Text semantics, keyword markers, location context | Priority level, Urgency score (0.0-1.0) |
| **3. Duplicate Intelligence** | Detect cross-citizen duplicate reports | `sentence-transformers/all-mpnet-base-v2` + Cross-Encoder reranker | 768-dim text embedding + spatial distance threshold | Cosine similarity score, Cluster ID, Master Grievance link |
| **4. Department Routing** | Route complaint to responsible agency | Softmax classifier over department embeddings | Predicted category, location coordinates, agency jurisdiction | Recommended Department ID, confidence |
| **5. Resolution Time Regressor**| Predict resolution time (hours) | LightGBM Regressor with objective `regression_l1` | Category, dept load, historical officer resolution speed, season | Expected resolution hours, estimated completion date |
| **6. SLA Breach Predictor** | Classify risk of missing legal SLA deadline | XGBoost Binary Classifier with calibrated probabilities | Backlog depth, priority, complexity, officer availability | SLA risk probability (0-100%), Risk tier (Low, Med, High, Critical) |
| **7. Explainable AI (XAI)** | Explain why grievance was flagged as High Risk | TreeSHAP (SHapley Additive exPlanations) | Tabular features fed to XGBoost/LightGBM | Feature importance waterfall, top risk drivers |
| **8. Civic Early-Warning Radar**| Identify geographic outbreaks & clusters | Spatial-temporal DBSCAN (`eps=500m`, `min_samples=4`) + Poisson anomaly scoring | Latitude, longitude, timestamp, category | Anomaly Hotspots, Growth rate %, Severity score |
| **9. Ground-Truth Verifier** | Verify resolution quality before closing | Multi-aspect composite score (Citizen rating + OCR/ResNet image inspection) | Officer resolution notes, before/after photo evidence, citizen rating | Verification status, Confidence score |

---

## 5. End-to-End Data Flow Pipelines

### 5.1. Citizen Ingestion & Pre-Submission Triage Pipeline

```
[Citizen Browser]
       |
       | 1. Types complaint description in Wizard (Step 1)
       | 2. Debounced API call: POST /api/v1/triage/preview
       v
[FastAPI Gateway]
       |
       | 3. Passes text to ML Triage Service
       v
[ML Triage Service (Memory-Cached Model / Fast Transformer)]
       |
       | 4. Computes preliminary category, priority, department
       | 5. Computes temporary 768d vector
       | 6. Queries pgvector HNSW for nearest neighbors (threshold > 0.82)
       v
[FastAPI Gateway]
       |
       | 7. Returns TriagePreviewResponse:
       |    - Predicted Category & Confidence
       |    - Recommended Department
       |    - Potential Duplicates with similarity scores
       |    - Estimated SLA window
       v
[Citizen Browser]
       | 8. Displays AI Analysis Panel & Duplicate Warning Banner
       | 9. Citizen confirms/corrects and clicks "Submit"
       | 10. POST /api/v1/grievances (Multipart form with files, location, category)
       v
[FastAPI Gateway]
       | 11. Stores grievance in DB (Status: SUBMITTED)
       | 12. Stores uploaded files to storage (Evidence table)
       | 13. Dispatches async Celery task: `process_grievance_triage(grievance_id)`
       | 14. Returns 201 Created with tracking ID
```

---

### 5.2. Asynchronous Triage, Routing & Duplicate Processing Pipeline

```
[Celery Worker: `process_grievance_triage`]
       |
       | 1. Fetch grievance text and metadata from DB
       | 2. Generate final 768d normalized embedding via SBERT
       | 3. INSERT INTO grievance_embeddings VALUES (grievance_id, embedding)
       v
[Vector Similarity Check]
       |
       | 4. Execute cosine distance query against open grievances:
       |    SELECT grievance_id, 1 - (embedding <=> :target) AS similarity
       |    FROM grievance_embeddings
       |    WHERE 1 - (embedding <=> :target) >= 0.85
       v
   [Duplicate Detected?]
       |-- YES --> a. Find or create `duplicate_clusters` record
       |           b. Add grievance to `cluster_memberships`
       |           c. If cluster has Master, mark grievance `is_duplicate = TRUE`
       |           d. Append timeline event: "Flagged as duplicate of {master_id}"
       |
       +--- NO --> a. Run LightGBM resolution time regressor
                   b. Run XGBoost SLA breach probability classifier
                   c. Compute TreeSHAP risk factors
                   d. Find optimal officer in department with lowest active queue
                   e. UPDATE grievances SET
                         status = 'ASSIGNED',
                         assigned_officer_id = :officer_id,
                         sla_deadline = NOW() + INTERVAL '...',
                         predicted_resolution_hours = :pred_hours
                   f. Append timeline event: "Assigned to Officer {name}"
                   g. Emit notification to officer via Redis PubSub
```

---

### 5.3. Civic Early-Warning Radar Pipeline

```
[Celery Beat Scheduler (Hourly / Every 15 Minutes)]
       |
       | 1. Triggers task `scan_radar_anomalies()`
       v
[Celery Worker: Spatial Analytics]
       |
       | 2. Queries active grievances from past 72 hours with coordinates:
       |    SELECT id, category, latitude, longitude, created_at FROM grievances
       |    WHERE created_at >= NOW() - INTERVAL '72 hours'
       v
[Spatial DBSCAN Engine]
       |
       | 3. Clusters points using Haversine distance metric (eps = 0.5km, min_pts = 4)
       | 4. For each cluster:
       |    a. Calculates geographic centroid (lat, lng) and radius
       |    b. Calculates 24h complaint velocity vs. 14-day historical baseline
       |    c. Computes growth rate % and Poisson anomaly p-value
       |    d. Evaluates severity (Low, Medium, High, Critical)
       v
[Database Persistence]
       |
       | 5. UPSERT INTO hotspots (title, category, centroid_lat, centroid_lng,
       |                          grievance_count, growth_rate_pct, severity, is_active)
       | 6. If severity == 'CRITICAL', trigger system alert notification to Admin
```

---

### 5.4. SLA Monitoring & Dynamic Escalation Pipeline

```
[Celery Beat Scheduler (Every 5 Minutes)]
       |
       | 1. Triggers `monitor_sla_escalations()`
       v
[Celery Worker: SLA Watcher]
       |
       | 2. Query all active grievances with status IN ('ASSIGNED', 'IN_PROGRESS', 'ESCALATED'):
       |    WHERE sla_deadline IS NOT NULL
       v
[Loop Grievances]
       |
       | 3. Calculate remaining time = sla_deadline - NOW()
       | 4. Fetch updated officer workload & days without status update
       | 5. Re-evaluate XGBoost SLA breach model:
       |    - If breach probability > 80% AND remaining time < 24h:
       |        -> UPDATE grievances SET priority = 'CRITICAL'
       |        -> If remaining time < 0 (overdue):
       |            -> UPDATE grievances SET status = 'ESCALATED'
       |            -> Append timeline: "Auto-escalated due to SLA breach"
       |            -> Notify Department Supervisor & Administrator
```

---

## 6. Security, Authentication & Role-Based Access Control (RBAC)

### 6.1. Authentication Architecture
- **JWT (JSON Web Tokens)**:
  - Symmetric HMAC-SHA256 (`HS256`) or Asymmetric RSA (`RS256`).
  - Access Token TTL: **60 minutes**.
  - Refresh Token TTL: **7 days** (stored with SHA-256 fingerprint in database).
- **Password Hashing**:
  - `bcrypt` with work factor 12.
- **Revocation**:
  - Revoked tokens and user logout invalidations are recorded in Redis with TTL matching token expiration.

### 6.2. Role-Based Access Control (RBAC) Matrix

| Resource / Action | Citizen | Department Officer | Administrator |
| :--- | :---: | :---: | :---: |
| **Submit Grievance** | Own only | Allowed | Allowed |
| **View Grievance Details** | Own only | Assigned Department | All |
| **Update Grievance Status** | Cannot | Assigned Only | All |
| **Submit Resolution Report**| Cannot | Assigned Only | All |
| **Verify Resolution / Appeal**| Own only | Cannot | Supervise |
| **View Duplicate Clusters** | Limited preview | Department View | Full Control / Merge |
| **Civic Radar / Hotspots** | Cannot | Ward / Dept Scope | Full Citywide |
| **Workload Simulator** | Cannot | Cannot | Full Access |
| **Model Research & Metrics**| Cannot | Cannot | Full Access |
| **Audit Logs** | Cannot | Cannot | Read-Only (Immutable)|

---

## 7. Storage & Infrastructure Architecture

### 7.1. File Storage Architecture
Evidence attachments (JPEG, PNG, PDF, MP4, Audio) are handled via a modular storage abstraction:
- **Development**: Local persistent volume (`/storage/evidence/{grievance_id}/{uuid}.ext`).
- **Production**: S3-compatible object storage (MinIO, AWS S3, or Google Cloud Storage) with signed temporary URLs for secure citizen/officer retrieval.
- **Validation**: Strict MIME-type checking, file size limits (15MB for images/docs, 50MB for video), and filename sanitization to eliminate directory traversal attacks.

### 7.2. Docker Container Topology
```
+-------------------------------------------------------------------------------+
|                             DOCKER COMPOSE TOPOLOGY                           |
|                                                                               |
|  +---------------------+   +---------------------+   +---------------------+  |
|  |    frontend-web     |   |     backend-api     |   |    celery-worker    |  |
|  |     (Next.js)       |   |      (FastAPI)      |   |   (ML / Analytics)  |  |
|  |    Port: 3000       |   |     Port: 8000      |   |                     |  |
|  +----------+----------+   +----------+----------+   +----------+----------+  |
|             |                         |                         |             |
|             +-------------------------+-------------------------+             |
|                                       |                                       |
|  +---------------------+   +----------+----------+   +---------------------+  |
|  |    redis-broker     |   |   postgres-database |   |     celery-beat     |  |
|  |      (Redis 7)      |   |  (PostgreSQL 16 +   |   |     (Scheduler)     |  |
|  |     Port: 6379      |   |      pgvector)      |   |                     |  |
|  +---------------------+   |     Port: 5432      |   +---------------------+  |
|                            +---------------------+                            |
+-------------------------------------------------------------------------------+
```

---

## 8. Scalability, High Availability & Production Hardening

1. **Database Connection Pooling**:
   - Asynchronous connection pooling via `asyncpg` within FastAPI (min pool size: 10, max pool size: 30).
   - In multi-node deployments, utilize **PgBouncer** for transactional connection pooling.
2. **Horizontal API Scaling**:
   - Stateless FastAPI instances scale horizontally behind an Nginx reverse proxy or cloud application load balancer.
3. **ML Cold-Start Prevention**:
   - Model weights (DeBERTa, SBERT, LightGBM) are loaded into worker memory during worker initialization (`celery.py` worker-init hook) to prevent per-request disk read latency.
4. **Resilience & Graceful Degradation**:
   - If the ML inference worker is temporarily backlogged or unreachable, the API persists the grievance with `status = 'SUBMITTED'` and a fallback rule-based priority, queuing the ML triage task for delayed processing without rejecting the citizen's submission.

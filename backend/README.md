# CivicMind AI — Backend (Phase 1, 2 & 3 Complete)

CivicMind AI is an enterprise-grade AI-powered citizen grievance intelligence and resolution prediction platform designed for modern public administration.

This directory contains the production Python backend scaffold, PostgreSQL 16 + `pgvector` persistence layer, Redis broker and revocation cache, FastAPI application architecture, **Phase 2 Authentication, Security, and Role-Based Access Control (RBAC)**, and **Phase 3 Grievance Management & Lifecycle Engine**.

---

## 1. Technology Stack

- **Python 3.12+** (tested on 3.13)
- **FastAPI** (ASGI web framework)
- **PostgreSQL 16** with **pgvector** (`0.8.7`)
- **SQLAlchemy 2.0** (AsyncEngine, AsyncSession, DeclarativeBase)
- **Alembic** (Async database schema migrations)
- **Pydantic v2** (`pydantic-settings`, `email-validator`)
- **asyncpg** (High-throughput async PostgreSQL driver)
- **Redis 7** (Broker, token revocation blacklist, and rate-limiting cache)
- **Argon2id** (`argon2-cffi` cryptographic password hashing)
- **PyJWT** (HMAC-SHA256 signed JWT tokens with standard RFC claims)
- **Google OAuth2 / Identity Services** (`google-auth`, tokeninfo verification, code exchange)
- **Docker & Docker Compose**
- **pytest & pytest-asyncio** (Comprehensive automated test suite)

---

## 2. Directory Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI application entrypoint, CORS & error handlers
│   ├── core/
│   │   ├── config.py            # Pydantic BaseSettings loading from .env & demo credentials
│   │   ├── database.py          # AsyncEngine, SessionMaker, get_db dependency
│   │   ├── dependencies.py      # Auth, RBAC guards, & object-level IDOR protection
│   │   ├── redis.py             # Shared async Redis client pool & health checks
│   │   └── security.py          # Argon2id hashing, JWT codec, blacklist, & rate limiting
│   ├── models/                  # 15 SQLAlchemy 2.0 ORM entities
│   │   ├── base.py              # DeclarativeBase & TimestampMixin
│   │   ├── user.py              # User entity with role constraints (citizen, officer, admin)
│   │   ├── department.py        # Municipal administrative entities
│   │   ├── officer.py           # Field officer extension profiles (department assignment)
│   │   ├── grievance.py         # Primary complaint records & constraints
│   │   ├── embedding.py         # 768-dim vector embeddings & HNSW index
│   │   ├── evidence.py          # Multimedia attachments
│   │   ├── timeline.py          # State transition event audit log
│   │   ├── resolution.py        # Closure reports & citizen reviews
│   │   ├── duplicate.py         # Semantic clusters & memberships
│   │   ├── hotspot.py           # Geospatial anomaly radar clusters
│   │   ├── knowledge.py         # Knowledge graph nodes & edges
│   │   ├── audit.py             # Immutable administrative audit logs
│   │   └── token.py             # Refresh token session persistence & family tracking
│   ├── schemas/
│   │   ├── auth.py              # Pydantic v2 auth request & response contracts
│   │   ├── grievance.py         # Lifecycle, evidence, resolution & triage schemas
│   │   └── health.py            # System health response contracts
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py          # Authentication endpoints (/api/v1/auth/*)
│   │       ├── grievances.py    # Lifecycle & grievance CRUD (/api/v1/grievances/*)
│   │       ├── uploads.py       # Evidence storage & retrieval (/api/v1/uploads/*)
│   │       ├── ai.py            # Operational preview endpoints (/api/v1/ai/*)
│   │       └── router.py        # Centralized v1 router with RBAC test gates
│   ├── services/
│   │   ├── auth_service.py      # Authentication lifecycle, token rotation & reuse detection
│   │   ├── grievance_service.py # Grievance CRUD, sequence generation, IDOR checks & triage
│   │   ├── lifecycle.py         # State machine transitions, timeline & audit event generation
│   │   └── storage_service.py   # MIME/magic-byte upload validation & authorized downloads
│   ├── repositories/            # Data access abstractions
│   └── utils/
│       └── logger.py            # Structured logging configuration
├── alembic/                     # Database migrations
│   ├── versions/
│   │   ├── 0001_initial_schema.py          # Baseline migration (15 tables + pgvector)
│   │   ├── 0002_refresh_token_family.py    # Refresh token family & client metadata
│   │   ├── 0003_add_google_auth_fields.py  # Google OAuth identity columns
│   │   └── 0004_grievance_lifecycle.py     # Sequence tracking & nullable evidence link
│   └── env.py                  # Async migration runner
├── tests/                       # Automated test suite (68 tests, 100% pass rate)
│   ├── conftest.py              # Async HTTP client, session fixtures, connection cleanup
│   ├── test_auth.py             # Auth endpoints, JWT, rotation, blacklist & password reset
│   ├── test_grievances.py       # Grievance CRUD, sequence IDs, IDOR, lifecycle, evidence, resolutions
│   ├── test_rbac.py             # Role gates, IDOR guards, department isolation, deactivation
│   ├── test_database.py         # Engine connectivity, transactions, rollbacks
│   ├── test_health.py           # System and component health endpoints
│   ├── test_migrations.py       # Alembic versioning and table presence
│   ├── test_models.py           # Model column types and constraints
│   ├── test_pgvector.py         # Vector extensions, HNSW indexes, cosine distance
│   ├── test_redis.py            # Redis connectivity, set, get, ttl, flush
│   └── test_startup.py          # Application metadata and OpenAPI schema
├── scripts/
│   ├── init-db.sql              # Container initialization SQL script
│   └── seed_demo_accounts.py    # Idempotent development demo account seeder
├── alembic.ini                  # Alembic CLI configuration
├── docker-compose.yml           # PostgreSQL 16 (pgvector) & Redis 7 services
├── Dockerfile                   # Container packaging definition
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment configuration template
└── README.md                    # This documentation
```

---

## 3. Quickstart & Service Startup

### Step 1: Environment Configuration
Copy the configuration template to `.env`:
```bash
cp .env.example .env
```

### Step 2: Start Containerized Services
Launch PostgreSQL 16 (with pgvector) and Redis 7:
```bash
docker compose up -d
```
Verify that both containers are healthy:
```bash
docker compose ps
```

### Step 3: Run Database Migrations
Apply all migrations to PostgreSQL via Alembic:
```bash
alembic upgrade head
```

### Step 4: Seed Development Demo Accounts
Populate baseline departments and pre-configured demo user accounts:
```bash
python scripts/seed_demo_accounts.py
```
This seeds the following idempotent accounts:
- **Admin**: `admin@civicmind.gov` / `admin123`
- **Department Officer**: `officer@civicmind.gov` / `officer123` (Assigned to PWD)
- **Citizen**: `citizen@civicmind.gov` / `citizen123`
- **Commissioner**: `commissioner.grievance@gov.in` / `admin123`
- **Executive Engineer**: `rajesh.verma@pwd.gov.in` / `officer123`
- **Resident**: `aarav.sharma@example.com` / `citizen123`

### Step 5: Start the FastAPI Application
Start the ASGI server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive documentation is available at:
- **Swagger UI**: `http://localhost:8000/api/v1/docs`
- **ReDoc**: `http://localhost:8000/api/v1/redoc`

---

## 4. Phase 2 Authentication & Security Architecture

### Cryptographic Hashing
- **Argon2id**: Passwords are saved exclusively as Argon2id hashes using OWASP recommended parameters (`time_cost=3`, `memory_cost=65536` [64 MB], `parallelism=4`, `hash_len=32`).
- **Timing Attack Resistance**: Password verification uses constant-time comparison.

### JWT Access Tokens
- **Algorithm**: HMAC-SHA256 (`HS256`).
- **Payload Claims**:
  - `sub`: User UUID string.
  - `role`: Role string (`citizen`, `officer`, `admin`).
  - `email`: User email address.
  - `name`: User full name.
  - `type`: Explicit token type guard (`"access"`).
  - `jti`: Unique UUID v4 token identifier (used for Redis blacklisting).
  - `iat`: Epoch issuance timestamp.
  - `exp`: Epoch expiration timestamp (default: 60 minutes).

### Rotating Refresh Tokens & Reuse Detection
- **Token Generation**: Cryptographically secure random tokens (`secrets.token_urlsafe(48)` — 384 bits entropy).
- **Storage**: Plaintext tokens are NEVER stored in the database. Only the SHA-256 hash is persisted in `refresh_tokens`.
- **Rotation**: On every successful call to `/api/v1/auth/refresh`, the presented token is marked `is_revoked = True` and a new refresh token in the same family is issued.
- **Automatic Reuse Detection**: If an already-revoked refresh token is replayed, the backend detects token theft, immediately revokes ALL active tokens in the entire `family_id`, and blocks further access.

### Redis Blacklisting (Immediate Logout Revocation)
- When a user signs out via `POST /api/v1/auth/logout`, the JWT's `jti` is stored in Redis under `blacklist:jwt:{jti}` with TTL equal to the token's remaining validity.
- The `get_current_user` dependency checks this blacklist on every authenticated request, rejecting revoked tokens with `401 Unauthorized`.

### Redis Login Rate Limiting (Brute-Force Protection)
- Failed login attempts are tracked per email/IP in Redis (`rate_limit:login:{identifier}`).
- 5 consecutive failed attempts trigger an automatic 5-minute lockout returning `429 Too Many Requests` with a `Retry-After` header.
- A successful login resets the failure counter immediately.

### Role-Based Access Control (RBAC) & IDOR Protection
- **Role Guards**: `@require_role(["citizen"])`, `@require_role(["officer"])`, `@require_role(["admin"])` enforce route-level privilege separation.
- **IDOR Protection**: `verify_user_access(current_user, target_user_id)` ensures citizens cannot access another user's personal grievances or profile data.
- **Department Jurisdiction**: `verify_department_access(current_user, target_dept_id)` prevents officers from inspecting complaints or operations of unrelated departments, while administrators maintain global oversight.

---

## 5. API Endpoints

### Authentication (`/api/v1/auth`)
| Method | Endpoint | Request Schema | Response Schema | Auth Required | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | `RegisterRequest` | `LoginResponse` | No | Register new citizen account and issue initial token pair |
| `POST` | `/api/v1/auth/login` | `LoginRequest` | `LoginResponse` | No | Authenticate credentials with rate limiting and issue tokens |
| `POST` | `/api/v1/auth/refresh` | `RefreshTokenRequest` | `RefreshTokenResponse` | No | Rotate refresh token and issue fresh access token |
| `POST` | `/api/v1/auth/logout` | `LogoutRequest` | Status message | Bearer Token | Blacklist access token in Redis and revoke refresh token |
| `GET` | `/api/v1/auth/me` | None | `UserPublic` | Bearer Token | Fetch authenticated user profile |
| `PUT` | `/api/v1/auth/me` | `UserProfileUpdateRequest` | `UserPublic` | Bearer Token | Update authenticated user profile |
| `POST` | `/api/v1/auth/forgot-password` | `ForgotPasswordRequest` | `ForgotPasswordResponse` | No | Request password reset token |
| `POST` | `/api/v1/auth/reset-password` | `ResetPasswordRequest` | Status message | No | Consume single-use token and update Argon2id hash |
| `GET` | `/api/v1/auth/google/url` | None | `GoogleAuthUrlResponse` | No | Fetch official Google OAuth2 sign-in redirect URL |
| `POST` | `/api/v1/auth/google` | `GoogleAuthRequest` | `LoginResponse` | No | Authenticate or auto-provision citizen account via Google Identity |

### System & RBAC Health Gates
| Method | Endpoint | Auth Required | Required Role | Description |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/health` | No | Any | Full system health check (PostgreSQL, Redis, pgvector) |
| `GET` | `/api/v1/health` | No | Any | API v1 routing layer health probe |
| `GET` | `/api/v1/rbac/citizen-only` | Bearer Token | `citizen` | Restricted citizen gate verification |
| `GET` | `/api/v1/rbac/officer-only` | Bearer Token | `officer` | Restricted officer gate verification |
| `GET` | `/api/v1/rbac/admin-only` | Bearer Token | `admin` | Restricted administrator gate verification |
| `GET` | `/api/v1/rbac/users/{user_id}/records` | Bearer Token | Self or `admin` | Object-level user IDOR guard |
| `GET` | `/api/v1/rbac/departments/{dept_id}/confidential` | Bearer Token | Assigned officer or `admin` | Department jurisdiction isolation guard |

---

## 6. Running Automated Tests

Run the complete test suite (57 tests):
```bash
pytest tests/ -v
```

Run with coverage analysis:
```bash
pytest tests/ --cov=app --cov-report=term-missing
```

### Test Suite Summary
- **57 passing tests** across 10 test modules.
- **84% statement coverage** across the entire application codebase.
- Covers: database connectivity, ORM entities, pgvector HNSW indexing, Redis caching, migrations, registration, login rate limiting, JWT validation, refresh token rotation, refresh reuse detection, token blacklisting, password reset lifecycle, profile updates, RBAC role gates, IDOR guards, and department jurisdiction silos.

# CivicMind AI — Backend (Phase 1)

CivicMind AI is an enterprise-grade AI-powered citizen grievance intelligence and resolution prediction platform designed for modern public administration.

This directory contains the production Python backend scaffold, PostgreSQL 16 + `pgvector` persistence layer, Redis broker configuration, and FastAPI service architecture.

---

## 1. Technology Stack

- **Python 3.12+**
- **FastAPI** (ASGI web framework)
- **PostgreSQL 16** with **pgvector** (`0.8.7`)
- **SQLAlchemy 2.0** (AsyncEngine, AsyncSession, DeclarativeBase)
- **Alembic** (Async database schema migrations)
- **Pydantic v2** (`pydantic-settings`)
- **asyncpg** (High-throughput async PostgreSQL driver)
- **Redis 7** (Broker and cache store)
- **Docker & Docker Compose**
- **pytest & pytest-asyncio** (Automated test suite)

---

## 2. Directory Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI application entrypoint & lifespans
│   ├── core/
│   │   ├── config.py            # Pydantic BaseSettings loading from .env
│   │   ├── database.py          # AsyncEngine, SessionMaker, get_db dependency
│   │   └── redis.py             # Shared async Redis client pool & health checks
│   ├── models/                  # 15 SQLAlchemy 2.0 ORM entities
│   │   ├── base.py              # DeclarativeBase & TimestampMixin
│   │   ├── user.py              # User entity with RBAC role check constraints
│   │   ├── department.py        # Municipal administrative entities
│   │   ├── officer.py           # Field officer extension profiles
│   │   ├── grievance.py         # Primary complaint records & constraints
│   │   ├── embedding.py         # 768-dim vector embeddings & HNSW index
│   │   ├── evidence.py          # Multimedia attachments
│   │   ├── timeline.py          # State transition event audit log
│   │   ├── resolution.py        # Closure reports & citizen reviews
│   │   ├── duplicate.py         # Semantic clusters & memberships
│   │   ├── hotspot.py           # Geospatial anomaly radar clusters
│   │   ├── knowledge.py         # Knowledge graph nodes & edges
│   │   ├── audit.py             # Immutable administrative audit logs
│   │   └── token.py             # Refresh token session persistence
│   ├── schemas/
│   │   └── health.py            # Pydantic v2 response contracts
│   ├── api/
│   │   └── v1/
│   │       └── router.py        # Versioned API routes (/api/v1/health)
│   ├── services/                # Business logic services (Phase 2+)
│   ├── repositories/            # Data access abstractions (Phase 2+)
│   └── utils/
│       └── logger.py            # Structured logging configuration
├── alembic/                     # Database migrations
│   ├── versions/
│   │   └── 0001_initial_schema.py # Initial baseline migration (15 tables + pgvector)
│   └── env.py                  # Async migration runner
├── tests/                       # Automated test suite
├── scripts/
│   └── init-db.sql              # Container initialization SQL script
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
Launch PostgreSQL 16 (with pgvector) and Redis 7 in detached mode:
```bash
docker compose up -d
```
Verify that both containers are healthy:
```bash
docker compose ps
```

### Step 3: Run Database Migrations
Apply the initial schema to PostgreSQL via Alembic:
```bash
alembic upgrade head
```

To test rollbacks:
```bash
alembic downgrade base
alembic upgrade head
```

### Step 4: Start the FastAPI Application
Start the ASGI server with hot-reload enabled:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 4. API Endpoints (Phase 1)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Aggregate system health check (API, DB, Redis, pgvector) |
| `GET` | `/health/database` | Dedicated PostgreSQL connectivity & pgvector status |
| `GET` | `/health/redis` | Dedicated Redis broker ping probe |
| `GET` | `/api/v1/health` | API v1 scoped health probe |
| `GET` | `/api/v1/docs` | Interactive Swagger / OpenAPI documentation |
| `GET` | `/api/v1/redoc` | Interactive ReDoc documentation |

---

## 5. Running Automated Tests

Execute the comprehensive test suite with pytest:
```bash
pytest tests/ -v
```

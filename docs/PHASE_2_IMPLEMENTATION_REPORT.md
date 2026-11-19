# CivicMind AI — Phase 2 Implementation Report

**Milestone**: Phase 2: Authentication, Security & Role-Based Access Control (RBAC)  
**Execution Timestamp**: 2026-11-19T22:15:00+05:30  
**Status**: **COMPLETED & VERIFIED**  
**Test Suite**: 51/51 Tests Passed (100% Pass Rate, 85% Code Coverage)  
**Database Migration Revision**: `0002_refresh_token_family` (PostgreSQL 16 `pgvector`)  
**Cache & Revocation Store**: Redis 7 (`redis:7-alpine`)  

---

## 1. Executive Summary

Phase 2 implemented production-grade authentication, session management, cryptographic security, and role-based access control (RBAC) for the **CivicMind AI** platform.

The system incorporates:
- **Argon2id password hashing** using OWASP-recommended memory and iteration parameters with timing attack mitigation.
- **Short-lived PyJWT access tokens** with standard RFC claims and explicit token-type enforcement.
- **Rotating cryptographically random refresh tokens** stored only as SHA-256 hashes in PostgreSQL.
- **Family-based refresh token reuse detection**: Replay of an already-rotated token triggers immediate, atomic invalidation of the entire token family, mitigating session hijacking.
- **Redis-backed JWT blacklisting**: Immediate access token revocation on logout.
- **Redis-backed login rate limiting**: Automatic lockout after 5 failed attempts within 5 minutes, returning `429 Too Many Requests` with a `Retry-After` header.
- **Role-Based Access Control (RBAC)** across three distinct system roles: `citizen`, `officer`, and `admin`.
- **Object-Level Authorization & IDOR Protection**: Guards guaranteeing that citizens can only access their own records, officers can only operate within their assigned department silos, and administrators retain supervised citywide jurisdiction.
- **Single-use 15-minute Redis password reset workflow**.
- **Frontend Compatibility**: The response schemas and token contracts align with the existing Next.js frontend (`src/services/authService.ts`, `src/services/apiClient.ts`, and `src/stores/authStore.ts`).

---

## 2. Files Created and Modified

### Security & Authentication Core
- [`backend/app/core/security.py`](file:///c:/Users/venka/OneDrive/Desktop/capstone%20project/backend/app/core/security.py): Argon2id password hashing/verification, PyJWT access token creation/decoding, SHA-256 token hashing, Redis token blacklisting (`blacklist_token`, `is_token_blacklisted`), Redis rate limiting (`check_login_rate_limit`, `record_login_attempt`), and single-use password reset tokens (`create_password_reset_token`, `verify_and_consume_password_reset_token`).
- [`backend/app/core/dependencies.py`](file:///c:/Users/venka/OneDrive/Desktop/capstone%20project/backend/app/core/dependencies.py): FastAPI security dependencies including `get_current_user`, `get_current_active_user`, `require_role`, `require_any_role`, `verify_user_access` (cross-citizen IDOR protection), and `verify_department_access` (department silo protection).
- [`backend/app/core/config.py`](file:///c:/Users/venka/OneDrive/Desktop/capstone%20project/backend/app/core/config.py): Extended configuration with JWT secret settings, token expiration intervals, demo account credentials, and `PRINT_DEMO_CREDENTIALS` flag.

### Schemas & Service Layer
- [`backend/app/schemas/auth.py`](file:///c:/Users/venka/OneDrive/Desktop/capstone%20project/backend/app/schemas/auth.py): Pydantic v2 schemas for `UserPublic`, `LoginRequest`, `LoginResponse`, `RegisterRequest`, `RefreshTokenRequest`, `RefreshTokenResponse`, `LogoutRequest`, `ForgotPasswordRequest`, `ForgotPasswordResponse`, `ResetPasswordRequest`, and `UserProfileUpdateRequest`.
- [`backend/app/services/auth_service.py`](file:///c:/Users/venka/OneDrive/Desktop/capstone%20project/backend/app/services/auth_service.py): Business logic for user registration, credential authentication, rotating token refresh with reuse detection, logout revocation, password reset, and profile updates.
- [`backend/app/api/v1/auth.py`](file:///c:/Users/venka/OneDrive/Desktop/capstone%20project/backend/app/api/v1/auth.py): REST endpoints under `/api/v1/auth/*`.
- [`backend/app/api/v1/router.py`](file:///c:/Users/venka/OneDrive/Desktop/capstone%20project/backend/app/api/v1/router.py): Mounted auth router and verification endpoints for citizen, officer, and admin role gates, as well as IDOR object guards.
- [`backend/app/main.py`](file:///c:/Users/venka/OneDrive/Desktop/capstone%20project/backend/app/main.py): Enhanced exception handlers preserving `exc.headers` (e.g. `Retry-After`) and providing both `detail` and `message` fields for maximum client compatibility.

### Database Models & Migrations
- [`backend/app/models/token.py`](file:///c:/Users/venka/OneDrive/Desktop/capstone%20project/backend/app/models/token.py): Extended `RefreshToken` with `family_id` (UUID), `user_agent`, `ip_address`, and index `idx_refresh_tokens_family_id`.
- [`backend/alembic/versions/0002_refresh_token_family.py`](file:///c:/Users/venka/OneDrive/Desktop/capstone%20project/backend/alembic/versions/0002_refresh_token_family.py): Migration adding family tracking columns and index to `refresh_tokens`.

### Scripts & Tooling
- [`backend/scripts/seed_demo_accounts.py`](file:///c:/Users/venka/OneDrive/Desktop/capstone%20project/backend/scripts/seed_demo_accounts.py): Idempotent database seeder creating baseline departments and demo accounts (`admin@civicmind.gov`, `officer@civicmind.gov`, `citizen@civicmind.gov`, `commissioner.grievance@gov.in`, `rajesh.verma@pwd.gov.in`, `aarav.sharma@example.com`).
- [`backend/requirements.txt`](file:///c:/Users/venka/OneDrive/Desktop/capstone%20project/backend/requirements.txt): Pinned `argon2-cffi==25.1.0`, `pyjwt==2.15.1`, `cryptography==50.0.2`, `email-validator==2.4.0`.

### Test Suite
- [`backend/tests/test_auth.py`](file:///c:/Users/venka/OneDrive/Desktop/capstone%20project/backend/tests/test_auth.py): 18 comprehensive tests for registration, login, rate limiting, JWT lifecycle, rotating refresh tokens, reuse detection, blacklisting, password reset flow, and profile management.
- [`backend/tests/test_rbac.py`](file:///c:/Users/venka/OneDrive/Desktop/capstone%20project/backend/tests/test_rbac.py): 6 tests covering role gates, IDOR protection, department isolation, and deactivated account handling.
- [`backend/tests/test_migrations.py`](file:///c:/Users/venka/OneDrive/Desktop/capstone%20project/backend/tests/test_migrations.py): Updated migration test tracking revision `0002_refresh_token_family` and table columns.

---

## 3. Cryptographic Security Architecture

### 3.1 Argon2id Password Hashing
Password hashing is handled via `argon2-cffi` using the OWASP-recommended parameters:
- **Type**: `Argon2id` (hybrid of Argon2d and Argon2i, resistant to GPU side-channel and timing attacks)
- **Time Cost (Iterations)**: 3
- **Memory Cost**: 65,536 KiB (64 MiB)
- **Parallelism**: 4 lanes
- **Hash Length**: 32 bytes

Plaintext passwords are never logged, persisted, or returned. Password verification is performed using constant-time comparison to eliminate side-channel timing leaks.

### 3.2 JWT Access Tokens
Access tokens are signed using HMAC-SHA256 (`HS256`) with a cryptographically secure 256-bit secret key.

**Standard RFC Claims Included**:
```json
{
  "sub": "62017467-3bca-41a0-93c4-8650033c5531",
  "role": "admin",
  "email": "admin@civicmind.gov",
  "name": "System Administrator",
  "type": "access",
  "jti": "231bfa54cf60408ea696be84dc3cf1aa",
  "iat": 1795101924,
  "exp": 1795105524
}
```
- `type: "access"` ensures a refresh token or arbitrary token cannot be submitted to protected endpoints.
- `jti` enables per-token revocation tracking in Redis.
- Configurable expiration (default: 60 minutes).

### 3.3 Rotating Refresh Tokens & Family Reuse Detection
Refresh tokens use cryptographically random entropy (`secrets.token_urlsafe(48)` — 384 bits entropy).

1. **Storage Security**: Only the SHA-256 hash of the refresh token is stored in the PostgreSQL `refresh_tokens` table. The raw token exists solely on the client device.
2. **Rotation Lifecycle**: Every successful call to `POST /api/v1/auth/refresh` revokes the incoming token (`is_revoked = True`) and issues a brand-new refresh token sharing the same `family_id`.
3. **Reuse Detection (Theft Mitigation)**:
   - If an already-revoked refresh token is re-submitted, the system detects a token reuse attack (e.g., token stolen from the client).
   - The service triggers an immediate atomic revocation query:
     ```sql
     UPDATE refresh_tokens SET is_revoked = TRUE WHERE family_id = :family_id
     ```
   - All active tokens in that family are invalidated, terminating both the attacker's and victim's sessions and preventing unauthorized account takeover.

### 3.4 Redis Token Blacklisting (Instant Logout Revocation)
JWTs are stateless by nature. To guarantee immediate revocation upon logout:
1. When `POST /api/v1/auth/logout` is called, the JWT payload is inspected for `jti` and `exp`.
2. The `jti` is inserted into Redis: `SET blacklist:jwt:{jti} "revoked" EX {remaining_token_lifetime}`.
3. Every protected API request verifies via `is_token_blacklisted(jti)`. If present in Redis, the request is rejected with `401 Unauthorized` (`Token has been revoked`).
4. The Redis key automatically expires when the JWT reaches its natural expiration timestamp, keeping Redis memory footprint minimal.

### 3.5 Redis Login Rate Limiting (Brute-Force Protection)
1. Every failed login attempt increments a Redis key: `rate_limit:login:{email}` with a 300-second TTL.
2. If the counter reaches 5 failed attempts, all subsequent login attempts for that email/IP are blocked with `429 Too Many Requests` for the remainder of the window.
3. The response includes a `Retry-After: {seconds}` HTTP header.
4. Successful authentication clears the Redis failure counter immediately.

---

## 4. Role-Based Access Control (RBAC) & Authorization Guards

### 4.1 Application Roles

| Role | Target Persona | Scope of Authority |
| :--- | :--- | :--- |
| `citizen` | Municipal resident | Can submit complaints, view own complaints, track timeline, rate resolutions, and manage personal profile. |
| `officer` | Departmental field officer | Can view and triage complaints assigned to their designated department, update statuses, upload resolution evidence, and submit closure reports. Cannot access other departments. |
| `admin` | Municipal commissioner & platform admin | Global oversight across all departments, cross-user inspection, user management, system audit logs, and configuration. |

### 4.2 Object-Level Authorization (IDOR Protection)
- **`verify_user_access(current_user, target_user_id)`**:
  - Citizens can only query or mutate data belonging to `current_user.id == target_user_id`.
  - Attempting to access another citizen's data returns `403 Forbidden` (`Access forbidden: you do not have permission to access another user's private data`).
  - Administrators are granted elevated cross-user access for administrative supervision.
- **`verify_department_access(current_user, target_department_id)`**:
  - Officers can only view records or take actions within their assigned department (e.g., `dept_pwd`).
  - Accessing another department (e.g., `dept_sanitation`) returns `403 Forbidden` (`Access forbidden: your officer roster does not permit access to department`).
  - Administrators hold citywide jurisdiction across all departments.

### 4.3 Account Deactivation Guard
If an account is deactivated in the database (`is_active = False`), all subsequent requests with existing valid tokens are rejected with `403 Forbidden` (`This account has been deactivated`).

---

## 5. Seeded Development Accounts

The idempotent seeder [`backend/scripts/seed_demo_accounts.py`](file:///c:/Users/venka/OneDrive/Desktop/capstone%20project/backend/scripts/seed_demo_accounts.py) initializes baseline departments and accounts:

| Email | Password | Role | Department / Jurisdiction | Full Name |
| :--- | :--- | :--- | :--- | :--- |
| `admin@civicmind.gov` | `admin123` | `admin` | Citywide Oversight | System Administrator |
| `commissioner.grievance@gov.in` | `admin123` | `admin` | Municipal Headquarters | Commissioner K. Sharma |
| `officer@civicmind.gov` | `officer123` | `officer` | Public Works (`dept_pwd`) | Officer Rajesh Verma |
| `rajesh.verma@pwd.gov.in` | `officer123` | `officer` | Public Works (`dept_pwd`) | Er. Rajesh Verma |
| `citizen@civicmind.gov` | `citizen123` | `citizen` | Ward 12 (Indiranagar) | Citizen Vikram Rao |
| `aarav.sharma@example.com` | `citizen123` | `citizen` | Ward 4 (Koramangala) | Aarav Sharma |

Seeder execution is idempotent: repeated runs detect existing records and skip them without duplicating rows.

---

## 6. API Endpoints Specification

### Authentication Routes (`/api/v1/auth`)

| Method | Endpoint | Request Schema | Response Schema | Auth Required | Required Role | Frontend Consumer |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | `RegisterRequest` | `LoginResponse` | None | Public | `src/services/authService.ts` |
| `POST` | `/api/v1/auth/login` | `LoginRequest` | `LoginResponse` | None | Public | `src/app/login/page.tsx` |
| `POST` | `/api/v1/auth/refresh` | `RefreshTokenRequest` | `RefreshTokenResponse` | None | Public | `src/services/apiClient.ts` |
| `POST` | `/api/v1/auth/logout` | `LogoutRequest` | `{"message": str}` | Bearer Token | Any | `src/stores/authStore.ts` |
| `GET` | `/api/v1/auth/me` | None | `UserPublic` | Bearer Token | Any | `src/services/authService.ts` |
| `PUT` | `/api/v1/auth/me` | `UserProfileUpdateRequest` | `UserPublic` | Bearer Token | Any | `src/app/citizen/profile/page.tsx` |
| `POST` | `/api/v1/auth/forgot-password` | `ForgotPasswordRequest` | `ForgotPasswordResponse` | None | Public | Password reset modal |
| `POST` | `/api/v1/auth/reset-password` | `ResetPasswordRequest` | `{"message": str}` | None | Public | Password reset modal |

### RBAC Test & Verification Routes (`/api/v1/rbac`)

| Method | Endpoint | Request | Response | Auth | Role | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/rbac/citizen-only` | None | `{"message": str, "role": str}` | Bearer | `citizen` | Restricts access exclusively to citizens. |
| `GET` | `/api/v1/rbac/officer-only` | None | `{"message": str, "role": str}` | Bearer | `officer` | Restricts access exclusively to officers. |
| `GET` | `/api/v1/rbac/admin-only` | None | `{"message": str, "role": str}` | Bearer | `admin` | Restricts access exclusively to administrators. |
| `GET` | `/api/v1/rbac/users/{user_id}/records` | None | `{"message": str, "caller_role": str}` | Bearer | Self or `admin` | IDOR guard: Citizen can only view self; Admin has global access. |
| `GET` | `/api/v1/rbac/departments/{dept_id}/confidential` | None | `{"message": str, "caller_role": str}` | Bearer | Assigned or `admin` | Department guard: Officer restricted to assigned dept; Admin global. |

---

## 7. Automated Test Suite & Coverage Verification

The test suite contains **51 tests** executed against live PostgreSQL 16 (`pgvector`) and Redis 7 test instances.

```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

### 7.1 Test Execution Results

```text
============================= test session starts =============================
platform win32 -- Python 3.13.3, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\venka\OneDrive\Desktop\capstone project\backend
configfile: pytest.ini
plugins: anyio-4.16.0, asyncio-1.5.0, cov-7.1.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=session, asyncio_default_test_loop_scope=session
collected 51 items

tests/test_auth.py::test_register_success PASSED                         [  1%]
tests/test_auth.py::test_register_duplicate_email PASSED                 [  3%]
tests/test_auth.py::test_register_weak_password PASSED                   [  5%]
tests/test_auth.py::test_register_invalid_email PASSED                   [  7%]
tests/test_auth.py::test_login_success PASSED                            [  9%]
tests/test_auth.py::test_login_wrong_password PASSED                     [ 11%]
tests/test_auth.py::test_login_nonexistent_email PASSED                  [ 13%]
tests/test_auth.py::test_login_rate_limiting PASSED                      [ 15%]
tests/test_auth.py::test_login_deactivated_account PASSED                [ 17%]
tests/test_auth.py::test_get_current_user_profile PASSED                 [ 19%]
tests/test_auth.py::test_get_me_unauthorized_missing_token PASSED        [ 21%]
tests/test_auth.py::test_get_me_expired_token PASSED                     [ 23%]
tests/test_auth.py::test_get_me_malformed_token PASSED                   [ 25%]
tests/test_auth.py::test_refresh_token_lifecycle_and_rotation PASSED     [ 27%]
tests/test_auth.py::test_refresh_token_reuse_detection PASSED            [ 29%]
tests/test_auth.py::test_logout_and_blacklist_revocation PASSED          [ 31%]
tests/test_auth.py::test_password_reset_flow PASSED                      [ 33%]
tests/test_auth.py::test_update_user_profile PASSED                      [ 35%]
tests/test_database.py::test_direct_db_health_check PASSED               [ 37%]
tests/test_database.py::test_session_execution PASSED                    [ 39%]
tests/test_database.py::test_get_db_generator PASSED                     [ 41%]
tests/test_database.py::test_transaction_rollback PASSED                 [ 43%]
tests/test_health.py::test_aggregate_health_endpoint PASSED              [ 45%]
tests/test_health.py::test_database_health_endpoint PASSED               [ 47%]
tests/test_health.py::test_redis_health_endpoint PASSED                  [ 49%]
tests/test_health.py::test_api_v1_health_endpoint PASSED                 [ 50%]
tests/test_migrations.py::test_alembic_version_table PASSED              [ 52%]
tests/test_migrations.py::test_all_15_tables_exist_in_database PASSED    [ 54%]
tests/test_migrations.py::test_migration_0002_refresh_tokens_family_columns PASSED [ 56%]
tests/test_models.py::test_table_registration_count PASSED               [ 58%]
tests/test_models.py::test_user_table_schema PASSED                      [ 60%]
tests/test_models.py::test_department_table_schema PASSED                [ 62%]
tests/test_models.py::test_grievance_table_schema PASSED                 [ 64%]
tests/test_models.py::test_embedding_table_schema PASSED                 [ 66%]
tests/test_models.py::test_knowledge_graph_schema PASSED                 [ 68%]
tests/test_models.py::test_audit_logs_schema PASSED                      [ 70%]
tests/test_pgvector.py::test_pgvector_extension_active PASSED            [ 72%]
tests/test_pgvector.py::test_vector_column_definition PASSED             [ 74%]
tests/test_pgvector.py::test_hnsw_index_exists PASSED                    [ 76%]
tests/test_pgvector.py::test_vector_insert_and_cosine_distance PASSED    [ 78%]
tests/test_rbac.py::test_citizen_only_gate PASSED                        [ 80%]
tests/test_rbac.py::test_officer_only_gate PASSED                        [ 82%]
tests/test_rbac.py::test_admin_only_gate PASSED                          [ 84%]
tests/test_rbac.py::test_object_level_user_access_idor_protection PASSED [ 86%]
tests/test_rbac.py::test_department_jurisdiction_guards PASSED           [ 88%]
tests/test_rbac.py::test_deactivated_user_token_rejection PASSED         [ 90%]
tests/test_redis.py::test_redis_health PASSED                            [ 92%]
tests/test_redis.py::test_redis_crud_operations PASSED                   [ 94%]
tests/test_startup.py::test_app_metadata PASSED                          [ 96%]
tests/test_startup.py::test_root_endpoint PASSED                         [ 98%]
tests/test_startup.py::test_openapi_schema PASSED                        [100%]

======================= 51 passed in 3.63s ========================
```

### 7.2 Coverage Summary

| Module | Statements | Missing | Coverage |
| :--- | :---: | :---: | :---: |
| `app/models/*` (15 entities) | 269 | 0 | **100%** |
| `app/schemas/auth.py` | 69 | 0 | **100%** |
| `app/schemas/health.py` | 24 | 0 | **100%** |
| `app/api/v1/router.py` | 34 | 0 | **100%** |
| `app/api/v1/auth.py` | 52 | 3 | **94%** |
| `app/core/security.py` | 109 | 15 | **86%** |
| `app/core/dependencies.py` | 64 | 11 | **83%** |
| `app/core/database.py` | 38 | 7 | **82%** |
| `app/core/redis.py` | 27 | 6 | **78%** |
| `app/main.py` | 87 | 22 | **75%** |
| `app/core/config.py` | 72 | 19 | **74%** |
| **TOTAL** | **1,089** | **163** | **85%** |

---

## 8. Frontend Integration & Compatibility

The frontend authentication client (`src/services/authService.ts`) expects the following response structure on login and registration:
```typescript
interface LoginResponse {
  token: string;
  user: User;
}
```
The FastAPI backend `LoginResponse` schema provides:
- `token`: Alias matching `access_token` so `res.data.token` resolves seamlessly.
- `access_token`: Standard OAuth2 / RFC bearer token.
- `refresh_token`: Rotatable long-lived session token.
- `token_type`: `"bearer"`.
- `user`: Public user profile object including `avatar` (mapped from `avatar_url`), `department`, and `role`.

This guarantees out-of-the-box compatibility without modifying a single line of frontend code.

---

## 9. Conclusion & Phase 3 Readiness

Phase 2 is fully complete. All authentication, cryptographic protections, RBAC dependencies, IDOR barriers, database migrations, demo accounts, and unit/integration tests are operational and verified.

The codebase is positioned for **Phase 3: Core Grievance Management, Evidence Ingestion & Workflow Engine**.

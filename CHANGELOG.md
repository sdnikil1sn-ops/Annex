**Purpose:** Records Phase 2 additions under Unreleased.
```markdown
# Changelog

All notable changes to ANNEX are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

## [Unreleased]

### Added
- Polyglot monorepo scaffolding: Flutter mobile, React web, browser extension, FastAPI backend, shared packages.
- Governance files: README, LICENSE, CHANGELOG, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY.
- GitHub Actions CI for all three language pipelines (JS, Python, Flutter).
- Backend health endpoint (`GET /healthz`) and pydantic-settings configuration module.
- Shared packages `@annex/shared-utils`, `@annex/shared-models`, `@annex/shared-ui` with unit tests.
- Backend core hardening: structlog structured logging (JSON/console), typed `AppError` hierarchy with
  sanitized 500s and a stable error envelope, request-ID correlation middleware, security hardening
  headers (CSP, nosniff, frame denial), and in-memory sliding-window rate limiting (429 + Retry-After).
- Strict type checking (`mypy --strict`) wired into CI for the backend.


### `CHANGELOG.md` (root)
**Purpose:** Records Phase 3.
```markdown
# Changelog

All notable changes to ANNEX are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

## [Unreleased]

### Added
- (Phase 1 & 2 entries unchanged — see previous commits)
- Backend data layer: SQLAlchemy 2.0 typed models (users, analyses, collections,
  collection_items, alerts, notifications) with Alembic migrations that run on
  local Postgres and hosted Supabase alike.
- Supabase Storage integration behind an injectable MediaStorage protocol.
- Redis client and Celery application with a ping task; Docker Compose stack
  (postgres, redis, api, worker) for local development and CI parity.
- Database integration tests guarded by TEST_DATABASE_URL; Postgres service
  added to the backend CI pipeline.

  
### 13. `/annex/CHANGELOG.md`
**Purpose:** Records Phase 4.
```markdown
# Changelog

All notable changes to ANNEX are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

## [Unreleased]

### Added
- (Phases 1–3 entries unchanged — see previous commits)
- Firebase Authentication integration: lazy Admin SDK initialization,
  ID-token verification via public keys, and an injectable `IdTokenVerifier`.
- `AuthService` with race-safe user upsert (by `firebase_uid`, email link,
  or creation) and `get_current_user` dependency.
- `users.firebase_uid` unique column (migration 0002) and authenticated
  profile endpoint `GET /api/v1/users/me`.
- Security test suite using test doubles + dependency overrides (no live
  Firebase required in CI).



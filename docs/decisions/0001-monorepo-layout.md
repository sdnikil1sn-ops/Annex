
**`/annex/docs/decisions/0001-monorepo-layout.md`** — ADR #1, recorded decision.
```markdown
# ADR 0001: Polyglot monorepo layout

- **Status:** Accepted
- **Date:** Phase 1
- **Deciders:** Architecture group

## Context
ANNEX ships a Flutter app, a React web app, a browser extension, and a FastAPI backend,
plus shared TS packages. We need one history, atomic cross-app changes, and shared CI —
without forcing a single build system on three languages.

## Decision
Use a **monorepo** with **language-native tooling per subproject**:
- `pnpm` workspaces for all TypeScript/JavaScript (`apps/web`, `apps/extension`, `packages/*`).
- `uv` + `pyproject.toml` for Python (`apps/backend`).
- Flutter tooling standalone for `apps/mobile`.
- A root `Makefile` + GitHub Actions orchestrate cross-language workflows.
- **No** Turborepo/Nx/Bazel: the added orchestration cost exceeds the benefit here.

## Consequences
+ Atomic cross-app changes, shared CI, one set of governance docs.
+ Each language uses best-in-class tooling.
− Developers must know three toolchains (mitigated by `Makefile` and `scripts/bootstrap.sh`).
− Releases per package require release-please monorepo config (added this phase).

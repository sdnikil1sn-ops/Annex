# Contributing to ANNEX

Thanks for contributing! ANNEX is built like a real product: clean architecture,
SOLID, DRY, KISS, and no placeholders.

## Development setup

1. Install prerequisites: Flutter (stable), Node.js 24 LTS, pnpm, uv, Docker.
2. Clone the repo and run `./scripts/bootstrap.sh`.
3. Run the full local checks: `make lint && make test`.

## Conventions

- **Commits:** Conventional Commits — `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`, `ci:`.
  Breaking changes: `feat!:`. Semver is derived from commit history by release-please.
- **Branches:** feature branches off `main`, PRs into `main`, trunk-based.
- **Style:** lint + format must pass in CI (`ruff` for Python, `dart format`/`flutter analyze` for Flutter,
  ESLint/Prettier for TS).
- **Tests:** every change ships with tests. No `TODO`, no placeholder code, no dead code.
- **Docs:** public APIs must have doc comments; architecture changes need an ADR in `docs/decisions/`.

## Pull request checklist

- [ ] Branch is up to date with `main`
- [ ] `make lint && make test` passes locally
- [ ] Tests cover the change
- [ ] CHANGELOG entry added (or release-please will generate from commits)
- [ ] No secrets, no `.env`, no build artifacts committed

## Code of conduct

All participation is governed by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

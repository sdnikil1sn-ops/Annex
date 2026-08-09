# ANNEX

> **Learn Before You Believe.**

ANNEX is an open-source, AI-powered **Media & Information Literacy platform**.
It helps people verify media claims — images, video, text, and documents — through
transparent, explainable analysis. This is a production-grade, modular, multilingual,
security-conscious codebase built like a real company product, not a prototype.

## Mission

Build the world's most advanced AI-powered Media & Information Literacy platform —
trustworthy by design, open by default.

## Repository layout

| Path | Description |
|---|---|
| `apps/mobile` | Flutter app (Android, iOS, Web, Linux, macOS, Windows) |
| `apps/web` | React + TypeScript web application |
| `apps/extension` | React + TypeScript browser extension |
| `apps/backend` | FastAPI service (Python) |
| `packages/shared_models` | Shared domain contracts (TS) |
| `packages/shared_ui` | Shared React UI primitives |
| `packages/shared_utils` | Framework-agnostic utilities (TS) |
| `docs` | Architecture, ADRs, runbooks, guides |
| `scripts` | Developer automation |
| `.github` | CI/CD and community templates |

## Tech stack

Flutter · React · TypeScript · FastAPI · Supabase (Postgres + Storage) ·
Firebase Auth · OpenAI/Gemini · Tesseract OCR · OpenCV · Redis · Celery ·
Docker · GitHub Actions · Cloud Run · Firebase Hosting

## Quick start

```bash
./scripts/bootstrap.sh          # installs every workspace's dependencies
make backend-run                # FastAPI on http://localhost:8000/docs
make web-dev                    # web app on http://localhost:5173
make mobile-run                 # Flutter app (device/emulator)

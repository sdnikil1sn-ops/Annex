#!/usr/bin/env bash
# bootstrap.sh — installs all dependencies for every ANNEX workspace.
# Usage: ./scripts/bootstrap.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> [1/3] Installing JS/TS workspace dependencies (pnpm)"
pnpm install

echo "==> [2/3] Installing backend dependencies (uv)"
cd apps/backend
uv sync
cd "$ROOT"

echo "==> [3/3] Installing Flutter dependencies"
cd apps/mobile
flutter pub get
cd "$ROOT"

echo "==> Done. Copy apps/backend/.env.example -> apps/backend/.env if needed."

.PHONY: setup lint test backend-run web-dev mobile-run docker-up clean

setup:
	./scripts/bootstrap.sh

lint:
	cd apps/backend && uv run ruff check .
	pnpm -r lint
	cd apps/mobile && flutter analyze

test:
	cd apps/backend && uv run pytest
	pnpm --filter './packages/*' test
	cd apps/mobile && flutter test

build:
	cd apps/backend && uv build
	pnpm -r build
	cd apps/mobile && flutter build web --release

backend-run:
	cd apps/backend && uv run uvicorn app.main:app --reload --port 8000

web-dev:
	pnpm --filter @annex/web dev

mobile-run:
	cd apps/mobile && flutter run

docker-up:
	docker compose up --build

clean:
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
	rm -rf node_modules apps/*/node_modules packages/*/node_modules apps/backend/.venv

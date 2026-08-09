"""Health-check task for verifying worker connectivity."""

from app.infra.celery_app import celery_app


@celery_app.task(name="app.tasks.ping")  # type: ignore[untyped-decorator]
def ping() -> str:
    """Return a pong payload proving the worker is alive."""
    return "pong"

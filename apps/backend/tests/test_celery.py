"""Celery task tests (eager execution, no broker needed)."""

from app.tasks.ping import ping


def test_ping_task_returns_pong() -> None:
    """The ping task must return 'pong' when executed eagerly."""
    result = ping.apply()
    assert result.get() == "pong"

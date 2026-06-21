from fastapi.testclient import TestClient

from service.app import app


def test_health_and_stats_endpoints() -> None:
    client = TestClient(app)

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    stats = client.get("/stats")
    assert stats.status_code == 200
    assert "runs" in stats.json()

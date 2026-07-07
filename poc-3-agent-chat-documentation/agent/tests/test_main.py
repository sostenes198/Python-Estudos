from fastapi.testclient import TestClient


def test_health_endpoint():
    from agent.main import app

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_all_webhook_routes_are_registered():
    from agent.main import app

    paths = set()
    for route in app.routes:
        if hasattr(route, "path"):
            paths.add(route.path)
        elif hasattr(route, "original_router"):
            for sub_route in route.original_router.routes:
                if hasattr(sub_route, "path"):
                    paths.add(sub_route.path)

    assert "/webhooks/outline" in paths
    assert "/webhooks/slack/events" in paths
    assert "/webhooks/slack/commands" in paths

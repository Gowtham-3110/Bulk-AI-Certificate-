from fastapi import status


def test_health_check(client):
    """Test health check endpoint."""
    resp = client.get("/health")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["status"] == "healthy"


def test_dashboard_ui_renders(client):
    """Test dashboard frontend template rendering."""
    resp = client.get("/")
    assert resp.status_code == status.HTTP_200_OK
    assert "CertifyFast" in resp.text
    assert "Bulk Generator API" in resp.text

from fastapi import status
from app.models import Job, JobStatus, Certificate, CertificateStatus


def test_create_generation_job_success(client):
    """Test creating a bulk job with valid payload."""
    payload = {
        "event_name": "Full Stack Cloud Architecture",
        "issuer_name": "Cloud Computing Council",
        "issue_date": "2026-10-08",
        "template_title": "Certificate of Completion",
        "recipients": [
            {"name": "Alice Cooper", "email": "alice@example.com", "attributes": {"grade": "A"}},
            {"name": "Bob Dylan", "email": "bob@example.com", "attributes": {"grade": "A+"}}
        ]
    }
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert "id" in data
    assert data["event_name"] == "Full Stack Cloud Architecture"
    assert data["total_recipients"] == 2
    assert len(data["certificates"]) == 2
    assert data["certificates"][0]["recipient_name"] == "Alice Cooper"
    assert data["certificates"][0]["certificate_code"].startswith("CERT-")


def test_create_job_validation_empty_recipients(client):
    """Test submitting a job with empty recipients list."""
    payload = {
        "event_name": "AI Workshop",
        "recipients": []
    }
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_job_validation_invalid_email(client):
    """Test submitting recipient with invalid email syntax."""
    payload = {
        "event_name": "AI Workshop",
        "recipients": [
            {"name": "John Doe", "email": "invalid-email-format"}
        ]
    }
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_job_validation_blank_name(client):
    """Test submitting recipient with blank or empty name."""
    payload = {
        "event_name": "AI Workshop",
        "recipients": [
            {"name": "   ", "email": "john@example.com"}
        ]
    }
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_job_validation_blank_event(client):
    """Test submitting job with blank event name."""
    payload = {
        "event_name": "   ",
        "recipients": [
            {"name": "John Doe", "email": "john@example.com"}
        ]
    }
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_job_status_and_progress(client):
    """Test tracking job status and progress through API."""
    payload = {
        "event_name": "Quantum Computing 101",
        "recipients": [
            {"name": "Eva Green", "email": "eva@example.com"}
        ]
    }
    create_resp = client.post("/api/v1/jobs", json=payload)
    job_id = create_resp.json()["id"]

    # Background task finishes when TestClient completes request
    get_resp_after = client.get(f"/api/v1/jobs/{job_id}")
    data = get_resp_after.json()
    assert data["status"] == "COMPLETED"
    assert data["processed_count"] == 1
    assert data["successful_count"] == 1
    assert data["failed_count"] == 0
    assert data["progress_percentage"] == 100.0
    assert data["certificates"][0]["status"] == "SUCCESS"
    assert data["certificates"][0]["download_url"] is not None


def test_list_jobs(client):
    """Test listing jobs with pagination."""
    for i in range(2):
        client.post("/api/v1/jobs", json={
            "event_name": f"Event {i}",
            "recipients": [{"name": f"User {i}", "email": f"user{i}@example.com"}]
        })

    resp = client.get("/api/v1/jobs?limit=10&offset=0")
    assert resp.status_code == status.HTTP_200_OK
    jobs = resp.json()
    assert len(jobs) == 2


def test_job_not_found(client):
    """Test requesting non-existent job ID returns 404."""
    resp = client.get("/api/v1/jobs/non-existent-uuid")
    assert resp.status_code == status.HTTP_404_NOT_FOUND

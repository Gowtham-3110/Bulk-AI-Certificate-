from fastapi import status


def test_individual_certificate_failure_isolation(client):
    """Critical requirement: A failure while generating one certificate

    should not prevent other valid certificates in the same job from being generated.
    The job status must indicate PARTIALLY_COMPLETED with specific failure reasons.
    """
    payload = {
        "event_name": "Robust Systems Engineering",
        "issuer_name": "Reliability Institute",
        "issue_date": "2026-10-08",
        "recipients": [
            {
                "name": "Sarah Connor",
                "email": "sarah@resistance.org",
                "attributes": {"rank": "Commander"}
            },
            {
                # Trigger simulated failure on this individual recipient
                "name": "__FAIL__ Broken Hardware Recipient",
                "email": "broken@domain.com",
                "attributes": {"simulate_error": True, "simulate_error_message": "Renderer GPU timeout"}
            },
            {
                "name": "John Connor",
                "email": "john@resistance.org",
                "attributes": {"rank": "Leader"}
            }
        ]
    }

    # 1. Create job (TestClient automatically runs background task)
    create_resp = client.post("/api/v1/jobs", json=payload)
    assert create_resp.status_code == status.HTTP_201_CREATED
    job_id = create_resp.json()["id"]

    # 2. Query job status
    status_resp = client.get(f"/api/v1/jobs/{job_id}")
    assert status_resp.status_code == status.HTTP_200_OK
    data = status_resp.json()

    # Verify overall job status is PARTIALLY_COMPLETED
    assert data["status"] == "PARTIALLY_COMPLETED"
    assert data["total_recipients"] == 3
    assert data["processed_count"] == 3
    assert data["successful_count"] == 2
    assert data["failed_count"] == 1
    assert data["progress_percentage"] == 100.0

    # Verify individual certificate statuses
    certs = {c["recipient_name"]: c for c in data["certificates"]}

    # Sarah Connor: SUCCESS
    assert certs["Sarah Connor"]["status"] == "SUCCESS"
    assert certs["Sarah Connor"]["error_message"] is None
    assert certs["Sarah Connor"]["download_url"] is not None

    # John Connor: SUCCESS
    assert certs["John Connor"]["status"] == "SUCCESS"
    assert certs["John Connor"]["error_message"] is None
    assert certs["John Connor"]["download_url"] is not None

    # Failing recipient: FAILED with error message
    failing_cert = certs["__FAIL__ Broken Hardware Recipient"]
    assert failing_cert["status"] == "FAILED"
    assert failing_cert["download_url"] is None
    assert failing_cert["error_message"] is not None
    assert "Simulated" in failing_cert["error_message"] or "Renderer" in failing_cert["error_message"]


def test_all_certificates_failing_sets_job_to_failed(client):
    """Test that when every certificate in a job fails, the job status is FAILED."""
    payload = {
        "event_name": "Failure Test Workshop",
        "recipients": [
            {
                "name": "__FAIL__ User One",
                "email": "one@example.com"
            },
            {
                "name": "__FAIL__ User Two",
                "email": "two@example.com"
            }
        ]
    }

    create_resp = client.post("/api/v1/jobs", json=payload)
    assert create_resp.status_code == status.HTTP_201_CREATED
    job_id = create_resp.json()["id"]

    status_resp = client.get(f"/api/v1/jobs/{job_id}")
    data = status_resp.json()
    assert data["status"] == "FAILED"
    assert data["successful_count"] == 0
    assert data["failed_count"] == 2

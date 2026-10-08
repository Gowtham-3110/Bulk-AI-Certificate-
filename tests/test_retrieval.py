import io
import uuid
import zipfile
from fastapi import status
from app.models import Certificate, CertificateStatus, Job, JobStatus


def test_download_individual_certificate_pdf(client):
    """Test retrieving an individual generated PDF certificate."""
    payload = {
        "event_name": "Cybersecurity Operations",
        "recipients": [
            {"name": "Ada Lovelace", "email": "ada@analytics.org"}
        ]
    }
    create_resp = client.post("/api/v1/jobs", json=payload)
    job_id = create_resp.json()["id"]

    # Get certificate ID
    status_resp = client.get(f"/api/v1/jobs/{job_id}")
    cert_id = status_resp.json()["certificates"][0]["id"]

    # Download PDF
    download_resp = client.get(f"/api/v1/certificates/{cert_id}/download")
    assert download_resp.status_code == status.HTTP_200_OK
    assert download_resp.headers["content-type"] == "application/pdf"
    assert "attachment" in download_resp.headers.get("content-disposition", "") or "filename" in download_resp.headers.get("content-disposition", "")
    assert download_resp.content.startswith(b"%PDF-")


def test_download_all_certificates_as_zip(client):
    """Test retrieving all generated certificates as a compressed ZIP file."""
    payload = {
        "event_name": "Distributed Systems",
        "recipients": [
            {"name": "Leslie Lamport", "email": "leslie@paxos.org"},
            {"name": "Barbara Liskov", "email": "barbara@mit.edu"}
        ]
    }
    create_resp = client.post("/api/v1/jobs", json=payload)
    job_id = create_resp.json()["id"]

    # Download ZIP
    zip_resp = client.get(f"/api/v1/jobs/{job_id}/download-all")
    assert zip_resp.status_code == status.HTTP_200_OK
    assert zip_resp.headers["content-type"] == "application/zip"

    # Open and verify ZIP content in memory
    zip_bytes = io.BytesIO(zip_resp.content)
    with zipfile.ZipFile(zip_bytes, "r") as zf:
        namelist = zf.namelist()
        assert len(namelist) == 2
        # Check that files in zip end in .pdf and contain recipient names
        assert any("Leslie" in name for name in namelist)
        assert any("Barbara" in name for name in namelist)
        for filename in namelist:
            file_data = zf.read(filename)
            assert file_data.startswith(b"%PDF-")


def test_download_certificate_not_yet_generated_or_failed(client):
    """Test that attempting to download a failed certificate returns 400."""
    payload = {
        "event_name": "Pending Job",
        "recipients": [
            {"name": "__FAIL__ Broken User", "email": "pending@example.com"}
        ]
    }
    create_resp = client.post("/api/v1/jobs", json=payload)
    cert_id = create_resp.json()["certificates"][0]["id"]

    download_resp = client.get(f"/api/v1/certificates/{cert_id}/download")
    assert download_resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Certificate has not been generated yet" in download_resp.json()["detail"]


def test_download_nonexistent_certificate_404(client):
    """Test that downloading a non-existent certificate returns 404."""
    resp = client.get("/api/v1/certificates/random-non-existent-uuid/download")
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_verify_certificate_endpoint(client):
    """Test public certificate authenticity verification."""
    payload = {
        "event_name": "Ethical Hacking",
        "recipients": [
            {"name": "Linus Torvalds", "email": "linus@kernel.org"}
        ]
    }
    create_resp = client.post("/api/v1/jobs", json=payload)
    job_id = create_resp.json()["id"]

    status_resp = client.get(f"/api/v1/jobs/{job_id}")
    cert_code = status_resp.json()["certificates"][0]["certificate_code"]

    # Verify valid certificate
    verify_resp = client.get(f"/api/v1/certificates/verify/{cert_code}")
    assert verify_resp.status_code == status.HTTP_200_OK
    verify_data = verify_resp.json()
    assert verify_data["is_valid"] is True
    assert verify_data["recipient_name"] == "Linus Torvalds"
    assert verify_data["event_name"] == "Ethical Hacking"

    # Verify invalid certificate
    invalid_resp = client.get("/api/v1/certificates/verify/FAKE-CODE-999")
    assert invalid_resp.status_code == status.HTTP_200_OK
    assert invalid_resp.json()["is_valid"] is False

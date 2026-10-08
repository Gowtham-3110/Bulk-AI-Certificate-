from pathlib import Path
from app.services.generator import CertificateGenerator


def test_certificate_generator_creates_valid_pdf(tmp_path):
    """Test that CertificateGenerator renders a valid, non-empty PDF file."""
    output_pdf = tmp_path / "test_certificate.pdf"

    result_path = CertificateGenerator.generate_pdf(
        output_path=output_pdf,
        recipient_name="Grace Hopper",
        event_name="Compiler Architecture Masterclass",
        issuer_name="ACM Distinguished Series",
        issue_date="2026-10-08",
        certificate_code="CERT-202610-GRACE001",
        template_title="Certificate of Distinction",
        custom_attributes={"Honor": "Pioneer", "Score": "100%"},
    )

    assert result_path.exists()
    assert result_path.is_file()

    file_bytes = result_path.read_bytes()
    # Check PDF magic bytes header
    assert file_bytes.startswith(b"%PDF-")
    # File size should be reasonable (> 1.5 KB)
    assert len(file_bytes) > 1500

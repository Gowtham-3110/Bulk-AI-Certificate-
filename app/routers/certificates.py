from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Certificate, CertificateStatus
from app.schemas import CertificateResponse, CertificateVerificationResponse

router = APIRouter(prefix="/api/v1/certificates", tags=["Certificates"])


def _format_certificate_response(cert: Certificate) -> CertificateResponse:
    download_url = f"/api/v1/certificates/{cert.id}/download" if cert.status == CertificateStatus.SUCCESS else None
    return CertificateResponse(
        id=cert.id,
        job_id=cert.job_id,
        recipient_name=cert.recipient_name,
        recipient_email=cert.recipient_email,
        certificate_code=cert.certificate_code,
        custom_attributes=cert.custom_attributes,
        status=cert.status,
        error_message=cert.error_message,
        download_url=download_url,
        created_at=cert.created_at,
        generated_at=cert.generated_at,
    )


@router.get(
    "/{certificate_id}",
    response_model=CertificateResponse,
    summary="Get Certificate Metadata",
    description="Retrieve details and status for a single certificate by its UUID.",
)
def get_certificate_metadata(
    certificate_id: str,
    db: Session = Depends(get_db),
):
    cert = db.query(Certificate).filter(Certificate.id == certificate_id).first()
    if not cert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Certificate with ID '{certificate_id}' not found.",
        )
    return _format_certificate_response(cert)


@router.get(
    "/{certificate_id}/download",
    summary="Download Individual Certificate PDF",
    description="Download the generated PDF for an individual certificate.",
)
def download_certificate_pdf(
    certificate_id: str,
    db: Session = Depends(get_db),
):
    cert = db.query(Certificate).filter(Certificate.id == certificate_id).first()
    if not cert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Certificate with ID '{certificate_id}' not found.",
        )

    if cert.status != CertificateStatus.SUCCESS or not cert.file_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Certificate has not been generated yet. Current status: {cert.status}. Error: {cert.error_message or 'None'}",
        )

    file_path = Path(cert.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated certificate file was not found on server storage.",
        )

    safe_name = "".join(c for c in cert.recipient_name if c.isalnum() or c in (" ", "-", "_")).strip().replace(" ", "_")
    filename = f"{safe_name}_{cert.certificate_code}.pdf"

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=filename,
    )


@router.get(
    "/verify/{certificate_code}",
    response_model=CertificateVerificationResponse,
    summary="Verify Certificate Authenticity",
    description="Public endpoint to verify the authenticity of a certificate using its verification code.",
)
def verify_certificate(
    certificate_code: str,
    db: Session = Depends(get_db),
):
    cert = db.query(Certificate).filter(Certificate.certificate_code == certificate_code).first()
    if not cert or cert.status != CertificateStatus.SUCCESS:
        return CertificateVerificationResponse(
            is_valid=False,
            certificate_code=certificate_code,
            message="Certificate code is invalid, unverified, or generation failed.",
        )

    job = cert.job
    return CertificateVerificationResponse(
        is_valid=True,
        certificate_code=cert.certificate_code,
        recipient_name=cert.recipient_name,
        event_name=job.event_name if job else "N/A",
        issuer_name=job.issuer_name if job else "N/A",
        issue_date=job.issue_date if job else "N/A",
        generated_at=cert.generated_at,
        message="Certificate is authentic and officially recognized.",
    )

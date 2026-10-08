import io
import uuid
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.config import DEFAULT_ISSUER
from app.database import get_db
from app.models import Job, Certificate, JobStatus, CertificateStatus
from app.schemas import (
    CreateJobRequest,
    JobSummaryResponse,
    JobDetailResponse,
    CertificateResponse,
)
from app.services.job_processor import process_certificate_job

router = APIRouter(prefix="/api/v1/jobs", tags=["Jobs"])


def _format_certificate_response(cert: Certificate) -> CertificateResponse:
    download_url = f"/api/v1/certificates/{cert.id}/download" if cert.status == CertificateStatus.SUCCESS else None
    preview_url = f"/api/v1/certificates/{cert.id}/preview" if cert.status == CertificateStatus.SUCCESS else None
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
        preview_url=preview_url,
        created_at=cert.created_at,
        generated_at=cert.generated_at,
    )


def _format_job_detail_response(job: Job) -> JobDetailResponse:
    certs_data = [_format_certificate_response(c) for c in job.certificates]
    download_all_url = f"/api/v1/jobs/{job.id}/download-all" if job.successful_count > 0 else None
    return JobDetailResponse(
        id=job.id,
        event_name=job.event_name,
        issuer_name=job.issuer_name,
        issue_date=job.issue_date,
        template_title=job.template_title,
        status=job.status,
        total_recipients=job.total_recipients,
        processed_count=job.processed_count,
        successful_count=job.successful_count,
        failed_count=job.failed_count,
        progress_percentage=job.progress_percentage,
        created_at=job.created_at,
        updated_at=job.updated_at,
        download_all_url=download_all_url,
        certificates=certs_data,
    )


def _format_job_summary_response(job: Job) -> JobSummaryResponse:
    download_all_url = f"/api/v1/jobs/{job.id}/download-all" if job.successful_count > 0 else None
    return JobSummaryResponse(
        id=job.id,
        event_name=job.event_name,
        issuer_name=job.issuer_name,
        issue_date=job.issue_date,
        template_title=job.template_title,
        status=job.status,
        total_recipients=job.total_recipients,
        processed_count=job.processed_count,
        successful_count=job.successful_count,
        failed_count=job.failed_count,
        progress_percentage=job.progress_percentage,
        created_at=job.created_at,
        updated_at=job.updated_at,
        download_all_url=download_all_url,
    )


@router.post(
    "",
    response_model=JobDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Bulk Certificate Generation Job",
    description="Submits a list of recipients and enqueues a background generation task.",
)
def create_generation_job(
    payload: CreateJobRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    if not payload.recipients:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one recipient must be provided.",
        )

    job_id = str(uuid.uuid4())
    issue_date = payload.issue_date or datetime.utcnow().strftime("%Y-%m-%d")
    issuer_name = (payload.issuer_name or "").strip() or DEFAULT_ISSUER
    template_title = (payload.template_title or "").strip() or "Certificate of Completion"

    new_job = Job(
        id=job_id,
        event_name=payload.event_name.strip(),
        issuer_name=issuer_name,
        issue_date=issue_date,
        template_title=template_title,
        status=JobStatus.PENDING,
        total_recipients=len(payload.recipients),
        processed_count=0,
        successful_count=0,
        failed_count=0,
    )
    db.add(new_job)

    # Pre-register certificate records
    for idx, r in enumerate(payload.recipients, start=1):
        cert_code = f"CERT-{datetime.utcnow().strftime('%Y%m')}-{uuid.uuid4().hex[:8].upper()}"
        cert = Certificate(
            id=str(uuid.uuid4()),
            job_id=job_id,
            recipient_name=r.name,
            recipient_email=r.email,
            certificate_code=cert_code,
            custom_attributes=r.attributes or {},
            status=CertificateStatus.PENDING,
        )
        db.add(cert)

    db.commit()
    db.refresh(new_job)

    # Enqueue background task
    background_tasks.add_task(process_certificate_job, new_job.id)

    return _format_job_detail_response(new_job)


@router.get(
    "",
    response_model=List[JobSummaryResponse],
    summary="List Certificate Jobs",
    description="Returns a paginated list of certificate generation jobs ordered by creation date descending.",
)
def list_jobs(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    jobs = db.query(Job).order_by(Job.created_at.desc()).offset(offset).limit(limit).all()
    return [_format_job_summary_response(j) for j in jobs]


@router.get(
    "/{job_id}",
    response_model=JobDetailResponse,
    summary="Get Job Status and Details",
    description="Check the current progress, status, and individual recipient certificate results for a job.",
)
def get_job_status(
    job_id: str,
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{job_id}' not found.",
        )
    return _format_job_detail_response(job)


@router.get(
    "/{job_id}/download-all",
    summary="Download All Generated Certificates as ZIP",
    description="Downloads a ZIP archive containing all successfully generated certificates for this job.",
)
def download_all_certificates(
    job_id: str,
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{job_id}' not found.",
        )

    successful_certs = [c for c in job.certificates if c.status == CertificateStatus.SUCCESS and c.file_path]
    if not successful_certs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No certificates have been successfully generated for this job yet.",
        )

    # Build ZIP archive in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for cert in successful_certs:
            pdf_path = Path(cert.file_path)
            if pdf_path.exists():
                # Clean recipient name for filename
                safe_name = "".join(c for c in cert.recipient_name if c.isalnum() or c in (" ", "-", "_")).strip()
                arcname = f"{safe_name}_{cert.certificate_code}.pdf"
                zf.write(pdf_path, arcname=arcname)

    zip_buffer.seek(0)
    safe_event = "".join(c for c in job.event_name if c.isalnum() or c in (" ", "-", "_")).strip().replace(" ", "_")
    zip_filename = f"{safe_event}_certificates_{job_id[:8]}.zip"

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{zip_filename}"'},
    )

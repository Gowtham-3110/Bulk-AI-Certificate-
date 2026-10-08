import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from app.config import STORAGE_DIR
import app.database as database
from app.models import Job, Certificate, JobStatus, CertificateStatus
from app.services.generator import CertificateGenerator

logger = logging.getLogger(__name__)


def validate_recipient_data(cert: Certificate) -> Optional[str]:
    """Validates individual recipient data before generation.

    Returns an error message string if invalid, or None if valid.
    """
    if not cert.recipient_name or not cert.recipient_name.strip():
        return "Recipient name is missing or blank."

    # Validate name does not contain illegal control characters
    if re.search(r"[\x00-\x1f\x7f]", cert.recipient_name):
        return "Recipient name contains invalid control characters."

    if not cert.recipient_email or "@" not in cert.recipient_email:
        return "Recipient email is missing or improperly formatted."

    # Allow testing of simulated generator failures via custom attributes or special prefix
    if cert.custom_attributes and cert.custom_attributes.get("simulate_error"):
        return cert.custom_attributes.get("simulate_error_message", "Simulated certificate generation failure.")

    if cert.recipient_name.startswith("__FAIL__"):
        return "Simulated runtime failure triggered by recipient name test prefix."

    return None


def process_certificate_job(job_id: str, db: Optional[Session] = None) -> None:
    """Processes all certificates for a given job in the background.

    Updates progress incrementally so status polls reflect real-time progress.
    Handles individual certificate failures gracefully without interrupting the rest of the job.
    """
    should_close = False
    if db is None:
        db = database.SessionLocal()
        should_close = True

    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found for background processing.")
            return

        job.status = JobStatus.PROCESSING
        job.updated_at = datetime.utcnow()
        db.commit()

        job_dir = STORAGE_DIR / job.id
        job_dir.mkdir(parents=True, exist_ok=True)

        for cert in job.certificates:
            # Skip if already in terminal status (idempotence)
            if cert.status in (CertificateStatus.SUCCESS, CertificateStatus.FAILED):
                continue

            try:
                # 1. Recipient-level validation
                validation_err = validate_recipient_data(cert)
                if validation_err:
                    cert.status = CertificateStatus.FAILED
                    cert.error_message = validation_err
                    job.failed_count += 1
                    job.processed_count += 1
                    db.commit()
                    continue

                # 2. Render Certificate PDF
                pdf_filename = f"{cert.certificate_code}.pdf"
                pdf_path = job_dir / pdf_filename

                CertificateGenerator.generate_pdf(
                    output_path=pdf_path,
                    recipient_name=cert.recipient_name,
                    event_name=job.event_name,
                    issuer_name=job.issuer_name,
                    issue_date=job.issue_date,
                    certificate_code=cert.certificate_code,
                    template_title=job.template_title,
                    custom_attributes=cert.custom_attributes,
                )

                # 3. Mark success
                cert.status = CertificateStatus.SUCCESS
                cert.file_path = str(pdf_path)
                cert.generated_at = datetime.utcnow()
                cert.error_message = None
                job.successful_count += 1

            except Exception as ex:
                logger.exception(f"Unexpected error generating certificate {cert.id}: {ex}")
                cert.status = CertificateStatus.FAILED
                cert.error_message = f"Certificate generation failed: {str(ex)}"
                job.failed_count += 1

            finally:
                job.processed_count = job.successful_count + job.failed_count
                job.updated_at = datetime.utcnow()
                db.commit()

        # 4. Finalize overall job status
        if job.successful_count == job.total_recipients:
            job.status = JobStatus.COMPLETED
        elif job.successful_count > 0 and job.failed_count > 0:
            job.status = JobStatus.PARTIALLY_COMPLETED
        else:
            job.status = JobStatus.FAILED

        job.updated_at = datetime.utcnow()
        db.commit()
        logger.info(f"Job {job_id} completed with status {job.status}. "
                    f"Success: {job.successful_count}/{job.total_recipients}, "
                    f"Failed: {job.failed_count}/{job.total_recipients}")

    except Exception as ex:
        logger.exception(f"Fatal error in job processor for job {job_id}: {ex}")
        if job:
            job.status = JobStatus.FAILED
            job.updated_at = datetime.utcnow()
            db.commit()
    finally:
        if should_close:
            db.close()

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr, field_validator
from app.models import JobStatus, CertificateStatus


class RecipientInput(BaseModel):
    name: str = Field(..., description="Recipient full name")
    email: EmailStr = Field(..., description="Recipient valid email address")
    attributes: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Optional custom metadata (e.g. grade, honors, role)",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        clean_name = v.strip()
        if not clean_name:
            raise ValueError("Recipient name cannot be empty or blank")
        if len(clean_name) > 100:
            raise ValueError("Recipient name must be 100 characters or fewer")
        return clean_name


class CreateJobRequest(BaseModel):
    event_name: str = Field(..., description="Course, workshop, or event title")
    issuer_name: Optional[str] = Field(
        default=None,
        description="Organization or issuer name (defaults to system setting if omitted)",
    )
    issue_date: Optional[str] = Field(
        default=None,
        description="Date of issuance formatted as YYYY-MM-DD or readable text (defaults to current date)",
    )
    template_title: Optional[str] = Field(
        default="Certificate of Completion",
        description="Heading of certificate (e.g. Certificate of Achievement / Completion / Excellence)",
    )
    recipients: List[RecipientInput] = Field(
        ...,
        min_length=1,
        description="List of recipients to generate certificates for (must contain at least 1 recipient)",
    )

    @field_validator("event_name")
    @classmethod
    def validate_event(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Event name cannot be empty")
        return clean


class CertificateResponse(BaseModel):
    id: str
    job_id: str
    recipient_name: str
    recipient_email: str
    certificate_code: str
    custom_attributes: Optional[Dict[str, Any]] = None
    status: CertificateStatus
    error_message: Optional[str] = None
    download_url: Optional[str] = None
    created_at: datetime
    generated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobSummaryResponse(BaseModel):
    id: str
    event_name: str
    issuer_name: str
    issue_date: str
    template_title: str
    status: JobStatus
    total_recipients: int
    processed_count: int
    successful_count: int
    failed_count: int
    progress_percentage: float
    created_at: datetime
    updated_at: datetime
    download_all_url: Optional[str] = None

    class Config:
        from_attributes = True


class JobDetailResponse(JobSummaryResponse):
    certificates: List[CertificateResponse] = []


class CertificateVerificationResponse(BaseModel):
    is_valid: bool
    certificate_code: str
    recipient_name: Optional[str] = None
    event_name: Optional[str] = None
    issuer_name: Optional[str] = None
    issue_date: Optional[str] = None
    generated_at: Optional[datetime] = None
    message: str

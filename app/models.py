import enum
import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Enum,
    ForeignKey,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship
from app.database import Base


class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    PARTIALLY_COMPLETED = "PARTIALLY_COMPLETED"
    FAILED = "FAILED"


class CertificateStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    event_name = Column(String(255), nullable=False)
    issuer_name = Column(String(255), nullable=False)
    issue_date = Column(String(50), nullable=False)
    template_title = Column(String(255), nullable=False, default="Certificate of Completion")
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False, index=True)

    total_recipients = Column(Integer, default=0, nullable=False)
    processed_count = Column(Integer, default=0, nullable=False)
    successful_count = Column(Integer, default=0, nullable=False)
    failed_count = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    certificates = relationship("Certificate", back_populates="job", cascade="all, delete-orphan", lazy="joined")

    @property
    def progress_percentage(self) -> float:
        if self.total_recipients == 0:
            return 0.0
        return round((self.processed_count / self.total_recipients) * 100, 1)


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)

    recipient_name = Column(String(255), nullable=False)
    recipient_email = Column(String(255), nullable=False)
    certificate_code = Column(String(64), unique=True, nullable=False, index=True)

    custom_attributes = Column(JSON, nullable=True)

    status = Column(Enum(CertificateStatus), default=CertificateStatus.PENDING, nullable=False, index=True)
    file_path = Column(String(512), nullable=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    generated_at = Column(DateTime, nullable=True)

    job = relationship("Job", back_populates="certificates")

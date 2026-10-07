import uuid
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class CandidateLeadCreate(BaseModel):
    """
    Payload submitted by candidate seeking a referral or lead submission.
    """
    job_id: str = Field(..., description="ID of the target job posting")
    company: str = Field(..., description="Employer company name")
    role_title: str = Field(..., description="Target role title")
    candidate_name: str = Field(..., min_length=2, max_length=100, description="Candidate full name")
    email: EmailStr = Field(..., description="Candidate contact email")
    linkedin_url: Optional[str] = Field(None, description="Candidate LinkedIn profile URL")
    yoe: float = Field(..., ge=0, le=50, description="Total years of relevant experience")
    current_ctc_lpa: Optional[float] = Field(None, ge=0, description="Current annual CTC in Lakhs (INR)")
    expected_ctc_lpa: Optional[float] = Field(None, ge=0, description="Expected annual CTC in Lakhs (INR)")
    notice_period_days: int = Field(default=30, ge=0, le=180, description="Notice period in days")
    resume_url: Optional[str] = Field(None, description="Public cloud link to resume (Google Drive, Dropbox, Notion, etc.)")


class CandidateLead(CandidateLeadCreate):
    """
    Stored candidate lead record with system metadata.
    """
    id: str = Field(default_factory=lambda: f"lead_{uuid.uuid4().hex[:12]}")
    status: str = Field(default="new", description="Referral lead status: new, referred, reviewing, contacted")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def from_row(cls, row: dict) -> "CandidateLead":
        dt = row["created_at"]
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return cls(
            id=row["id"],
            job_id=row["job_id"],
            company=row["company"],
            role_title=row["role_title"],
            candidate_name=row["candidate_name"],
            email=row["email"],
            linkedin_url=row["linkedin_url"],
            yoe=float(row["yoe"]),
            current_ctc_lpa=float(row["current_ctc_lpa"]) if row["current_ctc_lpa"] is not None else None,
            expected_ctc_lpa=float(row["expected_ctc_lpa"]) if row["expected_ctc_lpa"] is not None else None,
            notice_period_days=int(row["notice_period_days"]),
            resume_url=row["resume_url"],
            status=row["status"],
            created_at=dt,
        )

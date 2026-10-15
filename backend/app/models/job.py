import hashlib
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field


class JobItem(BaseModel):
    """
    Normalized job listing model representing a verified job posting
    from any ATS feed or custom career portal.
    """
    id: str = Field(description="Deterministic unique identifier")
    title: str = Field(description="Official job role title")
    company: str = Field(description="Employer name")
    domain: str = Field(default="Tech", description="Industry domain or sector")
    category: str = Field(default="general", description="Canonical role category")
    track: Optional[str] = Field(default=None, description="Granular role track (e.g. Chief of Staff, APM, TPM, BizOps)")
    seniority: str = Field(default="mid", description="Inferred seniority level: entry, mid, senior, lead, intern")
    location: str = Field(default="Not Specified", description="Display location or workplace city/region")
    country: str = Field(default="Global", description="Country name or Global")
    is_remote: bool = Field(default=False, description="Flag indicating if the position is remote-eligible")
    date_posted: datetime = Field(description="Verified UTC posting or update timestamp")
    apply_url: str = Field(description="Direct URL to official career portal application form")
    source: str = Field(description="Source identifier (greenhouse, lever, ashby, custom)")
    description_summary: Optional[str] = Field(default=None, description="Concise overview or snippet of requirements")
    raw_tags: List[str] = Field(default_factory=list, description="Original tags, departments, or tech stack mentions")

    @staticmethod
    def generate_id(company: str, title: str, apply_url: str) -> str:
        """
        Creates a deterministic hash identifier for a job to prevent duplicate records.
        """
        raw = f"{company.strip().lower()}|{title.strip().lower()}|{apply_url.strip()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    @classmethod
    def create(
        cls,
        title: str,
        company: str,
        apply_url: str,
        date_posted: datetime,
        source: str,
        domain: str = "Tech",
        category: str = "general",
        track: Optional[str] = None,
        seniority: str = "mid",
        location: str = "Not Specified",
        country: str = "Global",
        is_remote: bool = False,
        description_summary: Optional[str] = None,
        raw_tags: Optional[List[str]] = None,
    ) -> "JobItem":
        # Ensure date_posted has a timezone (UTC)
        if date_posted.tzinfo is None:
            date_posted = date_posted.replace(tzinfo=timezone.utc)

        job_id = cls.generate_id(company=company, title=title, apply_url=apply_url)
        return cls(
            id=job_id,
            title=title.strip(),
            company=company.strip(),
            domain=domain.strip(),
            category=category.strip().lower(),
            track=track.strip() if track else None,
            seniority=seniority.strip().lower(),
            location=location.strip(),
            country=country.strip(),
            is_remote=is_remote,
            date_posted=date_posted,
            apply_url=apply_url.strip(),
            source=source.strip().lower(),
            description_summary=description_summary,
            raw_tags=raw_tags or [],
        )


class JobFilterParams(BaseModel):
    """
    Search and filter parameters for querying the normalized job database.
    """
    search: Optional[str] = None
    company: Optional[str] = None
    category: Optional[str] = None
    cluster: Optional[str] = Field(default=None, description="Parent domain cluster (e.g. 'product_cluster', 'strategy_cluster')")
    track: Optional[str] = Field(default=None, description="Granular role track (e.g. 'Chief of Staff', 'APM')")
    domain: Optional[str] = None
    country: Optional[str] = None
    location: Optional[str] = None
    metro_hub: Optional[str] = None
    seniority: Optional[str] = None
    is_remote: Optional[bool] = None
    posted_within_days: Optional[int] = None
    sort_by: str = Field(default="date", description="Sort order: 'date' (newest first), 'company', or 'title'")
    synonyms: Optional[List[str]] = Field(default=None, description="Optional category synonyms for semantic title matching")
    include_inactive: bool = Field(default=False, description="Whether to include soft-archived/closed postings")
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)

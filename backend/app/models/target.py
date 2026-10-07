import re
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class CareerTarget(BaseModel):
    """
    Monitored career target representing a company's career portal endpoint.
    """
    id: str = Field(description="Unique identifier for target")
    name: str = Field(description="Display company name")
    slug: str = Field(description="URL-safe unique company slug")
    website: Optional[str] = Field(default=None, description="Official company website")
    career_url: str = Field(description="Public career portal URL")
    ats_type: str = Field(description="ATS provider: greenhouse, lever, ashby, smartrecruiters, workday, custom")
    feed_url: Optional[str] = Field(default=None, description="Direct JSON or API endpoint if available")
    category_tier: str = Field(default="startup", description="Tier: startup, unicorn, enterprise, consulting, other")
    domain: str = Field(default="Tech", description="Industry domain or sector")
    role_focus: List[str] = Field(default_factory=list, description="Target role tags: product, strategy, tech, etc.")
    status: str = Field(default="active", description="Health status: active, syncing, error, paused")
    last_scraped_at: Optional[str] = Field(default=None, description="ISO timestamp of last scrape pass")
    last_status: Optional[str] = Field(default=None, description="Result of last scrape: ok, 404, rate_limited, failed")
    job_count: int = Field(default=0, description="Number of currently active jobs in repository")
    created_at: str = Field(description="ISO timestamp of target creation")

    @staticmethod
    def generate_slug(name: str) -> str:
        s = name.strip().lower()
        s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
        return s or "company"

    @classmethod
    def create(
        cls,
        name: str,
        career_url: str,
        ats_type: str,
        category_tier: str = "startup",
        domain: str = "Tech",
        website: Optional[str] = None,
        feed_url: Optional[str] = None,
        role_focus: Optional[List[str]] = None,
        slug: Optional[str] = None,
        status: str = "active",
        job_count: int = 0,
    ) -> "CareerTarget":
        now_iso = datetime.now(timezone.utc).isoformat()
        resolved_slug = slug or cls.generate_slug(name)
        target_id = f"target_{resolved_slug}"
        return cls(
            id=target_id,
            name=name.strip(),
            slug=resolved_slug,
            website=website,
            career_url=career_url.strip(),
            ats_type=ats_type.strip().lower(),
            feed_url=feed_url.strip() if feed_url else None,
            category_tier=category_tier.strip().lower(),
            domain=domain.strip(),
            role_focus=role_focus or ["tech"],
            status=status,
            last_scraped_at=None,
            last_status=None,
            job_count=job_count,
            created_at=now_iso,
        )


class CareerTargetFilterParams(BaseModel):
    category_tier: Optional[str] = None
    domain: Optional[str] = None
    role_tag: Optional[str] = None
    status: Optional[str] = None
    search: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class CareerTargetStats(BaseModel):
    total_targets: int
    active_targets: int
    by_tier: Dict[str, int]
    total_live_jobs: int

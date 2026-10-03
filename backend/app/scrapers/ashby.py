import logging
from typing import List
import httpx

from backend.app.models.job import JobItem
from backend.app.scrapers.base import BaseATSConnector, DEFAULT_HEADERS
from backend.app.utils.classifier import classify_role, parse_location
from backend.app.utils.date_parser import parse_posting_date

logger = logging.getLogger("careerloom.ashby")


class AshbyConnector(BaseATSConnector):
    """
    Ingests job listings from public Ashby posting API endpoints.
    Endpoint: https://api.ashbyhq.com/posting-api/job-board/{company_slug}
    """

    async def fetch_jobs(
        self,
        company_name: str,
        company_slug: str,
        domain: str = "Tech",
    ) -> List[JobItem]:
        url = f"https://api.ashbyhq.com/posting-api/job-board/{company_slug}"
        jobs: List[JobItem] = []

        try:
            async with httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=self.timeout) as client:
                response = await client.get(url)
                if response.status_code == 404:
                    logger.warning(f"Ashby board not found for slug '{company_slug}'")
                    return []
                response.raise_for_status()
                data = response.json()

            raw_jobs = data.get("jobs", [])
            for rj in raw_jobs:
                if not rj.get("isListed", True):
                    continue

                title = rj.get("title", "").strip()
                if not title:
                    continue

                apply_url = rj.get("applyUrl") or rj.get("jobUrl") or f"https://jobs.ashbyhq.com/{company_slug}/{rj.get('id')}"
                raw_location = rj.get("locationName") or rj.get("location") or ""
                raw_date = rj.get("publishedAt")

                date_posted = parse_posting_date(raw_date)
                category, seniority = classify_role(title)
                location, country, is_remote = parse_location(str(raw_location), title, company_hint=company_name)

                # Ashby explicitly provides isRemote boolean
                if rj.get("isRemote"):
                    is_remote = True

                # Tags / metadata
                raw_tags = []
                if rj.get("department"):
                    raw_tags.append(rj["department"])
                if rj.get("team"):
                    raw_tags.append(rj["team"])
                if rj.get("employmentType"):
                    raw_tags.append(rj["employmentType"])

                description = rj.get("descriptionPlain") or ""
                description_summary = description[:300] + "..." if len(description) > 300 else (description or None)

                job = JobItem.create(
                    title=title,
                    company=company_name,
                    apply_url=apply_url,
                    date_posted=date_posted,
                    source="ashby",
                    domain=domain,
                    category=category,
                    seniority=seniority,
                    location=location,
                    country=country,
                    is_remote=is_remote,
                    description_summary=description_summary,
                    raw_tags=raw_tags,
                )
                jobs.append(job)

            logger.info(f"Ashby: Fetched {len(jobs)} jobs for {company_name} ({company_slug})")
            return jobs

        except Exception as e:
            logger.error(f"Error fetching Ashby jobs for {company_name} ({company_slug}): {e}")
            return []

import logging
from typing import List
import httpx

from backend.app.models.job import JobItem
from backend.app.scrapers.base import BaseATSConnector, DEFAULT_HEADERS
from backend.app.utils.classifier import classify_role, parse_location
from backend.app.utils.date_parser import parse_posting_date

logger = logging.getLogger("careerloom.greenhouse")


class GreenhouseConnector(BaseATSConnector):
    """
    Ingests job listings from public Greenhouse boards API endpoints.
    Endpoint: https://boards-api.greenhouse.io/v1/boards/{company}/jobs?content=true
    """

    async def fetch_jobs(
        self,
        company_name: str,
        company_slug: str,
        domain: str = "Tech",
    ) -> List[JobItem]:
        url = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs"
        jobs: List[JobItem] = []

        try:
            async with httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=self.timeout) as client:
                response = await client.get(url)
                if response.status_code == 404:
                    logger.warning(f"Greenhouse board not found for slug '{company_slug}'")
                    return []
                response.raise_for_status()
                data = response.json()

            raw_jobs = data.get("jobs", [])
            for rj in raw_jobs:
                title = rj.get("title", "").strip()
                if not title:
                    continue

                apply_url = rj.get("absolute_url") or f"https://boards.greenhouse.io/{company_slug}/jobs/{rj.get('id')}"
                raw_location = rj.get("location", {}).get("name", "")
                raw_date = rj.get("first_published") or rj.get("updated_at")

                date_posted = parse_posting_date(raw_date)
                category, seniority = classify_role(title)
                location, country, is_remote = parse_location(raw_location, title)

                # Extract departments/tags
                raw_tags = []
                for dept in rj.get("departments", []):
                    if dept.get("name"):
                        raw_tags.append(dept["name"])
                for office in rj.get("offices", []):
                    if office.get("name"):
                        raw_tags.append(office["name"])

                job = JobItem.create(
                    title=title,
                    company=company_name,
                    apply_url=apply_url,
                    date_posted=date_posted,
                    source="greenhouse",
                    domain=domain,
                    category=category,
                    seniority=seniority,
                    location=location,
                    country=country,
                    is_remote=is_remote,
                    raw_tags=raw_tags,
                )
                jobs.append(job)

            logger.info(f"Greenhouse: Fetched {len(jobs)} jobs for {company_name} ({company_slug})")
            return jobs

        except Exception as e:
            logger.error(f"Error fetching Greenhouse jobs for {company_name} ({company_slug}): {e}")
            return []

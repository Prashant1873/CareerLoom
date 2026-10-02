import logging
from typing import List
import httpx

from backend.app.models.job import JobItem
from backend.app.scrapers.base import BaseATSConnector, DEFAULT_HEADERS
from backend.app.utils.classifier import classify_role, parse_location
from backend.app.utils.date_parser import parse_posting_date

logger = logging.getLogger("careerloom.lever")


class LeverConnector(BaseATSConnector):
    """
    Ingests job listings from public Lever API endpoints.
    Endpoint: https://api.lever.co/v0/postings/{company}?mode=json
    """

    async def fetch_jobs(
        self,
        company_name: str,
        company_slug: str,
        domain: str = "Tech",
    ) -> List[JobItem]:
        url = f"https://api.lever.co/v0/postings/{company_slug}?mode=json"
        jobs: List[JobItem] = []

        try:
            async with httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=self.timeout) as client:
                response = await client.get(url)
                if response.status_code == 404:
                    logger.warning(f"Lever board not found for slug '{company_slug}'")
                    return []
                response.raise_for_status()
                data = response.json()

            if not isinstance(data, list):
                logger.warning(f"Unexpected Lever format for {company_slug}")
                return []

            for rj in data:
                title = rj.get("text", "").strip()
                if not title:
                    continue

                apply_url = rj.get("hostedUrl") or rj.get("applyUrl") or f"https://jobs.lever.co/{company_slug}/{rj.get('id')}"
                cats = rj.get("categories", {})
                raw_location = cats.get("location", "")
                raw_date = rj.get("createdAt")  # Epoch milliseconds

                date_posted = parse_posting_date(raw_date)
                category, seniority = classify_role(title)
                location, country, is_remote = parse_location(raw_location, title)

                # Check workplaceType field in Lever
                workplace_type = rj.get("workplaceType", "").lower()
                if "remote" in workplace_type:
                    is_remote = True

                # Extract tags/departments
                raw_tags = []
                if cats.get("department"):
                    raw_tags.append(cats["department"])
                if cats.get("team"):
                    raw_tags.append(cats["team"])
                if cats.get("commitment"):
                    raw_tags.append(cats["commitment"])

                description = rj.get("descriptionPlain") or ""
                description_summary = description[:300] + "..." if len(description) > 300 else (description or None)

                job = JobItem.create(
                    title=title,
                    company=company_name,
                    apply_url=apply_url,
                    date_posted=date_posted,
                    source="lever",
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

            logger.info(f"Lever: Fetched {len(jobs)} jobs for {company_name} ({company_slug})")
            return jobs

        except Exception as e:
            logger.error(f"Error fetching Lever jobs for {company_name} ({company_slug}): {e}")
            return []

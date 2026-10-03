import logging
from typing import List
import httpx

from backend.app.models.job import JobItem
from backend.app.scrapers.base import BaseATSConnector, DEFAULT_HEADERS
from backend.app.utils.classifier import classify_role, parse_location
from backend.app.utils.date_parser import parse_posting_date

logger = logging.getLogger("careerloom.workday")


class WorkdayConnector(BaseATSConnector):
    """
    Ingests job listings from public Workday Candidate Experience Service (CXS) endpoints.
    Endpoint: https://{subdomain}.myworkdayjobs.com/wday/cxs/{tenant}/{career_site}/jobs
    Used by major global enterprise employers (Pfizer, Target, Adobe, Morgan Stanley).
    """

    async def fetch_jobs(
        self,
        company_name: str,
        company_slug: str,
        domain: str = "Enterprise",
    ) -> List[JobItem]:
        # Parse slug format: "tenant/career_site" or just "tenant"
        parts = company_slug.split("/")
        tenant = parts[0]
        career_site = parts[1] if len(parts) > 1 else "Careers"
        subdomain = tenant

        url = f"https://{subdomain}.wd1.myworkdayjobs.com/wday/cxs/{tenant}/{career_site}/jobs"
        jobs: List[JobItem] = []

        headers = {
            **DEFAULT_HEADERS,
            "Content-Type": "application/json",
        }

        payload = {
            "appliedFacets": {},
            "limit": 50,
            "offset": 0,
            "searchText": "",
        }

        try:
            async with httpx.AsyncClient(headers=headers, timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 404:
                    # Try alternative non-wd1 endpoint
                    alt_url = f"https://{subdomain}.myworkdayjobs.com/wday/cxs/{tenant}/{career_site}/jobs"
                    response = await client.post(alt_url, json=payload)

                if response.status_code != 200:
                    logger.warning(f"Workday endpoint returned {response.status_code} for {company_name}")
                    return []

                data = response.json()

            postings = data.get("jobPostings", [])
            for posting in postings:
                title = posting.get("title", "").strip()
                if not title:
                    continue

                external_path = posting.get("externalPath", "")
                apply_url = f"https://{subdomain}.myworkdayjobs.com/en-US/{tenant}/{career_site}{external_path}"
                raw_location = posting.get("locationsText", "")
                posted_on = posting.get("postedOn", "")

                date_posted = parse_posting_date(posted_on)
                category, seniority = classify_role(title)
                location, country, is_remote = parse_location(raw_location, title)

                job = JobItem.create(
                    title=title,
                    company=company_name,
                    apply_url=apply_url,
                    date_posted=date_posted,
                    source="workday",
                    domain=domain,
                    category=category,
                    seniority=seniority,
                    location=location or raw_location,
                    country=country,
                    is_remote=is_remote,
                    raw_tags=[domain, "Enterprise", "Fortune 500"],
                )
                jobs.append(job)

            logger.info(f"Workday: Fetched {len(jobs)} jobs for {company_name} ({company_slug})")
            return jobs

        except Exception as e:
            logger.error(f"Error fetching Workday jobs for {company_name} ({company_slug}): {e}")
            return []

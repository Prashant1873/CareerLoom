import logging
from typing import List
import httpx

from backend.app.models.job import JobItem
from backend.app.scrapers.base import BaseATSConnector, DEFAULT_HEADERS
from backend.app.utils.classifier import classify_role, parse_location
from backend.app.utils.date_parser import parse_posting_date

logger = logging.getLogger("careerloom.smartrecruiters")


class SmartRecruitersConnector(BaseATSConnector):
    """
    Ingests job listings from public SmartRecruiters candidate API endpoints.
    Endpoint: https://api.smartrecruiters.com/v1/companies/{company}/postings
    Used by major global employers (Visa, Bosch, IKEA, Ubisoft, Skechers).
    """

    async def fetch_jobs(
        self,
        company_name: str,
        company_slug: str,
        domain: str = "Tech",
    ) -> List[JobItem]:
        url = f"https://api.smartrecruiters.com/v1/companies/{company_slug}/postings?limit=100"
        jobs: List[JobItem] = []

        try:
            async with httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=self.timeout) as client:
                response = await client.get(url)
                if response.status_code == 404:
                    logger.warning(f"SmartRecruiters company not found for slug '{company_slug}'")
                    return []
                response.raise_for_status()
                data = response.json()

            raw_postings = data.get("content", [])
            for posting in raw_postings:
                title = posting.get("name", "").strip()
                if not title:
                    continue

                posting_id = posting.get("id", "")
                apply_url = f"https://jobs.smartrecruiters.com/{company_slug}/{posting_id}"

                # Location parsing
                loc_obj = posting.get("location", {})
                city = loc_obj.get("city", "")
                region = loc_obj.get("region", "")
                country_code = loc_obj.get("country", "")
                is_loc_remote = bool(loc_obj.get("remote", False))

                location_str = ", ".join(filter(None, [city, region, country_code.upper()]))
                date_posted = parse_posting_date(posting.get("releasedDate"))
                category, seniority = classify_role(title)
                loc_text, country, is_remote_classified = parse_location(location_str, title, company_hint=company_name)
                cc = country_code.upper()
                if cc in ("IN", "IND"):
                    country = "India"
                elif cc in ("US", "USA"):
                    country = "United States"
                elif cc in ("GB", "UK"):
                    country = "United Kingdom"
                elif cc in ("DE", "GER"):
                    country = "Germany"

                tags = []
                func = posting.get("function", {}).get("label")
                if func:
                    tags.append(func)
                ind = posting.get("industry", {}).get("label")
                if ind:
                    tags.append(ind)

                job = JobItem.create(
                    title=title,
                    company=company_name,
                    apply_url=apply_url,
                    date_posted=date_posted,
                    source="smartrecruiters",
                    domain=domain,
                    category=category,
                    seniority=seniority,
                    location=location_str or loc_text,
                    country=country_code.upper() if len(country_code) == 2 else country,
                    is_remote=is_loc_remote or is_remote_classified,
                    raw_tags=tags,
                )
                jobs.append(job)

            logger.info(f"SmartRecruiters: Fetched {len(jobs)} jobs for {company_name} ({company_slug})")
            return jobs

        except Exception as e:
            logger.error(f"Error fetching SmartRecruiters jobs for {company_name} ({company_slug}): {e}")
            return []

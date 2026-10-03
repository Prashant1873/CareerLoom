import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.app.db.database import upsert_jobs
from backend.app.scrapers.ashby import AshbyConnector
from backend.app.scrapers.greenhouse import GreenhouseConnector
from backend.app.scrapers.lever import LeverConnector
from backend.app.scrapers.llm_scraper import LLMPortalExtractor

logger = logging.getLogger("careerloom.sync")

COMPANIES_FILE = Path(__file__).resolve().parent.parent / "data" / "companies.json"
CUSTOM_PORTALS_FILE = Path(__file__).resolve().parent.parent / "data" / "custom_portals.json"


class JobSyncService:
    def __init__(self):
        self.connectors = {
            "greenhouse": GreenhouseConnector(),
            "lever": LeverConnector(),
            "ashby": AshbyConnector(),
        }
        self.portal_extractor = LLMPortalExtractor()

    def load_companies(self) -> List[Dict[str, str]]:
        if not COMPANIES_FILE.exists():
            logger.error(f"Companies file missing at {COMPANIES_FILE}")
            return []
        with open(COMPANIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_custom_portals(self) -> List[Dict[str, str]]:
        if not CUSTOM_PORTALS_FILE.exists():
            logger.warning(f"Custom portals catalog missing at {CUSTOM_PORTALS_FILE}")
            return []
        with open(CUSTOM_PORTALS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    async def sync_custom_portals(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Crawls and ingests non-standard corporate career portals using BeautifulSoup & LLM scraper.
        """
        portals = self.load_custom_portals()
        if limit:
            portals = portals[:limit]

        total_synced = 0
        results = []
        for p in portals:
            company = p["company"]
            url = p["career_url"]
            domain = p.get("domain", "Enterprise")
            try:
                jobs = await self.portal_extractor.scrape_portal(url, company, default_domain=domain)
                if jobs:
                    inserted = await upsert_jobs(jobs)
                    total_synced += inserted
                    results.append({"company": company, "jobs_synced": inserted, "status": "success"})
                else:
                    results.append({"company": company, "jobs_synced": 0, "status": "no_jobs_extracted"})
            except Exception as e:
                logger.error("Failed scraping custom portal for %s: %s", company, e)
                results.append({"company": company, "error": str(e), "status": "error"})

        return {"total_jobs_synced": total_synced, "portals_processed": len(portals), "details": results}

    async def sync_company(self, company_info: Dict[str, str]) -> int:
        name = company_info["name"]
        slug = company_info["slug"]
        ats_type = company_info.get("ats_type", "greenhouse").lower()
        domain = company_info.get("domain", "Tech")

        connector = self.connectors.get(ats_type)
        if not connector:
            logger.error(f"Unknown ATS type '{ats_type}' for {name}")
            return 0

        try:
            jobs = await connector.fetch_jobs(
                company_name=name,
                company_slug=slug,
                domain=domain,
            )
            if jobs:
                inserted = await upsert_jobs(jobs)
                logger.info(f"Synced {inserted} jobs for {name}")
                return inserted
            return 0
        except Exception as e:
            logger.error(f"Failed to sync {name}: {e}")
            return 0

    async def sync_all(self, concurrency: int = 5, limit_companies: Optional[int] = None) -> Dict[str, object]:
        companies = self.load_companies()
        if limit_companies:
            companies = companies[:limit_companies]

        logger.info(f"Starting sync across {len(companies)} companies with concurrency {concurrency}...")
        semaphore = asyncio.Semaphore(concurrency)
        total_synced = 0
        processed_count = 0
        errors: List[str] = []

        async def _bounded_sync(company: Dict[str, str]):
            nonlocal total_synced, processed_count
            async with semaphore:
                try:
                    count = await self.sync_company(company)
                    total_synced += count
                    processed_count += 1
                except Exception as e:
                    errors.append(f"{company.get('name')}: {str(e)}")

        tasks = [_bounded_sync(comp) for comp in companies]
        await asyncio.gather(*tasks, return_exceptions=True)

        logger.info(f"Sync complete. Synced {total_synced} jobs across {processed_count} companies.")
        return {
            "total_jobs_synced": total_synced,
            "companies_processed": processed_count,
            "errors": errors,
        }

    async def live_fetch_company(self, company_name: str, company_slug: str, ats_type: Optional[str] = None) -> int:
        """
        On-demand instant fetch for a specific firm.
        """
        # If ATS type not provided, check companies.json or try greenhouse first
        if not ats_type:
            all_comps = self.load_companies()
            match = next((c for c in all_comps if c["slug"].lower() == company_slug.lower()), None)
            ats_type = match["ats_type"] if match else "greenhouse"

        return await self.sync_company({
            "name": company_name,
            "slug": company_slug,
            "ats_type": ats_type,
            "domain": "Tech",
        })

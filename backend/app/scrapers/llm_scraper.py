import json
import logging
import re
from typing import Any, Dict, List, Optional

from backend.app.models.job import JobItem
from backend.app.scrapers.custom_crawler import CustomPortalCrawler
from backend.app.services.llm_adapter import LLMQueryService, get_llm_service
from backend.app.services.taxonomy import match_category_phrase
from backend.app.utils.classifier import classify_role
from backend.app.utils.date_parser import parse_posting_date

logger = logging.getLogger("careerloom.scrapers.llm_scraper")


class LLMPortalExtractor:
    """
    Intelligent graph/semantic scraper for unstructured enterprise career portals.
    Combines BeautifulSoup DOM cleaning with LLM extraction and rule-based fallbacks.
    """

    def __init__(self, llm_service: Optional[LLMQueryService] = None):
        self.crawler = CustomPortalCrawler()
        self.llm = llm_service or get_llm_service()

    def _heuristic_normalize_candidate(
        self, candidate: Dict[str, Any], company: str, default_domain: str
    ) -> JobItem:
        """
        Extracts structured attributes from raw HTML text snippet using heuristics.
        """
        title = candidate.get("title", "").strip()
        apply_url = candidate.get("apply_url", "").strip()
        snippet = candidate.get("raw_snippet", "")

        # Detect remote
        is_remote = any(
            w in snippet.lower() or w in title.lower()
            for w in ["remote", "work from anywhere", "distributed", "virtual"]
        )

        # Detect location/country
        country = "Global"
        location = "Multiple Locations"
        if "united states" in snippet.lower() or "usa" in snippet.lower() or "us |" in snippet.lower():
            country = "United States"
            location = "United States"
        elif "united kingdom" in snippet.lower() or "london" in snippet.lower() or "uk |" in snippet.lower():
            country = "United Kingdom"
            location = "London, UK"
        elif "germany" in snippet.lower() or "berlin" in snippet.lower() or "munich" in snippet.lower():
            country = "Germany"
            location = "Germany"
        elif "india" in snippet.lower() or "bengaluru" in snippet.lower() or "bangalore" in snippet.lower():
            country = "India"
            location = "India"
        elif "singapore" in snippet.lower():
            country = "Singapore"
            location = "Singapore"
        elif is_remote:
            location = "Remote"

        # Match category & seniority & track
        category, seniority, track = classify_role(title, company=company, domain_hint=default_domain)

        # Parse date from snippet if present
        date_posted = parse_posting_date(snippet)

        return JobItem.create(
            title=title,
            company=company,
            domain=default_domain,
            category=category,
            track=track,
            seniority=seniority,
            location=location,
            country=country,
            is_remote=is_remote,
            date_posted=date_posted,
            apply_url=apply_url,
            source="custom_portal",
            description_summary=snippet[:200] if snippet else None,
            raw_tags=[t for t in [category, seniority, track, default_domain] if t and t != "general"],
        )

    async def scrape_portal(
        self,
        portal_url: str,
        company: str,
        default_domain: str = "Enterprise",
        html_override: Optional[str] = None,
    ) -> List[JobItem]:
        """
        Crawls and extracts structured JobItems from a custom career portal URL.
        """
        html = html_override or await self.crawler.fetch_page(portal_url)
        if not html:
            logger.warning("Could not fetch portal content for %s (%s)", company, portal_url)
            return []

        # Step 1: Extract candidate card blocks from DOM
        candidate_blocks = self.crawler.extract_job_candidate_blocks(html, portal_url)
        if not candidate_blocks:
            logger.info("No DOM candidate blocks found directly on %s", portal_url)
            return []

        logger.info(
            "Found %d candidate job blocks for %s. Normalizing...",
            len(candidate_blocks),
            company,
        )

        jobs: List[JobItem] = []
        for cand in candidate_blocks:
            try:
                job_item = self._heuristic_normalize_candidate(cand, company, default_domain)
                jobs.append(job_item)
            except Exception as e:
                logger.debug("Failed to normalize candidate %s: %s", cand, e)

        return jobs

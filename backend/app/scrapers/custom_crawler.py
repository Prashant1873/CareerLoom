import asyncio
import logging
import random
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from backend.app.utils.date_parser import parse_posting_date

logger = logging.getLogger("careerloom.scrapers.custom_crawler")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
]

DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}


class CustomPortalCrawler:
    """
    Polite, browser-mimicking crawler for custom enterprise career portals.
    Strips boilerplate and extracts structured job listing candidate blocks.
    """

    def __init__(self, timeout_seconds: float = 12.0, max_concurrency: int = 3):
        self.timeout = timeout_seconds
        self.semaphore = asyncio.Semaphore(max_concurrency)

    def _get_headers(self) -> Dict[str, str]:
        headers = dict(DEFAULT_HEADERS)
        headers["User-Agent"] = random.choice(USER_AGENTS)
        return headers

    async def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetches an HTML page with polite delay and browser headers.
        """
        async with self.semaphore:
            # Polite random jitter delay to prevent rapid-fire requests
            await asyncio.sleep(random.uniform(0.1, 0.4))
            try:
                async with httpx.AsyncClient(
                    headers=self._get_headers(),
                    follow_redirects=True,
                    timeout=self.timeout,
                    verify=True,
                ) as client:
                    resp = await client.get(url)
                    if resp.status_code == 200:
                        return resp.text
                    logger.warning("Crawler got status %s for url %s", resp.status_code, url)
                    return None
            except Exception as e:
                logger.warning("Crawler failed fetching %s: %s", url, e)
                return None

    def clean_html(self, html: str) -> BeautifulSoup:
        """
        Strips non-content tags (scripts, styles, headers, footers, SVGs)
        to isolate the core textual content.
        """
        soup = BeautifulSoup(html, "lxml")

        # Strip unneeded structural and media elements
        for tag in soup(
            [
                "script",
                "style",
                "svg",
                "path",
                "noscript",
                "iframe",
                "header",
                "footer",
                "nav",
                "link",
                "meta",
            ]
        ):
            tag.decompose()

        return soup

    def extract_job_candidate_blocks(self, html: str, base_url: str) -> List[Dict[str, Any]]:
        """
        Scans DOM for card-like blocks or career links indicating job listings.
        Extracts title, apply link, location hint, and snippet.
        """
        soup = self.clean_html(html)
        candidates: List[Dict[str, Any]] = []
        seen_links = set()

        # Strategy 1: Look for anchor tags pointing to job/career paths
        job_url_pattern = re.compile(
            r"/(jobs?|careers?|positions?|openings?|roles?)/[a-zA-Z0-9_\-\/]+",
            re.IGNORECASE,
        )

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            full_url = urljoin(base_url, href)

            if full_url in seen_links:
                continue

            link_text = a.get_text(separator=" ", strip=True)
            # Filter out non-job navigation links like 'View All Jobs' or 'Back to Careers'
            if len(link_text) < 4 or len(link_text) > 120:
                continue

            is_job_link = bool(job_url_pattern.search(href))
            parent_text = a.parent.get_text(separator=" ", strip=True) if a.parent else ""

            # Check if link text looks like a role title or the link matches the regex
            if is_job_link or any(
                term in link_text.lower()
                for term in [
                    "engineer",
                    "developer",
                    "manager",
                    "analyst",
                    "designer",
                    "director",
                    "consultant",
                    "intern",
                    "associate",
                    "specialist",
                    "lead",
                    "scientist",
                ]
            ):
                seen_links.add(full_url)

                # Extract possible location snippet from container
                container = a.find_parent(["div", "li", "tr", "article"])
                container_text = (
                    container.get_text(separator=" | ", strip=True) if container else parent_text
                )

                candidates.append(
                    {
                        "title": link_text,
                        "apply_url": full_url,
                        "raw_snippet": container_text[:300],
                    }
                )

        return candidates

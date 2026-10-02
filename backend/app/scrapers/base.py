import logging
from abc import ABC, abstractmethod
from typing import List, Optional
import httpx

from backend.app.models.job import JobItem

logger = logging.getLogger("careerloom.scrapers")

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 CareerLoom/1.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}


class BaseATSConnector(ABC):
    """
    Abstract base class for direct public ATS connectors.
    """
    def __init__(self, timeout: float = 12.0):
        self.timeout = timeout

    @abstractmethod
    async def fetch_jobs(
        self,
        company_name: str,
        company_slug: str,
        domain: str = "Tech",
    ) -> List[JobItem]:
        """
        Fetches and normalizes job listings from the ATS for a specific employer.
        """
        pass

import asyncio
import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

import httpx

from backend.app.db.database import (
    get_target_by_slug,
    is_domain_probed,
    record_probed_domain,
    upsert_target,
)
from backend.app.models.target import CareerTarget

logger = logging.getLogger("careerloom.discovery_prober")

# Stop-words to reject false positive entity matches from post titles/text
STOP_WORDS = {
    "india", "bangalore", "remote", "delhi", "mumbai", "hyderabad", "pune", "gurgaon", "noida",
    "developer", "developers", "engineer", "engineers", "engineering", "software", "frontend",
    "backend", "fullstack", "product", "manager", "management", "designer", "intern", "internship",
    "freshers", "fresher", "senior", "junior", "lead", "staff", "anyone", "referral", "referrals",
    "interview", "interviews", "salary", "hiring", "openings", "opening", "looking", "apply", "careers",
    "career", "urgent", "update", "advice", "help", "please", "company", "companies", "startup",
    "startups", "tech", "technology", "google", "amazon", "microsoft", "meta", "apple"  # already known
}

# Known Indian startup entities to prioritize
KNOWN_TECH_ENTITIES = {
    "swiggy", "zomato", "zepto", "blinkit", "cred", "groww", "meesho", "phonepe", "razorpay",
    "paytm", "inmobi", "glance", "atlan", "signoz", "sarvam", "browserstack", "postman", "hasura",
    "urban company", "nykaa", "delhivery", "porter", "navi", "slice", "pocket fm", "druva",
    "highradius", "zenoti", "mindtickle", "zeta", "thoughtworks", "truecaller", "instawork",
    "acceldata", "nobroker", "ixigo", "unacademy", "kredx", "lendingkart", "turtlemint", "cars24",
    "whatfix", "blusmart", "ather", "rapido", "spinny", "licious", "shiprocket", "khatabook",
    "classplus", "darwinbox", "clevertap", "moengage", "webengage", "chargebee", "kissflow",
    "hackerrank", "interviewbit", "yellow.ai", "haptik", "verloop", "entrupy", "cultfit", "pharmeasy",
    "tata 1mg", "practo", "jar", "jupiter", "fi money", "indmoney", "smallcase", "cashfree", "payu"
}

ATS_PATTERNS = [
    ("greenhouse", re.compile(r"boards\.greenhouse\.io/([a-zA-Z0-9_\-]+)", re.IGNORECASE)),
    ("lever", re.compile(r"jobs\.lever\.co/([a-zA-Z0-9_\-]+)", re.IGNORECASE)),
    ("ashby", re.compile(r"jobs\.ashbyhq\.com/([a-zA-Z0-9_\-]+)", re.IGNORECASE)),
    ("smartrecruiters", re.compile(r"careers\.smartrecruiters\.com/([a-zA-Z0-9_\-]+)", re.IGNORECASE)),
]

COMPANY_MENTION_PATTERNS = [
    re.compile(r"\b([A-Z][a-zA-Z0-9]{2,25})\s+(?:is\s+)?hiring\b"),
    re.compile(r"\b(?:hiring|openings?|roles?|jobs?)\s+at\s+([A-Z][a-zA-Z0-9]{2,25})\b"),
    re.compile(r"\b([A-Z][a-zA-Z0-9]{2,25})\s+careers?\b"),
    re.compile(r"\b(?:referral|referrals?)\s+for\s+([A-Z][a-zA-Z0-9]{2,25})\b"),
]


class DiscoveryEntityProber:
    """
    Extracts employer names and career links from Reddit posts, performs concurrent
    probing of candidate ATS feeds, and enrolls verified targets into the database.
    """

    def __init__(self, probe_timeout_seconds: float = 3.0, max_concurrency: int = 5):
        self.probe_timeout_seconds = probe_timeout_seconds
        self.semaphore = asyncio.Semaphore(max_concurrency)

    def extract_candidates_from_text(self, text: str) -> List[Tuple[str, Optional[str], Optional[str]]]:
        """
        Parses text for:
        1. Direct ATS links -> (company_slug, ats_type, direct_url)
        2. Mentioned company entities -> (company_name, None, None)
        """
        candidates: List[Tuple[str, Optional[str], Optional[str]]] = []
        seen: Set[str] = set()

        if not text:
            return []

        # 1. Direct ATS URL parsing
        for ats_name, pattern in ATS_PATTERNS:
            for match in pattern.finditer(text):
                slug = match.group(1).lower().strip()
                if slug and slug not in seen and slug not in STOP_WORDS:
                    seen.add(slug)
                    candidates.append((slug, ats_name, match.group(0)))

        # 2. Heuristic company mention matching
        for pattern in COMPANY_MENTION_PATTERNS:
            for match in pattern.finditer(text):
                name = match.group(1).strip()
                slug = CareerTarget.generate_slug(name)
                if slug not in seen and slug not in STOP_WORDS and len(slug) >= 3:
                    seen.add(slug)
                    candidates.append((name, None, None))

        # 3. Known entity keyword matching
        text_lower = text.lower()
        for entity in KNOWN_TECH_ENTITIES:
            slug = CareerTarget.generate_slug(entity)
            if slug not in seen and re.search(rf"\b{re.escape(entity)}\b", text_lower):
                seen.add(slug)
                candidates.append((entity.title(), None, None))

        return candidates

    async def probe_ats_candidate(
        self,
        name_or_slug: str,
        hint_ats: Optional[str] = None,
        direct_url: Optional[str] = None,
    ) -> Optional[CareerTarget]:
        """
        Tests public ATS API endpoints for a candidate company name or slug.
        Returns a verified CareerTarget if >= 1 active posting is found.
        """
        slug = CareerTarget.generate_slug(name_or_slug)
        if not slug or slug in STOP_WORDS:
            return None

        # Check negative cache
        cached_status = await is_domain_probed(slug)
        if cached_status in ("non_ats", "failed"):
            return None

        # Check if already registered in career_targets
        existing = await get_target_by_slug(slug)
        if existing:
            return None

        async with self.semaphore:
            headers = {"User-Agent": "CareerLoom-Discovery/1.0"}
            async with httpx.AsyncClient(timeout=self.probe_timeout_seconds, headers=headers) as client:
                probe_endpoints = []
                if hint_ats == "greenhouse":
                    probe_endpoints = [("greenhouse", f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs")]
                elif hint_ats == "lever":
                    probe_endpoints = [("lever", f"https://api.lever.co/v0/postings/{slug}?mode=json")]
                elif hint_ats == "ashby":
                    probe_endpoints = [("ashby", f"https://api.ashbyhq.com/posting-api/job-board/{slug}")]
                elif hint_ats == "smartrecruiters":
                    probe_endpoints = [("smartrecruiters", f"https://api.smartrecruiters.com/v1/companies/{slug}/postings")]
                else:
                    # Probe all canonical endpoints concurrently
                    probe_endpoints = [
                        ("greenhouse", f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"),
                        ("lever", f"https://api.lever.co/v0/postings/{slug}?mode=json"),
                        ("ashby", f"https://api.ashbyhq.com/posting-api/job-board/{slug}"),
                        ("smartrecruiters", f"https://api.smartrecruiters.com/v1/companies/{slug}/postings"),
                    ]

                for ats_type, endpoint in probe_endpoints:
                    try:
                        resp = await client.get(endpoint)
                        if resp.status_code == 200:
                            data = resp.json()
                            job_count = 0
                            if ats_type == "greenhouse":
                                job_count = len(data.get("jobs", []))
                            elif ats_type == "lever":
                                job_count = len(data) if isinstance(data, list) else 0
                            elif ats_type == "ashby":
                                job_count = len(data.get("jobs", []))
                            elif ats_type == "smartrecruiters":
                                job_count = len(data.get("content", []))

                            if job_count > 0:
                                # Candidate verified!
                                career_url = direct_url or (
                                    f"https://boards.greenhouse.io/{slug}" if ats_type == "greenhouse"
                                    else f"https://jobs.lever.co/{slug}" if ats_type == "lever"
                                    else f"https://jobs.ashbyhq.com/{slug}" if ats_type == "ashby"
                                    else f"https://careers.smartrecruiters.com/{slug}"
                                )
                                target = CareerTarget.create(
                                    name=name_or_slug.title(),
                                    slug=slug,
                                    career_url=career_url,
                                    ats_type=ats_type,
                                    feed_url=endpoint,
                                    category_tier="startup",
                                    domain="Tech / Ecosystem Discovery",
                                    role_focus=["tech", "product", "founders_office"],
                                    status="active",
                                    job_count=job_count,
                                )
                                target.last_status = "ok"
                                await upsert_target(target)
                                await record_probed_domain(slug, status="verified", ttl_days=14)
                                logger.info(f"Verified & enrolled target {target.name} ({ats_type}) with {job_count} jobs.")
                                return target
                    except Exception:
                        pass

                # If all probes failed, record negative cache for 7 days
                await record_probed_domain(slug, status="non_ats", ttl_days=7)
                return None

    async def process_discovery_posts(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parses discovery posts, extracts candidate company mentions, probes ATS endpoints,
        and returns discovery statistics.
        """
        candidates: List[Tuple[str, Optional[str], Optional[str]]] = []
        for post in posts:
            title = post.get("title", "")
            selftext = post.get("selftext", "")
            url = post.get("url", "")
            full_text = f"{title} {selftext} {url}"
            extracted = self.extract_candidates_from_text(full_text)
            candidates.extend(extracted)

        # Deduplicate candidates by slug
        unique_candidates: Dict[str, Tuple[str, Optional[str], Optional[str]]] = {}
        for name, ats_hint, direct_url in candidates:
            s = CareerTarget.generate_slug(name)
            if s and s not in unique_candidates:
                unique_candidates[s] = (name, ats_hint, direct_url)

        enrolled_targets: List[CareerTarget] = []

        async def _probe_single(item):
            name, ats_hint, direct_url = item
            target = await self.probe_ats_candidate(name, ats_hint, direct_url)
            if target:
                enrolled_targets.append(target)

        tasks = [_probe_single(c) for c in unique_candidates.values()]
        await asyncio.gather(*tasks, return_exceptions=True)

        return {
            "posts_processed": len(posts),
            "candidates_found": len(unique_candidates),
            "targets_enrolled": len(enrolled_targets),
            "enrolled_slugs": [t.slug for t in enrolled_targets],
        }


_prober_instance: Optional[DiscoveryEntityProber] = None


def get_discovery_prober() -> DiscoveryEntityProber:
    global _prober_instance
    if _prober_instance is None:
        _prober_instance = DiscoveryEntityProber()
    return _prober_instance

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Setup project root import
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.db.database import get_connection, init_db, upsert_targets
from backend.app.models.target import CareerTarget
from backend.scripts.add_indian_companies import INDIAN_COMPANIES_CATALOG

logger = logging.getLogger("careerloom.seed_targets")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

COMPANIES_FILE = PROJECT_ROOT / "backend" / "app" / "data" / "companies.json"

# Curated Tier-1 Strategy & Management Consulting firms
CONSULTING_FIRMS = {
    "mckinsey", "mckinsey & company", "bcg", "boston consulting group", "bain", "bain & company",
    "kearney", "oliver wyman", "roland berger", "strategy&", "alvarez & marsal", "dalberg",
    "samagra", "arthur d. little", "everest group", "zinnov", "monitor deloitte"
}

# Curated Indian tech giants, unicorns, and high-growth firms
INDIAN_UNICORNS = {
    "paytm", "cred", "meesho", "groww", "inmobi", "glance", "freshworks", "slice", "swiggy",
    "porter", "hackerrank", "sarvam", "sarvam ai", "atlan", "navi", "fi", "fi money",
    "pocketfm", "pocket fm", "druva", "highradius", "zenoti", "mindtickle", "signoz", "zeta",
    "thoughtworks", "truecaller", "instawork", "acceldata", "nobroker", "ixigo", "abhibus",
    "unacademy", "kredx", "lendingkart", "turtlemint", "cars24", "whatfix", "zepto", "zomato",
    "blinkit", "flipkart", "phonepe", "postman", "browserstack", "hasura", "urban company",
    "nykaa", "delhivery", "razorpay"
}

# Established Indian Conglomerates & IT enterprises
INDIAN_ENTERPRISES = {
    "tata", "tata digital", "tata 1mg", "reliance", "jio", "infosys", "wipro", "tcs", "hcl",
    "l&t", "mahindra", "titan", "aditya birla", "bosch", "target india"
}


def infer_tier(name: str, domain: str, slug: str) -> str:
    n_low = name.lower()
    s_low = slug.lower()
    d_low = domain.lower()

    if any(c in n_low or c in s_low for c in CONSULTING_FIRMS) or "consulting" in d_low:
        return "consulting"
    if any(u in n_low or u in s_low for u in INDIAN_UNICORNS):
        return "unicorn"
    if any(e in n_low or e in s_low for e in INDIAN_ENTERPRISES) or "conglomerate" in d_low:
        return "enterprise"
    if "startup" in d_low or "seed" in d_low or "ai /" in d_low:
        return "startup"
    return "enterprise"


def infer_role_focus(tier: str, domain: str, name: str) -> List[str]:
    d_low = domain.lower()
    n_low = name.lower()

    if tier == "consulting" or "consulting" in d_low:
        return ["strategy", "consulting", "product"]
    if tier in ("unicorn", "startup"):
        tags = ["tech", "product"]
        if "fintech" in d_low or "commerce" in d_low or "consumer" in d_low:
            tags.extend(["strategy", "founders_office"])
        return tags
    if "data" in d_low or "ai" in d_low:
        return ["tech", "product", "ai_research"]
    return ["tech", "product"]


def infer_career_url(ats_type: str, slug: str, name: str) -> str:
    ats = ats_type.lower()
    if ats == "greenhouse":
        return f"https://boards.greenhouse.io/{slug}"
    elif ats == "lever":
        return f"https://jobs.lever.co/{slug}"
    elif ats == "ashby":
        return f"https://jobs.ashbyhq.com/{slug}"
    elif ats == "smartrecruiters":
        return f"https://careers.smartrecruiters.com/{slug}"
    elif ats == "workday":
        return f"https://{slug}.wd1.myworkdayjobs.com/careers"
    return f"https://www.google.com/search?q={name}+careers"


def infer_feed_url(ats_type: str, slug: str) -> Optional[str]:
    ats = ats_type.lower()
    if ats == "greenhouse":
        return f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
    elif ats == "lever":
        return f"https://api.lever.co/v0/postings/{slug}?mode=json"
    elif ats == "ashby":
        return f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
    elif ats == "smartrecruiters":
        return f"https://api.smartrecruiters.com/v1/companies/{slug}/postings"
    return None


def collect_seed_targets() -> List[CareerTarget]:
    """
    Consolidates Indian startups, unicorns, conglomerates, and global companies
    into a unified collection of CareerTarget models.
    """
    targets_map: Dict[str, CareerTarget] = {}

    # 1. Ingest Indian Startups & Unicorns from add_indian_companies.py
    for c in INDIAN_COMPANIES_CATALOG:
        name = c["name"]
        slug = CareerTarget.generate_slug(c.get("slug") or name)
        ats_type = c.get("ats_type", "lever").lower()
        domain = c.get("domain", "Tech / Startups")
        tier = infer_tier(name, domain, slug)
        role_focus = infer_role_focus(tier, domain, name)
        career_url = infer_career_url(ats_type, slug, name)
        feed_url = infer_feed_url(ats_type, slug)

        target = CareerTarget.create(
            name=name,
            career_url=career_url,
            ats_type=ats_type,
            category_tier=tier,
            domain=domain,
            feed_url=feed_url,
            role_focus=role_focus,
            slug=slug,
            status="active",
        )
        targets_map[slug] = target

    # 2. Ingest Global + Indian catalog from companies.json
    if COMPANIES_FILE.exists():
        with open(COMPANIES_FILE, "r", encoding="utf-8") as f:
            global_comps = json.load(f)

        for c in global_comps:
            name = c.get("name")
            if not name:
                continue
            slug = CareerTarget.generate_slug(c.get("slug") or name)
            # If already added via curated Indian catalog, preserve enriched tier/tags unless missing
            if slug in targets_map:
                continue

            ats_type = c.get("ats_type", "greenhouse").lower()
            domain = c.get("domain", "Enterprise Tech")
            tier = infer_tier(name, domain, slug)
            role_focus = infer_role_focus(tier, domain, name)
            career_url = infer_career_url(ats_type, slug, name)
            feed_url = infer_feed_url(ats_type, slug)

            target = CareerTarget.create(
                name=name,
                career_url=career_url,
                ats_type=ats_type,
                category_tier=tier,
                domain=domain,
                feed_url=feed_url,
                role_focus=role_focus,
                slug=slug,
                status="active",
            )
            targets_map[slug] = target

    return list(targets_map.values())


async def seed_career_targets(force: bool = False) -> int:
    """
    Seeds career_targets table in SQLite. Idempotent by default.
    """
    await init_db()

    async with get_connection() as db:
        async with db.execute("SELECT COUNT(*) as count FROM career_targets") as cur:
            row = await cur.fetchone()
            existing_count = row["count"] if row else 0

    if existing_count > 0 and not force:
        logger.info(f"career_targets table already contains {existing_count} targets. Skipping seed.")
        return existing_count

    targets = collect_seed_targets()
    inserted_count = await upsert_targets(targets)
    logger.info(f"Successfully seeded {inserted_count} career targets into SQLite.")
    return inserted_count


if __name__ == "__main__":
    force_flag = "--force" in sys.argv
    count = asyncio.run(seed_career_targets(force=force_flag))
    print(f"\nDone! career_targets table holds {count} active targets.")

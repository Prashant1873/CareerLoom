"""
Seed Career Targets Script.
Idempotently populates and synchronizes career_targets table from partitioned
curated datasets (startups, conglomerates, consulting) and legacy company catalogs.
"""
import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

# Setup project root import
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.db.database import get_connection, init_db, upsert_targets
from backend.app.models.target import CareerTarget
from backend.scripts.add_indian_companies import INDIAN_COMPANIES_CATALOG

logger = logging.getLogger("careerloom.seed_targets")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

TARGETS_DIR = PROJECT_ROOT / "backend" / "app" / "data" / "targets"
COMPANIES_FILE = PROJECT_ROOT / "backend" / "app" / "data" / "companies.json"

VALID_ROLE_TAGS: Set[str] = {
    "product",
    "strategy",
    "tech",
    "founders_office",
    "consulting",
    "leadership",
    "operations",
}

CONSULTING_FIRMS = {
    "mckinsey", "mckinsey & company", "bcg", "boston consulting group", "bain", "bain & company",
    "kearney", "oliver wyman", "roland berger", "strategy&", "alvarez & marsal", "dalberg",
    "samagra", "arthur d. little", "everest group", "zinnov", "monitor deloitte"
}

INDIAN_CONGLOMERATES = {
    "tata", "tata sons", "tata digital", "tata 1mg", "tcs", "reliance", "jio", "infosys",
    "wipro", "l&t", "mahindra", "titan", "aditya birla", "godrej", "itc", "bajaj"
}

INDIAN_UNICORNS = {
    "paytm", "cred", "meesho", "groww", "inmobi", "glance", "freshworks", "slice", "swiggy",
    "porter", "hackerrank", "sarvam", "sarvam ai", "atlan", "navi", "fi", "fi money",
    "pocketfm", "pocket fm", "druva", "highradius", "zenoti", "mindtickle", "signoz", "zeta",
    "thoughtworks", "truecaller", "instawork", "acceldata", "nobroker", "ixigo", "abhibus",
    "unacademy", "kredx", "lendingkart", "turtlemint", "cars24", "whatfix", "zepto", "zomato",
    "blinkit", "flipkart", "phonepe", "postman", "browserstack", "hasura", "urban company",
    "nykaa", "delhivery", "razorpay", "makemytrip", "redbus", "cleartrip", "payu"
}


def sanitize_role_focus(tags: Optional[List[str]]) -> List[str]:
    """Ensures role focus tags only contain valid standardized taxonomy tags."""
    if not tags:
        return ["tech"]
    clean = [t.strip().lower() for t in tags if t.strip().lower() in VALID_ROLE_TAGS]
    return clean or ["tech"]


def infer_tier(name: str, domain: str, slug: str) -> str:
    n_low = name.lower()
    s_low = slug.lower()
    d_low = domain.lower()

    if any(c in n_low or c in s_low for c in CONSULTING_FIRMS) or "consulting" in d_low:
        return "consulting"
    if any(cg in n_low or cg in s_low for cg in INDIAN_CONGLOMERATES) or "conglomerate" in d_low:
        return "conglomerate"
    if any(u in n_low or u in s_low for u in INDIAN_UNICORNS):
        return "unicorn"
    return "startup"


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


def collect_seed_targets(targets_dir: Optional[Path] = None) -> List[CareerTarget]:
    """
    Consolidates partitioned datasets (startups, conglomerates, consulting)
    along with fallback catalogs into a deduplicated list of CareerTarget models.
    """
    directory = targets_dir or TARGETS_DIR
    targets_map: Dict[str, CareerTarget] = {}

    partition_files = [
        directory / "indian_startups.json",
        directory / "indian_conglomerates.json",
        directory / "strategy_consulting.json",
    ]

    # 1. Ingest partitioned JSON catalog files
    for p_path in partition_files:
        if not p_path.exists():
            logger.warning(f"Partition file not found: {p_path}")
            continue

        try:
            with open(p_path, "r", encoding="utf-8") as f:
                items = json.load(f)
            logger.info(f"Loaded {len(items)} items from {p_path.name}")

            for item in items:
                name = item.get("name")
                if not name:
                    continue
                slug = CareerTarget.generate_slug(item.get("slug") or name)
                ats_type = (item.get("ats_type") or "custom").lower()
                category_tier = (item.get("category_tier") or "startup").lower()
                domain = item.get("domain", "Tech")
                career_url = item.get("career_url") or infer_career_url(ats_type, slug, name)
                feed_url = item.get("feed_url") or infer_feed_url(ats_type, slug)
                role_focus = sanitize_role_focus(item.get("role_focus"))
                website = item.get("website")

                target = CareerTarget.create(
                    name=name,
                    career_url=career_url,
                    ats_type=ats_type,
                    category_tier=category_tier,
                    domain=domain,
                    website=website,
                    feed_url=feed_url,
                    role_focus=role_focus,
                    slug=slug,
                    status="active",
                    job_count=0,
                )
                targets_map[slug] = target

        except Exception as e:
            logger.error(f"Error reading partition {p_path}: {e}")

    # 2. Ingest curated Indian catalog from add_indian_companies.py as fallback/supplement
    for c in INDIAN_COMPANIES_CATALOG:
        name = c["name"]
        slug = CareerTarget.generate_slug(c.get("slug") or name)
        if slug in targets_map:
            continue

        ats_type = c.get("ats_type", "lever").lower()
        domain = c.get("domain", "Tech / Startups")
        tier = infer_tier(name, domain, slug)
        role_focus = sanitize_role_focus(c.get("role_focus"))
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
            job_count=0,
        )
        targets_map[slug] = target

    # 3. Ingest global catalog from companies.json as supplement
    if COMPANIES_FILE.exists():
        try:
            with open(COMPANIES_FILE, "r", encoding="utf-8") as f:
                global_comps = json.load(f)

            for c in global_comps:
                name = c.get("name")
                if not name:
                    continue
                slug = CareerTarget.generate_slug(c.get("slug") or name)
                if slug in targets_map:
                    continue

                ats_type = (c.get("ats_type") or "greenhouse").lower()
                domain = c.get("domain", "Enterprise Tech")
                tier = infer_tier(name, domain, slug)
                role_focus = sanitize_role_focus(c.get("role_focus"))
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
                    job_count=0,
                )
                targets_map[slug] = target
        except Exception as e:
            logger.warning(f"Error reading companies.json: {e}")

    return list(targets_map.values())


async def seed_career_targets(
    force: bool = False,
    dry_run: bool = False,
    targets_dir: Optional[Path] = None,
) -> int:
    """
    Seeds career_targets table in SQLite. Idempotent by default.
    Preserves existing live telemetry, job_count, and scrape history.
    """
    await init_db()

    targets = collect_seed_targets(targets_dir)

    if dry_run:
        logger.info(f"[DRY RUN] Would seed/upsert {len(targets)} targets into career_targets.")
        return len(targets)

    async with get_connection() as db:
        async with db.execute("SELECT COUNT(*) as count FROM career_targets") as cur:
            row = await cur.fetchone()
            existing_count = row["count"] if row else 0

    inserted_count = await upsert_targets(targets)
    logger.info(
        f"Successfully seeded {inserted_count} career targets into SQLite (prior count: {existing_count})."
    )
    return inserted_count


def parse_args():
    parser = argparse.ArgumentParser(description="Seed Career Targets into CareerLoom SQLite database")
    parser.add_argument("--force", action="store_true", help="Force re-seeding of targets")
    parser.add_argument("--dry-run", action="store_true", help="Simulate seeding without executing DB writes")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    count = asyncio.run(seed_career_targets(force=args.force, dry_run=args.dry_run))
    print(f"\nDone! Processed {count} career targets.")

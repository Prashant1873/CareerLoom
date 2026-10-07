import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import aiosqlite

from backend.app.models.job import JobFilterParams, JobItem
from backend.app.models.lead import CandidateLead
from backend.app.models.target import CareerTarget, CareerTargetFilterParams, CareerTargetStats

logger = logging.getLogger("careerloom.database")

# Ensure the database resides in data/jobs.db
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DB_PATH = DATA_DIR / "jobs.db"


from contextlib import asynccontextmanager

_shared_conn: Optional[aiosqlite.Connection] = None

@asynccontextmanager
async def get_connection():
    global _shared_conn
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if _shared_conn is None:
        _shared_conn = await aiosqlite.connect(str(DB_PATH))
        _shared_conn.row_factory = aiosqlite.Row
        await _shared_conn.execute("PRAGMA journal_mode=WAL")
        await _shared_conn.execute("PRAGMA synchronous=NORMAL")
        await _shared_conn.execute("PRAGMA cache_size=-64000")
    yield _shared_conn

async def close_db() -> None:
    global _shared_conn
    if _shared_conn is not None:
        try:
            await _shared_conn.close()
        except Exception:
            pass
        _shared_conn = None


async def _ensure_column(db: aiosqlite.Connection, table: str, column: str, col_type: str) -> None:
    async with db.execute(f"PRAGMA table_info({table})") as cursor:
        rows = await cursor.fetchall()
        cols = [r["name"] for r in rows]
        if column not in cols:
            await db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")


async def init_db() -> None:
    """
    Initializes the SQLite database schema and indexes.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    async with get_connection() as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                domain TEXT NOT NULL,
                category TEXT NOT NULL,
                seniority TEXT NOT NULL,
                location TEXT NOT NULL,
                country TEXT NOT NULL,
                is_remote INTEGER NOT NULL,
                date_posted TEXT NOT NULL,
                apply_url TEXT NOT NULL,
                source TEXT NOT NULL,
                description_summary TEXT,
                raw_tags TEXT
            )
        """)

        # Performance indexes for sub-50ms faceted searches and chronological sorting
        await db.execute("CREATE INDEX IF NOT EXISTS idx_jobs_date_posted ON jobs (date_posted DESC)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs (company)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_jobs_category ON jobs (category)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_jobs_domain ON jobs (domain)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_jobs_country ON jobs (country)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_jobs_is_remote ON jobs (is_remote)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_jobs_seniority ON jobs (seniority)")

        # Soft-archive columns on jobs table
        await _ensure_column(db, "jobs", "is_active", "INTEGER DEFAULT 1")
        await _ensure_column(db, "jobs", "last_seen_at", "TEXT")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_jobs_is_active ON jobs (is_active)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_jobs_active_date ON jobs (is_active, date_posted DESC)")

        # Career targets repository table (Phase 11)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS career_targets (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                website TEXT,
                career_url TEXT NOT NULL,
                ats_type TEXT NOT NULL,
                feed_url TEXT,
                category_tier TEXT NOT NULL,
                domain TEXT NOT NULL,
                role_focus TEXT,
                status TEXT DEFAULT 'active',
                last_scraped_at TEXT,
                last_status TEXT,
                job_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)
        await db.execute("CREATE INDEX IF NOT EXISTS idx_targets_category ON career_targets (category_tier)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_targets_status ON career_targets (status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_targets_last_scraped ON career_targets (last_scraped_at)")

        # Candidate leads table for referral acceleration engine (Phase 10)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS candidate_leads (
                id TEXT PRIMARY KEY,
                job_id TEXT NOT NULL,
                company TEXT NOT NULL,
                role_title TEXT NOT NULL,
                candidate_name TEXT NOT NULL,
                email TEXT NOT NULL,
                linkedin_url TEXT,
                yoe REAL NOT NULL,
                current_ctc_lpa REAL,
                expected_ctc_lpa REAL,
                notice_period_days INTEGER DEFAULT 30,
                resume_url TEXT,
                status TEXT DEFAULT 'new',
                created_at TEXT NOT NULL
            )
        """)
        await db.execute("CREATE INDEX IF NOT EXISTS idx_leads_company ON candidate_leads (company)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_leads_job_id ON candidate_leads (job_id)")
        # Reddit discovery cache table (Phase 12)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS discovery_cache (
                id TEXT PRIMARY KEY,
                subreddit TEXT NOT NULL,
                post_id TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT,
                selftext TEXT,
                payload TEXT NOT NULL,
                scanned_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            )
        """)
        await db.execute("CREATE INDEX IF NOT EXISTS idx_disc_sub ON discovery_cache (subreddit)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_disc_expires ON discovery_cache (expires_at)")

        # Probed domains and ATS negative cache (Phase 12)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS probed_cache (
                domain_or_slug TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                probed_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            )
        """)
        await db.execute("CREATE INDEX IF NOT EXISTS idx_probed_expires ON probed_cache (expires_at)")

        await db.commit()
    logger.info(f"Database initialized at {DB_PATH}")


def _row_to_job(row: aiosqlite.Row) -> JobItem:
    raw_tags = []
    if row["raw_tags"]:
        try:
            raw_tags = json.loads(row["raw_tags"])
        except Exception:
            raw_tags = [t.strip() for t in row["raw_tags"].split(",") if t.strip()]

    # Parse ISO timestamp
    raw_date = row["date_posted"]
    try:
        date_posted = datetime.fromisoformat(raw_date)
        if date_posted.tzinfo is None:
            date_posted = date_posted.replace(tzinfo=timezone.utc)
    except Exception:
        date_posted = datetime.now(timezone.utc)

    return JobItem(
        id=row["id"],
        title=row["title"],
        company=row["company"],
        domain=row["domain"],
        category=row["category"],
        seniority=row["seniority"],
        location=row["location"],
        country=row["country"],
        is_remote=bool(row["is_remote"]),
        date_posted=date_posted,
        apply_url=row["apply_url"],
        source=row["source"],
        description_summary=row["description_summary"],
        raw_tags=raw_tags,
    )


async def upsert_jobs(jobs: List[JobItem]) -> int:
    """
    Bulk upserts normalized JobItems into SQLite.
    """
    if not jobs:
        return 0

    now_iso = datetime.now(timezone.utc).isoformat()
    records = [
        (
            job.id,
            job.title,
            job.company,
            job.domain,
            job.category,
            job.seniority,
            job.location,
            job.country,
            1 if job.is_remote else 0,
            job.date_posted.isoformat(),
            job.apply_url,
            job.source,
            job.description_summary,
            json.dumps(job.raw_tags),
            1,
            now_iso,
        )
        for job in jobs
    ]

    async with get_connection() as db:
        await db.executemany(
            """
            INSERT OR REPLACE INTO jobs (
                id, title, company, domain, category, seniority,
                location, country, is_remote, date_posted, apply_url,
                source, description_summary, raw_tags, is_active, last_seen_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            records,
        )
        await db.commit()

    return len(records)


async def query_jobs(params: JobFilterParams) -> Tuple[List[JobItem], int]:
    """
    Faceted query returning a paginated list of JobItems and the total count.
    """
    conditions: List[str] = []
    values: List[object] = []

    if not params.include_inactive:
        conditions.append("is_active = 1")

    if params.search:
        # Match title or company
        search_pattern = f"%{params.search.strip()}%"
        conditions.append("(title LIKE ? OR company LIKE ? OR category LIKE ?)")
        values.extend([search_pattern, search_pattern, search_pattern])

    if params.company:
        conditions.append("LOWER(company) = LOWER(?)")
        values.append(params.company.strip())

    if params.category:
        conditions.append("LOWER(category) = LOWER(?)")
        values.append(params.category.strip())

    if params.domain:
        conditions.append("LOWER(domain) = LOWER(?)")
        values.append(params.domain.strip())

    if params.country:
        c_lower = params.country.lower().strip()
        if c_lower == "remote":
            conditions.append("is_remote = 1")
        elif c_lower in ("europe", "eu"):
            eu_countries = [
                "united kingdom", "germany", "france", "ireland", "netherlands",
                "switzerland", "spain", "italy", "sweden", "poland", "europe"
            ]
            placeholders = ",".join("?" for _ in eu_countries)
            conditions.append(f"(LOWER(country) IN ({placeholders}) OR (is_remote = 1 AND LOWER(country) = 'global'))")
            values.extend(eu_countries)
        elif c_lower in ("us", "usa", "united states"):
            conditions.append("(LOWER(country) IN ('united states', 'usa', 'us') OR (is_remote = 1 AND LOWER(country) = 'global'))")
        else:
            conditions.append("(LOWER(country) = LOWER(?) OR (is_remote = 1 AND LOWER(?) = 'global'))")
            values.extend([params.country.strip(), params.country.strip()])

    target_loc = params.metro_hub or params.location
    if target_loc:
        loc_lower = target_loc.lower().strip()
        if "bengaluru" in loc_lower or "bangalore" in loc_lower or loc_lower == "blr":
            conditions.append("(LOWER(location) LIKE '%bengaluru%' OR LOWER(location) LIKE '%bangalore%' OR LOWER(location) LIKE '%blr%')")
        elif "delhi" in loc_lower or "ncr" in loc_lower or "gurgaon" in loc_lower or "gurugram" in loc_lower or "noida" in loc_lower:
            conditions.append("(LOWER(location) LIKE '%delhi%' OR LOWER(location) LIKE '%noida%' OR LOWER(location) LIKE '%gurgaon%' OR LOWER(location) LIKE '%gurugram%' OR LOWER(location) LIKE '%ncr%')")
        elif "hyderabad" in loc_lower or loc_lower == "hyd":
            conditions.append("(LOWER(location) LIKE '%hyderabad%' OR LOWER(location) LIKE '%hyd%' OR LOWER(location) LIKE '%secunderabad%')")
        elif "pune" in loc_lower or loc_lower == "pun":
            conditions.append("(LOWER(location) LIKE '%pune%' OR LOWER(location) LIKE '%pun%')")
        elif "mumbai" in loc_lower or "bombay" in loc_lower or loc_lower == "bom":
            conditions.append("(LOWER(location) LIKE '%mumbai%' OR LOWER(location) LIKE '%bombay%' OR LOWER(location) LIKE '%navi mumbai%' OR LOWER(location) LIKE '%thane%')")
        elif "chennai" in loc_lower or "madras" in loc_lower or loc_lower == "maa":
            conditions.append("(LOWER(location) LIKE '%chennai%' OR LOWER(location) LIKE '%madras%')")
        elif loc_lower == "remote":
            conditions.append("is_remote = 1")
        else:
            loc_pattern = f"%{loc_lower}%"
            conditions.append("LOWER(location) LIKE ?")
            values.append(loc_pattern)

    if params.seniority:
        conditions.append("LOWER(seniority) = LOWER(?)")
        values.append(params.seniority.strip())

    if params.is_remote is not None:
        conditions.append("is_remote = ?")
        values.append(1 if params.is_remote else 0)

    if params.posted_within_days:
        cutoff = datetime.now(timezone.utc) - timedelta(days=params.posted_within_days)
        conditions.append("date_posted >= ?")
        values.append(cutoff.isoformat())

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    # Resolve sorting
    sort_clause = "date_posted DESC"
    if params.sort_by == "company":
        sort_clause = "company ASC, date_posted DESC"
    elif params.sort_by == "title":
        sort_clause = "title ASC, date_posted DESC"

    count_sql = f"SELECT COUNT(*) as total FROM jobs {where_clause}"
    select_sql = f"""
        SELECT * FROM jobs
        {where_clause}
        ORDER BY {sort_clause}
        LIMIT ? OFFSET ?
    """

    async with get_connection() as db:
        # Total count
        async with db.execute(count_sql, values) as cursor:
            count_row = await cursor.fetchone()
            total = count_row["total"] if count_row else 0

        # Paginated results
        fetch_values = list(values) + [params.limit, params.offset]
        async with db.execute(select_sql, fetch_values) as cursor:
            rows = await cursor.fetchall()
            jobs = [_row_to_job(r) for r in rows]

    return jobs, total


async def get_stats() -> Dict[str, object]:
    """
    Returns statistics about indexed job listings.
    """
    async with get_connection() as db:
        async with db.execute("SELECT COUNT(*) as total FROM jobs") as cursor:
            total_jobs = (await cursor.fetchone())["total"]

        async with db.execute("SELECT COUNT(DISTINCT company) as companies FROM jobs") as cursor:
            total_companies = (await cursor.fetchone())["companies"]

        async with db.execute("SELECT MAX(date_posted) as latest FROM jobs") as cursor:
            latest_post = (await cursor.fetchone())["latest"]

    return {
        "total_jobs": total_jobs,
        "total_companies": total_companies,
        "latest_posting_date": latest_post,
    }


async def get_filter_options() -> Dict[str, List[str]]:
    """
    Returns unique categories, domains, and countries for UI filters.
    """
    async with get_connection() as db:
        async with db.execute("SELECT DISTINCT category FROM jobs WHERE category IS NOT NULL ORDER BY category") as cursor:
            categories = [r["category"] for r in await cursor.fetchall() if r["category"]]

        async with db.execute("SELECT DISTINCT domain FROM jobs WHERE domain IS NOT NULL ORDER BY domain") as cursor:
            domains = [r["domain"] for r in await cursor.fetchall() if r["domain"]]

        async with db.execute("SELECT DISTINCT country FROM jobs WHERE country IS NOT NULL ORDER BY country") as cursor:
            countries = [r["country"] for r in await cursor.fetchall() if r["country"]]

        async with db.execute("SELECT DISTINCT company FROM jobs WHERE company IS NOT NULL ORDER BY company") as cursor:
            companies = [r["company"] for r in await cursor.fetchall() if r["company"]]

    return {
        "categories": categories,
        "domains": domains,
        "countries": countries,
        "companies": companies,
    }


async def insert_lead(lead: CandidateLead) -> str:
    """
    Inserts a candidate lead record into SQLite.
    """
    async with get_connection() as db:
        await db.execute(
            """
            INSERT INTO candidate_leads (
                id, job_id, company, role_title, candidate_name,
                email, linkedin_url, yoe, current_ctc_lpa, expected_ctc_lpa,
                notice_period_days, resume_url, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                lead.id,
                lead.job_id,
                lead.company,
                lead.role_title,
                lead.candidate_name,
                lead.email,
                lead.linkedin_url,
                lead.yoe,
                lead.current_ctc_lpa,
                lead.expected_ctc_lpa,
                lead.notice_period_days,
                lead.resume_url,
                lead.status,
                lead.created_at.isoformat(),
            ),
        )
        await db.commit()
    return lead.id


async def get_leads(
    company: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> Tuple[List[CandidateLead], int]:
    """
    Queries candidate leads with optional company or status filtering.
    """
    conditions: List[str] = []
    values: List[object] = []

    if company:
        conditions.append("LOWER(company) = LOWER(?)")
        values.append(company.strip())
    if status:
        conditions.append("status = ?")
        values.append(status.strip())

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    count_query = f"SELECT COUNT(*) FROM candidate_leads {where_clause}"
    select_query = f"""
        SELECT * FROM candidate_leads
        {where_clause}
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """

    async with get_connection() as db:
        async with db.execute(count_query, values) as cursor:
            row = await cursor.fetchone()
            total = row[0] if row else 0

        async with db.execute(select_query, values + [limit, offset]) as cursor:
            rows = await cursor.fetchall()
            leads = [CandidateLead.from_row(dict(r)) for r in rows]

    return leads, total


def _row_to_target(row: aiosqlite.Row) -> CareerTarget:
    role_focus = []
    if row["role_focus"]:
        try:
            role_focus = json.loads(row["role_focus"])
        except Exception:
            role_focus = [t.strip() for t in row["role_focus"].split(",") if t.strip()]

    return CareerTarget(
        id=row["id"],
        name=row["name"],
        slug=row["slug"],
        website=row["website"],
        career_url=row["career_url"],
        ats_type=row["ats_type"],
        feed_url=row["feed_url"],
        category_tier=row["category_tier"],
        domain=row["domain"],
        role_focus=role_focus,
        status=row["status"] or "active",
        last_scraped_at=row["last_scraped_at"],
        last_status=row["last_status"],
        job_count=row["job_count"] or 0,
        created_at=row["created_at"],
    )


async def upsert_target(target: CareerTarget) -> None:
    """
    Inserts or updates a single CareerTarget by unique slug.
    """
    async with get_connection() as db:
        await db.execute(
            """
            INSERT INTO career_targets (
                id, name, slug, website, career_url, ats_type,
                feed_url, category_tier, domain, role_focus, status,
                last_scraped_at, last_status, job_count, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(slug) DO UPDATE SET
                name=excluded.name,
                website=excluded.website,
                career_url=excluded.career_url,
                ats_type=excluded.ats_type,
                feed_url=excluded.feed_url,
                category_tier=excluded.category_tier,
                domain=excluded.domain,
                role_focus=excluded.role_focus,
                status=excluded.status,
                last_scraped_at=COALESCE(excluded.last_scraped_at, career_targets.last_scraped_at),
                last_status=COALESCE(excluded.last_status, career_targets.last_status),
                job_count=excluded.job_count
            """,
            (
                target.id,
                target.name,
                target.slug,
                target.website,
                target.career_url,
                target.ats_type,
                target.feed_url,
                target.category_tier,
                target.domain,
                json.dumps(target.role_focus),
                target.status,
                target.last_scraped_at,
                target.last_status,
                target.job_count,
                target.created_at,
            ),
        )
        await db.commit()


async def upsert_targets(targets: List[CareerTarget]) -> int:
    """
    Batch inserts or updates a list of CareerTargets.
    """
    if not targets:
        return 0
    records = [
        (
            t.id,
            t.name,
            t.slug,
            t.website,
            t.career_url,
            t.ats_type,
            t.feed_url,
            t.category_tier,
            t.domain,
            json.dumps(t.role_focus),
            t.status,
            t.last_scraped_at,
            t.last_status,
            t.job_count,
            t.created_at,
        )
        for t in targets
    ]
    async with get_connection() as db:
        await db.executemany(
            """
            INSERT INTO career_targets (
                id, name, slug, website, career_url, ats_type,
                feed_url, category_tier, domain, role_focus, status,
                last_scraped_at, last_status, job_count, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(slug) DO UPDATE SET
                name=excluded.name,
                website=excluded.website,
                career_url=excluded.career_url,
                ats_type=excluded.ats_type,
                feed_url=excluded.feed_url,
                category_tier=excluded.category_tier,
                domain=excluded.domain,
                role_focus=excluded.role_focus,
                status=excluded.status,
                last_scraped_at=COALESCE(excluded.last_scraped_at, career_targets.last_scraped_at),
                last_status=COALESCE(excluded.last_status, career_targets.last_status),
                job_count=excluded.job_count
            """,
            records,
        )
        await db.commit()
    return len(targets)


async def get_targets(params: CareerTargetFilterParams) -> Tuple[List[CareerTarget], int]:
    """
    Queries career targets with optional filtering and pagination.
    """
    conditions: List[str] = []
    values: List[object] = []

    if params.category_tier:
        conditions.append("LOWER(category_tier) = LOWER(?)")
        values.append(params.category_tier.strip())

    if params.domain:
        conditions.append("LOWER(domain) = LOWER(?)")
        values.append(params.domain.strip())

    if params.status:
        conditions.append("LOWER(status) = LOWER(?)")
        values.append(params.status.strip())

    if params.role_tag:
        conditions.append("LOWER(role_focus) LIKE ?")
        values.append(f'%"{params.role_tag.strip().lower()}"%')

    if params.search:
        search_pattern = f"%{params.search.strip().lower()}%"
        conditions.append("(LOWER(name) LIKE ? OR LOWER(slug) LIKE ? OR LOWER(domain) LIKE ?)")
        values.extend([search_pattern, search_pattern, search_pattern])

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    count_sql = f"SELECT COUNT(*) as total FROM career_targets {where_clause}"
    select_sql = f"""
        SELECT * FROM career_targets
        {where_clause}
        ORDER BY name ASC
        LIMIT ? OFFSET ?
    """

    async with get_connection() as db:
        async with db.execute(count_sql, values) as cursor:
            count_row = await cursor.fetchone()
            total = count_row["total"] if count_row else 0

        fetch_values = list(values) + [params.limit, params.offset]
        async with db.execute(select_sql, fetch_values) as cursor:
            rows = await cursor.fetchall()
            targets = [_row_to_target(r) for r in rows]

    return targets, total


async def get_target_by_slug(slug: str) -> Optional[CareerTarget]:
    """
    Retrieves a single CareerTarget by slug.
    """
    async with get_connection() as db:
        async with db.execute("SELECT * FROM career_targets WHERE LOWER(slug) = LOWER(?)", [slug.strip()]) as cursor:
            row = await cursor.fetchone()
            if row:
                return _row_to_target(row)
    return None


async def get_target_stats() -> CareerTargetStats:
    """
    Calculates aggregate metrics across monitored career targets and live postings.
    """
    async with get_connection() as db:
        async with db.execute("SELECT COUNT(*) as total FROM career_targets") as cursor:
            total_targets = (await cursor.fetchone())["total"]

        async with db.execute("SELECT COUNT(*) as active FROM career_targets WHERE status = 'active'") as cursor:
            active_targets = (await cursor.fetchone())["active"]

        async with db.execute("SELECT category_tier, COUNT(*) as count FROM career_targets GROUP BY category_tier") as cursor:
            tier_rows = await cursor.fetchall()
            by_tier = {r["category_tier"]: r["count"] for r in tier_rows}

        async with db.execute("SELECT COUNT(*) as live_jobs FROM jobs WHERE is_active = 1") as cursor:
            live_jobs = (await cursor.fetchone())["live_jobs"]

    return CareerTargetStats(
        total_targets=total_targets,
        active_targets=active_targets,
        by_tier=by_tier,
        total_live_jobs=live_jobs,
    )


async def reconcile_target_jobs(
    company: str,
    live_job_ids: List[str],
    sync_timestamp: Optional[str] = None,
) -> Dict[str, int]:
    """
    Reconciles job postings for a target company:
    - Marks live job IDs as is_active = 1 and updates last_seen_at.
    - Soft-archives vanished postings (is_active = 0).
    - Updates career_targets table metadata (job_count, last_scraped_at, last_status).
    """
    ts = sync_timestamp or datetime.now(timezone.utc).isoformat()
    company_clean = company.strip()

    async with get_connection() as db:
        if live_job_ids:
            placeholders = ",".join("?" for _ in live_job_ids)
            # Mark live jobs as active and update last_seen_at
            await db.execute(
                f"UPDATE jobs SET is_active = 1, last_seen_at = ? WHERE id IN ({placeholders})",
                [ts] + live_job_ids,
            )
            # Soft archive vanished jobs for this company
            cursor = await db.execute(
                f"UPDATE jobs SET is_active = 0 WHERE LOWER(company) = LOWER(?) AND id NOT IN ({placeholders})",
                [company_clean] + live_job_ids,
            )
            archived_count = cursor.rowcount
        else:
            # If no live jobs returned, soft-archive all jobs for this company
            cursor = await db.execute(
                "UPDATE jobs SET is_active = 0 WHERE LOWER(company) = LOWER(?)",
                [company_clean],
            )
            archived_count = cursor.rowcount

        # Update career_targets metadata
        await db.execute(
            """
            UPDATE career_targets
            SET job_count = ?, last_scraped_at = ?, last_status = 'ok'
            WHERE LOWER(name) = LOWER(?) OR LOWER(slug) = LOWER(?)
            """,
            (len(live_job_ids), ts, company_clean, company_clean.replace(" ", "-")),
        )
        await db.commit()

    logger.info(
        f"Reconciled jobs for {company_clean}: {len(live_job_ids)} live, {archived_count} soft-archived"
    )
    return {"live_count": len(live_job_ids), "archived_count": archived_count}


# ============================================================================
# Phase 12: Discovery Cache & Probed Cache Operations
# ============================================================================

async def save_discovery_posts(posts: List[Dict[str, Any]], ttl_hours: int = 24) -> int:
    """
    Saves or updates Reddit discovery posts in discovery_cache table with TTL.
    """
    if not posts:
        return 0

    now = datetime.now(timezone.utc)
    scanned_at = now.isoformat()
    expires_at = (now + timedelta(hours=ttl_hours)).isoformat()

    saved_count = 0
    async with get_connection() as db:
        for p in posts:
            subreddit = str(p.get("subreddit", "")).replace("r/", "").strip()
            post_id = str(p.get("id", p.get("post_id", ""))).strip()
            if not post_id or not subreddit:
                continue

            cache_id = f"{subreddit}_{post_id}"
            title = str(p.get("title", "")).strip()
            url = str(p.get("url", "")).strip()
            selftext = str(p.get("selftext", "")).strip()
            payload = json.dumps(p)

            await db.execute(
                """
                INSERT INTO discovery_cache (id, subreddit, post_id, title, url, selftext, payload, scanned_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    url = excluded.url,
                    selftext = excluded.selftext,
                    payload = excluded.payload,
                    scanned_at = excluded.scanned_at,
                    expires_at = excluded.expires_at
                """,
                (cache_id, subreddit, post_id, title, url, selftext, payload, scanned_at, expires_at),
            )
            saved_count += 1
        await db.commit()

    return saved_count


async def get_cached_discovery_posts(
    subreddit: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Retrieves unexpired cached discovery posts.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    async with get_connection() as db:
        if subreddit:
            clean_sub = subreddit.replace("r/", "").strip().lower()
            cursor = await db.execute(
                """
                SELECT payload FROM discovery_cache
                WHERE LOWER(subreddit) = ? AND expires_at > ?
                ORDER BY scanned_at DESC
                LIMIT ?
                """,
                (clean_sub, now_iso, limit),
            )
        else:
            cursor = await db.execute(
                """
                SELECT payload FROM discovery_cache
                WHERE expires_at > ?
                ORDER BY scanned_at DESC
                LIMIT ?
                """,
                (now_iso, limit),
            )
        rows = await cursor.fetchall()
        results = []
        for r in rows:
            try:
                results.append(json.loads(r["payload"]))
            except Exception:
                pass
        return results


async def record_probed_domain(
    domain_or_slug: str,
    status: str,
    ttl_days: int = 7,
) -> None:
    """
    Records outcome of probing an employer or ATS domain/slug with TTL.
    """
    key = domain_or_slug.strip().lower()
    if not key:
        return

    now = datetime.now(timezone.utc)
    probed_at = now.isoformat()
    expires_at = (now + timedelta(days=ttl_days)).isoformat()

    async with get_connection() as db:
        await db.execute(
            """
            INSERT INTO probed_cache (domain_or_slug, status, probed_at, expires_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(domain_or_slug) DO UPDATE SET
                status = excluded.status,
                probed_at = excluded.probed_at,
                expires_at = excluded.expires_at
            """,
            (key, status, probed_at, expires_at),
        )
        await db.commit()


async def is_domain_probed(domain_or_slug: str) -> Optional[str]:
    """
    Checks if a domain or slug is cached and unexpired in probed_cache.
    Returns status ('verified', 'failed', 'non_ats') if found, else None.
    """
    key = domain_or_slug.strip().lower()
    if not key:
        return None

    now_iso = datetime.now(timezone.utc).isoformat()
    async with get_connection() as db:
        cursor = await db.execute(
            """
            SELECT status FROM probed_cache
            WHERE domain_or_slug = ? AND expires_at > ?
            """,
            (key, now_iso),
        )
        row = await cursor.fetchone()
        if row:
            return row["status"]
        return None



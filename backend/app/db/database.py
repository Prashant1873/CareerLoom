import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import aiosqlite

from backend.app.models.job import JobFilterParams, JobItem
from backend.app.models.lead import CandidateLead

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
        await db.execute("CREATE INDEX IF NOT EXISTS idx_leads_created ON candidate_leads (created_at DESC)")

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
        )
        for job in jobs
    ]

    async with get_connection() as db:
        await db.executemany(
            """
            INSERT OR REPLACE INTO jobs (
                id, title, company, domain, category, seniority,
                location, country, is_remote, date_posted, apply_url,
                source, description_summary, raw_tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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


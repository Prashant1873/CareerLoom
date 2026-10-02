import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import aiosqlite

from backend.app.models.job import JobFilterParams, JobItem

logger = logging.getLogger("careerloom.database")

# Ensure the database resides in data/jobs.db
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DB_PATH = DATA_DIR / "jobs.db"


from contextlib import asynccontextmanager

@asynccontextmanager
async def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(str(DB_PATH)) as conn:
        conn.row_factory = aiosqlite.Row
        yield conn


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
        if params.country.lower() == "remote":
            conditions.append("is_remote = 1")
        else:
            conditions.append("(LOWER(country) = LOWER(?) OR (is_remote = 1 AND LOWER(?) = 'global'))")
            values.extend([params.country.strip(), params.country.strip()])

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

    count_sql = f"SELECT COUNT(*) as total FROM jobs {where_clause}"
    select_sql = f"""
        SELECT * FROM jobs
        {where_clause}
        ORDER BY date_posted DESC
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

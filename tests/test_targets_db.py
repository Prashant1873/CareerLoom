import pytest
import pytest_asyncio
from datetime import datetime, timezone

from backend.app.db.database import (
    init_db,
    get_connection,
    upsert_jobs,
    query_jobs,
    upsert_target,
    upsert_targets,
    get_targets,
    get_target_by_slug,
    get_target_stats,
    reconcile_target_jobs,
)
from backend.app.models.job import JobItem, JobFilterParams
from backend.app.models.target import CareerTarget, CareerTargetFilterParams


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    await init_db()
    yield


@pytest.mark.asyncio
async def test_init_db_and_schema():
    async with get_connection() as db:
        # Check career_targets table
        async with db.execute("PRAGMA table_info(career_targets)") as cursor:
            target_cols = [r["name"] for r in await cursor.fetchall()]
            assert "id" in target_cols
            assert "name" in target_cols
            assert "slug" in target_cols
            assert "career_url" in target_cols
            assert "ats_type" in target_cols
            assert "category_tier" in target_cols
            assert "role_focus" in target_cols
            assert "status" in target_cols
            assert "last_scraped_at" in target_cols
            assert "job_count" in target_cols

        # Check jobs table migration columns
        async with db.execute("PRAGMA table_info(jobs)") as cursor:
            job_cols = [r["name"] for r in await cursor.fetchall()]
            assert "is_active" in job_cols
            assert "last_seen_at" in job_cols


@pytest.mark.asyncio
async def test_target_crud_operations():
    t1 = CareerTarget.create(
        name="Swiggy Test",
        career_url="https://swiggy.com/careers",
        ats_type="smartrecruiters",
        category_tier="unicorn",
        domain="Quick Commerce",
        role_focus=["product", "tech"],
        slug="swiggy-test",
    )
    await upsert_target(t1)

    fetched = await get_target_by_slug("swiggy-test")
    assert fetched is not None
    assert fetched.name == "Swiggy Test"
    assert fetched.category_tier == "unicorn"
    assert "product" in fetched.role_focus

    # Batch upsert
    t2 = CareerTarget.create(
        name="McKinsey India Test",
        career_url="https://mckinsey.com/careers",
        ats_type="custom",
        category_tier="consulting",
        domain="Strategy Consulting",
        role_focus=["strategy", "consulting"],
        slug="mckinsey-india-test",
    )
    t3 = CareerTarget.create(
        name="CRED Test",
        career_url="https://cred.club/careers",
        ats_type="lever",
        category_tier="unicorn",
        domain="Fintech",
        role_focus=["tech", "product", "founders_office"],
        slug="cred-test",
    )
    await upsert_targets([t2, t3])

    # Filter by tier = unicorn
    results, total = await get_targets(CareerTargetFilterParams(category_tier="unicorn"))
    slugs = [t.slug for t in results]
    assert "swiggy-test" in slugs
    assert "cred-test" in slugs
    assert "mckinsey-india-test" not in slugs

    # Filter by role_tag = strategy
    strategy_results, _ = await get_targets(CareerTargetFilterParams(role_tag="strategy"))
    assert any(t.slug == "mckinsey-india-test" for t in strategy_results)

    # Search
    search_results, _ = await get_targets(CareerTargetFilterParams(search="McKinsey"))
    assert len(search_results) >= 1
    assert search_results[0].slug == "mckinsey-india-test"


@pytest.mark.asyncio
async def test_target_stats():
    stats = await get_target_stats()
    assert stats.total_targets >= 3
    assert stats.active_targets >= 3
    assert "unicorn" in stats.by_tier
    assert "consulting" in stats.by_tier


@pytest.mark.asyncio
async def test_stale_job_reconciler():
    company = "ReconcileCo"
    # Seed target
    target = CareerTarget.create(
        name=company,
        career_url="https://reconcile.co/careers",
        ats_type="greenhouse",
        slug="reconcileco",
    )
    await upsert_target(target)

    now = datetime.now(timezone.utc)
    # Create 3 jobs
    j1 = JobItem.create(
        title="PM Lead",
        company=company,
        apply_url="https://reconcile.co/jobs/1",
        date_posted=now,
        source="greenhouse",
    )
    j2 = JobItem.create(
        title="SDE-2",
        company=company,
        apply_url="https://reconcile.co/jobs/2",
        date_posted=now,
        source="greenhouse",
    )
    j3 = JobItem.create(
        title="Strategy Associate",
        company=company,
        apply_url="https://reconcile.co/jobs/3",
        date_posted=now,
        source="greenhouse",
    )
    await upsert_jobs([j1, j2, j3])

    # Reconcile with only j1 and j2 (j3 vanished from career portal)
    reconcile_res = await reconcile_target_jobs(company=company, live_job_ids=[j1.id, j2.id])
    assert reconcile_res["live_count"] == 2
    assert reconcile_res["archived_count"] == 1

    # Verify query_jobs default only returns active jobs (j1, j2)
    jobs, total = await query_jobs(JobFilterParams(company=company))
    job_ids = [j.id for j in jobs]
    assert j1.id in job_ids
    assert j2.id in job_ids
    assert j3.id not in job_ids
    assert total == 2

    # Verify include_inactive=True returns all 3
    all_jobs, all_total = await query_jobs(JobFilterParams(company=company, include_inactive=True))
    assert all_total == 3

    # Verify target record updated
    updated_target = await get_target_by_slug("reconcileco")
    assert updated_target is not None
    assert updated_target.job_count == 2
    assert updated_target.last_status == "ok"
    assert updated_target.last_scraped_at is not None

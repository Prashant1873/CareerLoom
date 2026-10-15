import pytest
from starlette.testclient import TestClient

from backend.app.main import app
from backend.app.scrapers.custom_crawler import CustomPortalCrawler
from backend.app.scrapers.llm_scraper import LLMPortalExtractor
from backend.app.services.sync import JobSyncService

SAMPLE_ENTERPRISE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Global Consulting Careers</title>
    <script>var tracking = true;</script>
    <style>.banner { color: red; }</style>
</head>
<body>
    <header><nav><a href="/home">Home</a></nav></header>
    <main>
        <h1>Open Opportunities</h1>
        <div class="job-list">
            <div class="job-card">
                <a href="/careers/positions/associate-consultant-123">Associate Consultant</a>
                <span class="location">London, UK | Full Time</span>
                <span class="date">Posted 2 days ago</span>
                <p>Join our strategy practice working with Fortune 500 clients.</p>
            </div>
            <div class="job-card">
                <a href="/careers/positions/senior-software-engineer-456">Senior Software Engineer</a>
                <span class="location">United States | Remote</span>
                <span class="date">Posted Oct 01, 2026</span>
                <p>Build enterprise cloud platforms with Python and Go.</p>
            </div>
        </div>
    </main>
    <footer><p>&copy; 2026 Enterprise Corp</p></footer>
</body>
</html>
"""


def test_clean_html_strips_boilerplate():
    crawler = CustomPortalCrawler()
    cleaned = crawler.clean_html(SAMPLE_ENTERPRISE_HTML)
    assert cleaned.find("script") is None
    assert cleaned.find("style") is None
    assert cleaned.find("footer") is None
    assert cleaned.find("nav") is None
    assert "Open Opportunities" in cleaned.get_text()


def test_extract_job_candidate_blocks():
    crawler = CustomPortalCrawler()
    candidates = crawler.extract_job_candidate_blocks(
        SAMPLE_ENTERPRISE_HTML, base_url="https://www.example.com"
    )
    assert len(candidates) >= 2
    titles = [c["title"] for c in candidates]
    assert "Associate Consultant" in titles
    assert "Senior Software Engineer" in titles

    urls = [c["apply_url"] for c in candidates]
    assert "https://www.example.com/careers/positions/associate-consultant-123" in urls


@pytest.mark.asyncio
async def test_llm_extractor_heuristic_normalization():
    extractor = LLMPortalExtractor()
    jobs = await extractor.scrape_portal(
        portal_url="https://www.example.com/careers",
        company="Global Strategy Corp",
        default_domain="Consulting",
        html_override=SAMPLE_ENTERPRISE_HTML,
    )

    assert len(jobs) >= 2
    titles = [j.title for j in jobs]
    assert "Associate Consultant" in titles
    assert "Senior Software Engineer" in titles

    # Check the engineer job
    swe = next(j for j in jobs if "Software Engineer" in j.title)
    assert swe.company == "Global Strategy Corp"
    assert swe.is_remote is True
    assert swe.country == "United States"
    assert swe.category == "software_engineering"
    assert swe.source == "custom_portal"

    # Check consultant job
    consultant = next(j for j in jobs if "Consultant" in j.title)
    assert consultant.country == "United Kingdom"
    assert consultant.category in ("management_consulting", "consulting_strategy")


def test_custom_portals_catalog():
    sync = JobSyncService()
    portals = sync.load_custom_portals()
    assert len(portals) >= 4
    companies = [p["company"] for p in portals]
    assert "McKinsey & Company" in companies
    assert "Goldman Sachs" in companies


def test_api_custom_portals():
    client = TestClient(app)
    resp = client.get("/api/jobs/portals")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 4
    assert any(p["company"] == "McKinsey & Company" for p in data["portals"])

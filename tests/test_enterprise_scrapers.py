import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.app.scrapers.smartrecruiters import SmartRecruitersConnector
from backend.app.scrapers.workday import WorkdayConnector
from backend.app.services.sync import JobSyncService


@pytest.mark.asyncio
async def test_smartrecruiters_connector_parsing():
    connector = SmartRecruitersConnector()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "totalFound": 1,
        "content": [
            {
                "id": "743999912345",
                "name": "Senior Software Engineer - Distributed Systems",
                "releasedDate": "2026-10-01T10:00:00.000Z",
                "location": {
                    "city": "Austin",
                    "region": "TX",
                    "country": "us",
                    "remote": True,
                },
                "industry": {"label": "Information Technology"},
                "function": {"label": "Engineering"},
            }
        ],
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        jobs = await connector.fetch_jobs("Visa", "visa", domain="Tech")

        assert len(jobs) == 1
        job = jobs[0]
        assert job.company == "Visa"
        assert "Senior Software Engineer" in job.title
        assert job.category == "software_engineering"
        assert job.seniority == "senior"

        assert job.is_remote is True
        assert job.country == "US"
        assert "jobs.smartrecruiters.com/visa/743999912345" in job.apply_url


@pytest.mark.asyncio
async def test_workday_connector_parsing():
    connector = WorkdayConnector()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "total": 1,
        "jobPostings": [
            {
                "title": "Principal AI Research Scientist",
                "externalPath": "/job/R-998877",
                "postedOn": "Posted 2 Days Ago",
                "locationsText": "Cambridge, MA, United States",
            }
        ],
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        jobs = await connector.fetch_jobs("Pfizer", "pfizer/PfizerCareers", domain="Healthcare")

        assert len(jobs) == 1
        job = jobs[0]
        assert job.company == "Pfizer"
        assert "Principal AI Research Scientist" in job.title
        assert job.category == "data_ai"
        assert job.domain == "Healthcare"

        assert "pfizer.myworkdayjobs.com/en-US/pfizer/PfizerCareers/job/R-998877" in job.apply_url



def test_sync_service_connector_registration():
    service = JobSyncService()
    assert "smartrecruiters" in service.connectors
    assert "workday" in service.connectors
    assert "greenhouse" in service.connectors
    assert "lever" in service.connectors
    assert "ashby" in service.connectors

    portals = service.load_custom_portals()
    assert len(portals) >= 10
    companies = [p["company"] for p in portals]
    assert "Apple" in companies
    assert "Microsoft" in companies
    assert "Citadel" in companies
    assert "Pfizer" in companies

import asyncio
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.database import init_db


@pytest.fixture(autouse=True)
def setup_db():
    asyncio.run(init_db())


client = TestClient(app)


def test_lead_submission_and_persistence():
    lead_payload = {
        "job_id": "test_job_123",
        "company": "Swiggy",
        "role_title": "Software Development Engineer 2",
        "candidate_name": "Arjun Sharma",
        "email": "arjun.sharma@example.com",
        "linkedin_url": "https://linkedin.com/in/arjun-sharma-dev",
        "yoe": 3.5,
        "current_ctc_lpa": 24.0,
        "expected_ctc_lpa": 38.0,
        "notice_period_days": 30,
        "resume_url": "https://drive.google.com/file/d/sample-resume",
    }

    # 1. Submit lead
    res = client.post("/api/leads/submit", json=lead_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "lead_id" in data
    assert "Arjun Sharma" in data["referral_pitch"]
    assert "Swiggy" in data["referral_pitch"]
    assert "Software Development Engineer 2" in data["referral_pitch"]
    assert "3.5 years" in data["referral_pitch"]

    # 2. Query leads list
    res_list = client.get("/api/leads?company=Swiggy")
    assert res_list.status_code == 200
    list_data = res_list.json()
    assert list_data["total"] >= 1
    found = any(l["id"] == data["lead_id"] for l in list_data["leads"])
    assert found is True


def test_lead_validation():
    # Negative YoE should fail
    bad_payload = {
        "job_id": "job_001",
        "company": "CRED",
        "role_title": "Backend Engineer",
        "candidate_name": "A", # too short
        "email": "not-an-email",
        "yoe": -2,
    }
    res = client.post("/api/leads/submit", json=bad_payload)
    assert res.status_code == 422


def test_referral_pitch_endpoint():
    pitch_req = {
        "candidate_name": "Priya Patel",
        "company": "Meesho",
        "role_title": "Senior Product Manager",
        "job_apply_url": "https://jobs.lever.co/meesho/xyz",
        "yoe": 6.0,
        "linkedin_url": "https://linkedin.com/in/priyapatel",
    }
    res = client.post("/api/leads/pitch", json=pitch_req)
    assert res.status_code == 200
    pitch = res.json()["pitch"]
    assert "Priya Patel" in pitch
    assert "Senior Product Manager" in pitch
    assert "Meesho" in pitch
    assert "6.0 years" in pitch

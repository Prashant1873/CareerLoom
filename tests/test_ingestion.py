import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.models.job import JobItem
from backend.app.utils.date_parser import parse_posting_date, format_relative_date
from backend.app.utils.classifier import classify_role, parse_location


def test_date_parser_iso():
    dt = parse_posting_date("2026-03-25T14:30:00Z")
    assert dt.year == 2026
    assert dt.month == 3
    assert dt.day == 25
    assert dt.tzinfo is not None


def test_date_parser_epoch_ms():
    # 1711627200000 -> 2024-03-28
    dt = parse_posting_date(1711627200000)
    assert dt.year == 2024
    assert dt.tzinfo is not None


def test_date_parser_relative():
    dt = parse_posting_date("2 days ago")
    rel = format_relative_date(dt)
    assert "2d ago" in rel or "Yesterday" in rel or "d ago" in rel


def test_role_classifier():
    cat, sen = classify_role("Senior Product Manager - Growth")
    assert cat == "product"
    assert sen == "senior"

    cat, sen = classify_role("Associate Machine Learning Engineer")
    assert cat == "data_ai"
    assert sen == "entry"

    cat, sen = classify_role("Software Engineering Intern")
    assert cat == "software_engineering"
    assert sen == "intern"


def test_location_parser():
    loc, country, is_remote = parse_location("San Francisco, CA (Remote)")
    assert country == "United States"
    assert is_remote is True

    loc, country, is_remote = parse_location("London, UK")
    assert country == "United Kingdom"
    assert is_remote is False


def test_api_health():
    client = TestClient(app)
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_api_companies_list():
    client = TestClient(app)
    res = client.get("/api/jobs/companies")
    assert res.status_code == 200
    assert res.json()["total"] >= 50


def test_api_jobs_query():
    client = TestClient(app)
    res = client.get("/api/jobs?limit=5")
    assert res.status_code == 200
    data = res.json()
    assert "total" in data
    assert "jobs" in data

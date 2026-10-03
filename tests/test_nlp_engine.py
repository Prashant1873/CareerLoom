import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.llm_adapter import HeuristicQueryParser, parse_natural_language_query
from backend.app.services.taxonomy import match_category_phrase, get_all_categories
from backend.app.utils.query_cache import QueryCache, query_cache


def test_query_cache_hit_and_normalization():
    cache = QueryCache(max_size=10, ttl_seconds=60)
    cache.set("Junior Product Manager in UK", {"category": "product"})
    
    # Normalized lookup (case insensitivity and extra spaces)
    res = cache.get("junior   product manager in uk")
    assert res is not None
    assert res["category"] == "product"


def test_heuristic_parser_product_entry():
    parser = HeuristicQueryParser()
    res = parser.parse("Looking for product entry level roles in London or remote")
    assert res["category"] == "product"
    assert res["seniority"] == "entry"
    assert res["is_remote"] is True
    assert res["country"] == "United Kingdom"


def test_heuristic_parser_data_ai():
    parser = HeuristicQueryParser()
    res = parser.parse("machine learning engineer new grad in US posted this week")
    assert res["category"] == "data_ai"
    assert res["seniority"] == "entry"
    assert res["country"] == "United States"
    assert res["posted_within_days"] == 7


def test_heuristic_parser_tech_keywords():
    parser = HeuristicQueryParser()
    res = parser.parse("python backend developer in Germany")
    assert res["category"] == "software_engineering"
    assert res["country"] == "Germany"
    assert res["search_terms"] == "python"


def test_taxonomy_matching():
    match = match_category_phrase("Product Entry Level")
    assert match is not None
    assert match["category"] == "product"
    assert match["seniority"] == "entry"

    match_ml = match_category_phrase("junior machine learning")
    assert match_ml is not None
    assert match_ml["category"] == "data_ai"
    assert match_ml["seniority"] == "entry"


def test_api_categories():
    client = TestClient(app)
    res = client.get("/api/categories")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 7
    categories_ids = [c["id"] for c in data["categories"]]
    assert "product" in categories_ids
    assert "software_engineering" in categories_ids
    assert "data_ai" in categories_ids


def test_api_discovery_tracks():
    client = TestClient(app)
    res = client.get("/api/categories/tracks")
    assert res.status_code == 200
    tracks = res.json()["tracks"]
    assert len(tracks) >= 30
    track_names = [t["track"] for t in tracks]
    assert "Product Entry Level" in track_names


def test_api_nlp_parse_endpoint():
    client = TestClient(app)
    res = client.post("/api/nlp/parse", json={"prompt": "Associate Product Manager in Europe"})
    assert res.status_code == 200
    data = res.json()
    assert data["category_label"] == "Product Management"
    assert data["parsed_parameters"]["category"] == "product"
    assert data["parsed_parameters"]["seniority"] == "entry"


def test_api_nlp_search_endpoint():
    client = TestClient(app)
    res = client.post("/api/nlp/search", json={"prompt": "Software Engineer"})
    assert res.status_code == 200
    data = res.json()
    assert "total" in data
    assert "jobs" in data
    assert isinstance(data["jobs"], list)


def test_api_jobs_sorting_and_filtering():
    client = TestClient(app)
    
    # Sort by date
    res_date = client.get("/api/jobs?sort_by=date&limit=5")
    assert res_date.status_code == 200
    jobs = res_date.json()["jobs"]
    if len(jobs) >= 2:
        assert jobs[0]["date_posted"] >= jobs[1]["date_posted"]

    # Filter by region (Europe)
    res_eu = client.get("/api/jobs?country=Europe&limit=5")
    assert res_eu.status_code == 200

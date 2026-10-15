import pytest
from datetime import datetime, timezone
from backend.app.services.taxonomy import (
    CATEGORIES_TAXONOMY,
    CATEGORY_CLUSTERS,
    get_all_categories,
    get_all_clusters,
    get_categories_in_cluster,
    resolve_category_or_cluster,
    match_category_phrase,
)
from backend.app.utils.classifier import classify_role
from backend.app.models.job import JobItem, JobFilterParams


def test_categories_taxonomy_structure():
    # Verify all 6 granular categories exist
    expected_categories = [
        "product",
        "technical_product",
        "product_ops",
        "management_consulting",
        "corporate_strategy",
        "founders_office",
    ]
    for cat_id in expected_categories:
        assert cat_id in CATEGORIES_TAXONOMY
        meta = CATEGORIES_TAXONOMY[cat_id]
        assert "label" in meta
        assert "cluster" in meta
        assert "curated_tracks" in meta
        assert "synonyms" in meta
        assert len(meta["curated_tracks"]) > 0

    # Verify clusters exist
    assert "product_cluster" in CATEGORY_CLUSTERS
    assert "strategy_cluster" in CATEGORY_CLUSTERS

    prod_cats = get_categories_in_cluster("product_cluster")
    assert "product" in prod_cats
    assert "technical_product" in prod_cats
    assert "product_ops" in prod_cats

    strat_cats = get_categories_in_cluster("strategy_cluster")
    assert "management_consulting" in strat_cats
    assert "corporate_strategy" in strat_cats
    assert "founders_office" in strat_cats


def test_cluster_resolution():
    assert resolve_category_or_cluster("product") == ["product", "technical_product", "product_ops"]
    assert resolve_category_or_cluster("product_cluster") == ["product", "technical_product", "product_ops"]
    assert resolve_category_or_cluster("strategy") == ["management_consulting", "corporate_strategy", "founders_office"]
    assert resolve_category_or_cluster("founders_office") == ["founders_office"]


def test_classifier_pm_tracks():
    # APM
    cat, sen, track = classify_role("Associate Product Manager")
    assert cat == "product"
    assert sen == "entry"
    assert track == "Associate Product Manager (APM)"

    # Senior PM
    cat, sen, track = classify_role("Senior Product Manager")
    assert cat == "product"
    assert sen == "senior"
    assert track == "Senior Product Manager"

    # Technical PM / TPM
    cat, sen, track = classify_role("Technical Product Manager")
    assert cat == "technical_product"
    assert track == "Technical Product Manager (TPM)"

    cat, sen, track = classify_role("Principal TPM")
    assert cat == "technical_product"
    assert sen == "lead"
    assert track == "Principal TPM"

    # Product Operations
    cat, sen, track = classify_role("Product Operations Manager")
    assert cat == "product_ops"
    assert track == "Product Operations Manager"

    # Executive PM
    cat, sen, track = classify_role("VP of Product")
    assert cat == "product"
    assert sen == "lead"
    assert track == "Director / VP Product"


def test_classifier_strategy_tracks():
    # Chief of Staff
    cat, sen, track = classify_role("Chief of Staff")
    assert cat == "founders_office"
    assert sen == "lead"
    assert track == "Chief of Staff"

    # Founder's Office Associate
    cat, sen, track = classify_role("Founder's Office Associate")
    assert cat == "founders_office"
    assert sen == "entry"
    assert track == "Founder's Office Associate"

    # Management Consultant
    cat, sen, track = classify_role("Management Consultant")
    assert cat == "management_consulting"
    assert track == "Management Consultant"

    # Corporate Strategy
    cat, sen, track = classify_role("Corporate Strategy Analyst")
    assert cat == "corporate_strategy"
    assert sen == "entry"
    assert track == "Corporate Strategy Analyst"

    # BizOps
    cat, sen, track = classify_role("Business Operations Manager")
    assert cat == "founders_office"
    assert track == "Business Operations (BizOps) Manager"


def test_consulting_hints():
    # McKinsey Associate -> management_consulting
    cat, sen, track = classify_role("Associate", company="McKinsey & Company")
    assert cat == "management_consulting"
    assert sen == "entry"
    assert track == "Associate Consultant"

    # Bain Business Analyst -> management_consulting
    cat, sen, track = classify_role("Business Analyst", company="Bain & Company")
    assert cat == "management_consulting"
    assert sen == "entry"
    assert track == "Management Consultant"

    # Non-consulting firm Business Analyst -> general
    cat, sen, track = classify_role("Business Analyst", company="Swiggy")
    assert cat == "general"


def test_collision_precedence():
    # Founder's Office > Product
    cat, sen, track = classify_role("Founder's Office - Product & Strategy")
    assert cat == "founders_office"

    # Technical Product > Product
    cat, sen, track = classify_role("Technical Product Manager - Mobile")
    assert cat == "technical_product"

    # Product Ops > Product
    cat, sen, track = classify_role("Product Operations Manager - Core Product")
    assert cat == "product_ops"


def test_job_model_track():
    now = datetime.now(timezone.utc)
    job = JobItem.create(
        title="Chief of Staff",
        company="Razorpay",
        apply_url="https://razorpay.com/jobs/cos",
        date_posted=now,
        source="ashby",
        category="founders_office",
        track="Chief of Staff",
        seniority="lead",
    )
    assert job.track == "Chief of Staff"
    assert job.category == "founders_office"
    data = job.model_dump()
    assert data["track"] == "Chief of Staff"

    params = JobFilterParams(track="Chief of Staff", cluster="strategy_cluster")
    assert params.track == "Chief of Staff"
    assert params.cluster == "strategy_cluster"


def test_match_category_phrase():
    match = match_category_phrase("Associate Product Manager (APM)")
    assert match is not None
    assert match["category"] == "product"
    assert match["matched_track"] == "Associate Product Manager (APM)"
    assert match["cluster"] == "product_cluster"

    match2 = match_category_phrase("Chief of Staff")
    assert match2 is not None
    assert match2["category"] == "founders_office"
    assert match2["cluster"] == "strategy_cluster"

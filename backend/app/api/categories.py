from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.services.taxonomy import (
    get_all_categories,
    get_category_by_id,
    match_category_phrase,
)

router = APIRouter(prefix="/api/categories", tags=["Categories"])


class CategoryResponse(BaseModel):
    id: str
    label: str
    description: str
    icon: str
    curated_tracks: List[str]
    related_skills: List[str]


class CategoriesListResponse(BaseModel):
    total: int
    categories: List[CategoryResponse]


@router.get("", response_model=CategoriesListResponse)
async def list_categories():
    """
    Returns full catalog of canonical job role categories and discovery tracks.
    Used for category navigation and search pill suggestions.
    """
    cats = get_all_categories()
    return CategoriesListResponse(
        total=len(cats),
        categories=[
            CategoryResponse(
                id=c["id"],
                label=c["label"],
                description=c["description"],
                icon=c["icon"],
                curated_tracks=c["curated_tracks"],
                related_skills=c["related_skills"],
            )
            for c in cats
        ],
    )


@router.get("/tracks")
async def list_discovery_tracks():
    """
    Returns flat list of curated discovery tracks for quick-pill exploration
    (e.g., 'Product Entry Level', 'Junior Machine Learning Engineer', 'SWE New Grad').
    """
    cats = get_all_categories()
    tracks = []
    for c in cats:
        for t in c["curated_tracks"]:
            tracks.append({
                "track": t,
                "category_id": c["id"],
                "category_label": c["label"],
            })
    return {"total": len(tracks), "tracks": tracks}


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: str):
    """
    Returns detailed metadata for a single canonical category.
    """
    cat = get_category_by_id(category_id)
    if not cat:
        raise HTTPException(status_code=404, detail=f"Category '{category_id}' not found")
    return CategoryResponse(
        id=cat["id"],
        label=cat["label"],
        description=cat["description"],
        icon=cat["icon"],
        curated_tracks=cat["curated_tracks"],
        related_skills=cat["related_skills"],
    )

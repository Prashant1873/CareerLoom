import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.app.db.database import query_jobs
from backend.app.models.job import JobFilterParams, JobItem
from backend.app.services.llm_adapter import parse_natural_language_query
from backend.app.services.taxonomy import match_category_phrase

logger = logging.getLogger("careerloom.api.nlp")
router = APIRouter(prefix="/api/nlp", tags=["Natural Language Search"])


class NLPPromptRequest(BaseModel):
    prompt: str = Field(..., description="Freeform conversational search prompt (e.g. 'entry level product manager in Europe or remote')")


class NLPSearchRequest(BaseModel):
    prompt: str = Field(..., description="Freeform conversational search prompt")
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="date", description="Sort order: 'date' (newest first), 'company', or 'title'")


class NLPParseResponse(BaseModel):
    prompt: str
    parsed_parameters: Dict[str, Any]
    matched_track: Optional[str] = None
    category_label: Optional[str] = None


class NLPSearchResponse(BaseModel):
    prompt: str
    parsed_parameters: Dict[str, Any]
    matched_track: Optional[str] = None
    category_label: Optional[str] = None
    total: int
    limit: int
    offset: int
    jobs: List[JobItem]


@router.post("/parse", response_model=NLPParseResponse)
async def parse_prompt(req: NLPPromptRequest):
    """
    Parses a natural language prompt into structured search parameters.
    Uses free online LLMs (Groq / Gemini) with seamless offline heuristic fallback.
    """
    parsed = await parse_natural_language_query(req.prompt)

    # Check taxonomy for track match
    matched_track = None
    category_label = None
    tax_match = match_category_phrase(req.prompt)
    if tax_match:
        matched_track = tax_match.get("matched_track")
        category_label = tax_match.get("label")
        if not parsed.get("category"):
            parsed["category"] = tax_match.get("category")
        if not parsed.get("seniority") and tax_match.get("seniority"):
            parsed["seniority"] = tax_match.get("seniority")

    return NLPParseResponse(
        prompt=req.prompt,
        parsed_parameters=parsed,
        matched_track=matched_track,
        category_label=category_label,
    )


@router.post("/search", response_model=NLPSearchResponse)
async def search_with_natural_language(req: NLPSearchRequest):
    """
    Unified conversational search: translates freeform natural language queries
    into structured database parameters and returns ranked, verified job cards.
    """
    parsed = await parse_natural_language_query(req.prompt)

    matched_track = None
    category_label = None
    tax_match = match_category_phrase(req.prompt)
    if tax_match:
        matched_track = tax_match.get("matched_track")
        category_label = tax_match.get("label")
        if not parsed.get("category"):
            parsed["category"] = tax_match.get("category")
        if not parsed.get("seniority") and tax_match.get("seniority"):
            parsed["seniority"] = tax_match.get("seniority")

    filter_params = JobFilterParams(
        search=parsed.get("search_terms"),
        category=parsed.get("category"),
        seniority=parsed.get("seniority"),
        country=parsed.get("country"),
        is_remote=parsed.get("is_remote"),
        domain=parsed.get("domain"),
        posted_within_days=parsed.get("posted_within_days"),
        sort_by=req.sort_by,
        limit=req.limit,
        offset=req.offset,
    )

    jobs, total = await query_jobs(filter_params)

    # If strict combination returned 0 jobs but category was matched, retry without strict search_terms
    if total == 0 and parsed.get("search_terms") and parsed.get("category"):
        fallback_params = JobFilterParams(
            search=None,
            category=parsed.get("category"),
            seniority=parsed.get("seniority"),
            country=parsed.get("country"),
            is_remote=parsed.get("is_remote"),
            domain=parsed.get("domain"),
            posted_within_days=parsed.get("posted_within_days"),
            sort_by=req.sort_by,
            limit=req.limit,
            offset=req.offset,
        )
        jobs, total = await query_jobs(fallback_params)

    return NLPSearchResponse(
        prompt=req.prompt,
        parsed_parameters=parsed,
        matched_track=matched_track,
        category_label=category_label,
        total=total,
        limit=req.limit,
        offset=req.offset,
        jobs=jobs,
    )

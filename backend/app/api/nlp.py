import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.app.db.database import query_jobs
from backend.app.models.job import JobFilterParams, JobItem
from backend.app.services.llm_adapter import parse_natural_language_query
from backend.app.services.taxonomy import match_category_phrase
from backend.app.utils.classifier import get_indian_metro_hub, parse_location

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
    Executes sub-20ms fast-path taxonomy match, falling back to LLM for ambiguous queries.
    """
    tax_match = match_category_phrase(req.prompt)
    if tax_match:
        _, country, is_remote = parse_location(req.prompt, "")
        metro_hub = get_indian_metro_hub(req.prompt) or None
        clean_country = country if country not in ("Global", "Remote / Global") else None

        parsed = {
            "category": tax_match.get("category"),
            "track": tax_match.get("matched_track"),
            "cluster": tax_match.get("cluster"),
            "seniority": tax_match.get("seniority"),
            "country": clean_country,
            "is_remote": True if is_remote else None,
            "metro_hub": metro_hub,
            "search_terms": None,
        }
        return NLPParseResponse(
            prompt=req.prompt,
            parsed_parameters=parsed,
            matched_track=tax_match.get("matched_track"),
            category_label=tax_match.get("label"),
        )

    # Fallback to LLM query parser
    parsed = await parse_natural_language_query(req.prompt)
    return NLPParseResponse(
        prompt=req.prompt,
        parsed_parameters=parsed,
        matched_track=None,
        category_label=None,
    )


@router.post("/search", response_model=NLPSearchResponse)
async def search_with_natural_language(req: NLPSearchRequest):
    """
    Unified conversational search: translates freeform natural language queries
    into structured database parameters and returns ranked, verified job cards.
    Leverages sub-20ms fast-path before LLM fallback.
    """
    tax_match = match_category_phrase(req.prompt)
    if tax_match:
        _, country, is_remote = parse_location(req.prompt, "")
        metro_hub = get_indian_metro_hub(req.prompt) or None
        clean_country = country if country not in ("Global", "Remote / Global") else None

        parsed = {
            "category": tax_match.get("category"),
            "track": tax_match.get("matched_track"),
            "cluster": tax_match.get("cluster"),
            "seniority": tax_match.get("seniority"),
            "country": clean_country,
            "is_remote": True if is_remote else None,
            "metro_hub": metro_hub,
            "search_terms": None,
        }
        filter_params = JobFilterParams(
            search=None,
            category=parsed.get("category"),
            track=parsed.get("track"),
            seniority=parsed.get("seniority"),
            country=parsed.get("country"),
            metro_hub=parsed.get("metro_hub"),
            is_remote=parsed.get("is_remote"),
            sort_by=req.sort_by,
            limit=req.limit,
            offset=req.offset,
        )
        jobs, total = await query_jobs(filter_params)
        if total > 0:
            return NLPSearchResponse(
                prompt=req.prompt,
                parsed_parameters=parsed,
                matched_track=tax_match.get("matched_track"),
                category_label=tax_match.get("label"),
                total=total,
                limit=req.limit,
                offset=req.offset,
                jobs=jobs,
            )

    # Fallback to LLM adapter
    parsed = await parse_natural_language_query(req.prompt)

    matched_track = None
    category_label = None
    if tax_match:
        matched_track = tax_match.get("matched_track")
        category_label = tax_match.get("label")
        if not parsed.get("category"):
            parsed["category"] = tax_match.get("category")
        if not parsed.get("track"):
            parsed["track"] = tax_match.get("matched_track")
        if not parsed.get("seniority") and tax_match.get("seniority"):
            parsed["seniority"] = tax_match.get("seniority")

    filter_params = JobFilterParams(
        search=parsed.get("search_terms"),
        category=parsed.get("category"),
        track=parsed.get("track"),
        seniority=parsed.get("seniority"),
        country=parsed.get("country"),
        metro_hub=parsed.get("metro_hub"),
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
            track=parsed.get("track"),
            seniority=parsed.get("seniority"),
            country=parsed.get("country"),
            metro_hub=parsed.get("metro_hub"),
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

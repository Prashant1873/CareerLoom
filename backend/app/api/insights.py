import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel

from backend.app.services.reddit import get_reddit_service

logger = logging.getLogger("careerloom.api.insights")
router = APIRouter(prefix="/api/insights", tags=["Community Insights"])


class RedditThreadItem(BaseModel):
    title: str
    url: str
    score: int
    num_comments: int
    author: str
    subreddit: str


class CommunityInsightsResponse(BaseModel):
    company: str
    role: str
    subreddit: str
    turnaround_estimate: str
    interview_stages: List[str]
    insider_tips: List[str]
    sentiment_summary: str
    threads: List[RedditThreadItem]
    last_updated: str


@router.get("/company", response_model=CommunityInsightsResponse)
async def get_company_insights(
    company: str = Query(..., description="Target employer name (e.g. 'Stripe', 'Figma', 'McKinsey & Company')"),
    role: Optional[str] = Query(None, description="Optional role context (e.g. 'Software Engineer', 'Product Manager')"),
    domain: Optional[str] = Query("tech", description="Domain context for subreddit routing (e.g. 'tech', 'product', 'finance', 'consulting')"),
):
    """
    Returns authentic interview timelines, round breakdowns, insider advice,
    and public Reddit discussion threads for a specific employer.
    """
    reddit_service = get_reddit_service()
    insights = await reddit_service.fetch_community_insights(
        company=company,
        role=role,
        domain=domain,
    )
    return insights

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.app.db.database import get_leads, insert_lead
from backend.app.models.lead import CandidateLead, CandidateLeadCreate

logger = logging.getLogger("careerloom.api.leads")
router = APIRouter(prefix="/api/leads", tags=["Candidate Leads & Referrals"])


class ReferralPitchRequest(BaseModel):
    candidate_name: str
    company: str
    role_title: str
    job_apply_url: Optional[str] = None
    yoe: float
    current_company: Optional[str] = None
    key_skills: Optional[str] = None
    linkedin_url: Optional[str] = None
    resume_url: Optional[str] = None


class LeadSubmitResponse(BaseModel):
    success: bool
    lead_id: str
    message: str
    referral_pitch: str
    lead: CandidateLead


class LeadsListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    leads: List[CandidateLead]


def generate_referral_pitch(
    name: str,
    company: str,
    role: str,
    yoe: float,
    apply_url: Optional[str] = None,
    linkedin_url: Optional[str] = None,
    resume_url: Optional[str] = None,
    current_ctc_lpa: Optional[float] = None,
    notice_period_days: Optional[int] = None,
) -> str:
    """
    Generates a concise, high-converting referral request message
    tailored for Indian tech professionals on LinkedIn and WhatsApp.
    """
    notice_str = f"{notice_period_days} days" if notice_period_days else "30 days"
    if notice_period_days == 0:
        notice_str = "Immediate joiner (0 days notice)"

    lines = [
        f"Hi [Name],",
        f"",
        f"Hope you are doing well! I came across the {role} position open at {company} and would love to be considered.",
        f"",
        f"A quick snapshot of my profile:",
        f"• Experience: {yoe:.1f} years in tech",
        f"• Notice Period: {notice_str}",
    ]

    if linkedin_url:
        lines.append(f"• LinkedIn: {linkedin_url}")
    if resume_url:
        lines.append(f"• Resume: {resume_url}")
    if apply_url:
        lines.append(f"• Requisition Link: {apply_url}")

    lines.extend([
        f"",
        f"If you find my profile relevant, would you be open to putting in an internal referral for me? Happy to share my updated CV or any additional details.",
        f"",
        f"Thank you so much for your time and help!",
        f"Best regards,",
        f"{name}",
    ])

    return "\n".join(lines)


@router.post("/submit", response_model=LeadSubmitResponse)
async def submit_lead(payload: CandidateLeadCreate):
    """
    Submits a candidate lead seeking a referral or interview pipeline entry.
    Validates input, records to SQLite, and returns a high-conversion referral message.
    """
    try:
        lead = CandidateLead(
            job_id=payload.job_id,
            company=payload.company,
            role_title=payload.role_title,
            candidate_name=payload.candidate_name,
            email=payload.email,
            linkedin_url=payload.linkedin_url,
            yoe=payload.yoe,
            current_ctc_lpa=payload.current_ctc_lpa,
            expected_ctc_lpa=payload.expected_ctc_lpa,
            notice_period_days=payload.notice_period_days,
            resume_url=payload.resume_url,
            status="new",
        )

        lead_id = await insert_lead(lead)

        pitch = generate_referral_pitch(
            name=lead.candidate_name,
            company=lead.company,
            role=lead.role_title,
            yoe=lead.yoe,
            linkedin_url=lead.linkedin_url,
            resume_url=lead.resume_url,
            current_ctc_lpa=lead.current_ctc_lpa,
            notice_period_days=lead.notice_period_days,
        )

        return LeadSubmitResponse(
            success=True,
            lead_id=lead_id,
            message="Lead registered successfully. Your tailored referral pitch is ready to share!",
            referral_pitch=pitch,
            lead=lead,
        )
    except Exception as e:
        logger.error(f"Failed to submit lead: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to record lead: {str(e)}")


@router.get("", response_model=LeadsListResponse)
async def list_leads(
    company: Optional[str] = Query(None, description="Filter by employer company"),
    status: Optional[str] = Query(None, description="Filter by lead status (new, referred, reviewing, contacted)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """
    Retrieves recorded candidate leads with pagination and optional filtering.
    """
    leads, total = await get_leads(company=company, status=status, limit=limit, offset=offset)
    return LeadsListResponse(
        total=total,
        limit=limit,
        offset=offset,
        leads=leads,
    )


@router.post("/pitch")
async def generate_pitch_endpoint(req: ReferralPitchRequest):
    """
    Generates a high-converting referral pitch without requiring lead persistence.
    """
    pitch = generate_referral_pitch(
        name=req.candidate_name,
        company=req.company,
        role=req.role_title,
        yoe=req.yoe,
        apply_url=req.job_apply_url,
        linkedin_url=req.linkedin_url,
        resume_url=req.resume_url,
    )
    return {"pitch": pitch}

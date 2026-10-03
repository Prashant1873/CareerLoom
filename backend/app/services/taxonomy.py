import re
from typing import Any, Dict, List, Optional


CATEGORIES_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "product": {
        "id": "product",
        "label": "Product Management",
        "description": "Product discovery, strategy, feature delivery, and user lifecycle optimization",
        "icon": "Package",
        "curated_tracks": [
            "Product Entry Level",
            "Associate Product Manager (APM)",
            "Technical Product Manager",
            "Growth Product Manager",
            "AI Product Manager",
        ],
        "synonyms": [
            "product manager",
            "product management",
            "pm",
            "apm",
            "technical product manager",
            "group product manager",
            "product owner",
            "product lead",
        ],
        "related_skills": ["Roadmap Strategy", "User Research", "Metrics & KPIs", "A/B Testing", "Agile"],
    },
    "software_engineering": {
        "id": "software_engineering",
        "label": "Software Engineering",
        "description": "Full stack, backend, frontend, infrastructure, and distributed systems",
        "icon": "Code",
        "curated_tracks": [
            "SWE New Grad",
            "Backend Systems Engineer",
            "Frontend React Engineer",
            "Founding Engineer (Remote)",
            "Cloud Infrastructure / DevOps",
        ],
        "synonyms": [
            "software engineer",
            "software developer",
            "swe",
            "backend engineer",
            "frontend engineer",
            "full stack engineer",
            "full-stack developer",
            "devops engineer",
            "site reliability engineer",
            "sre",
            "cloud engineer",
            "infrastructure engineer",
            "systems engineer",
            "firmware engineer",
        ],
        "related_skills": ["Python", "TypeScript", "Go", "React", "Distributed Systems", "PostgreSQL", "Docker", "Kubernetes"],
    },
    "data_ai": {
        "id": "data_ai",
        "label": "AI & Data Science",
        "description": "Machine learning, LLM systems, computer vision, data engineering, and AI research",
        "icon": "Cpu",
        "curated_tracks": [
            "Junior Machine Learning Engineer",
            "AI Researcher",
            "Data Scientist (New Grad)",
            "MLOps / AI Platform Engineer",
            "Computer Vision Specialist",
        ],
        "synonyms": [
            "machine learning engineer",
            "ml engineer",
            "ai engineer",
            "ai researcher",
            "data scientist",
            "data science",
            "data engineer",
            "deep learning engineer",
            "nlp engineer",
            "computer vision engineer",
            "mlops engineer",
            "llm engineer",
        ],
        "related_skills": ["PyTorch", "Transformers", "LLMs", "Vector Databases", "MLOps", "Pandas", "Scikit-Learn"],
    },
    "design": {
        "id": "design",
        "label": "Design & UX",
        "description": "Product design, user experience research, design systems, and interaction design",
        "icon": "Palette",
        "curated_tracks": [
            "Product Designer (Entry Level)",
            "UI/UX Designer",
            "Design Systems Engineer",
            "Interaction Designer",
            "Brand & Motion Designer",
        ],
        "synonyms": [
            "product designer",
            "ui/ux designer",
            "ux designer",
            "ui designer",
            "interaction designer",
            "ux researcher",
            "design systems designer",
            "graphic designer",
        ],
        "related_skills": ["Figma", "Design Systems", "Prototyping", "User Testing", "Visual Hierarchy"],
    },
    "finance_quant": {
        "id": "finance_quant",
        "label": "Quantitative & Finance",
        "description": "Quantitative trading, algorithmic research, risk modeling, and financial analytics",
        "icon": "TrendingUp",
        "curated_tracks": [
            "Quantitative Trader (New Grad)",
            "Quantitative Research Analyst",
            "Risk Modeling Analyst",
            "Fintech Investment Analyst",
        ],
        "synonyms": [
            "quantitative trader",
            "quant trader",
            "quantitative researcher",
            "quant researcher",
            "algorithmic trader",
            "risk analyst",
            "financial analyst",
            "portfolio manager",
        ],
        "related_skills": ["C++", "Python", "Stochastic Calculus", "Time Series", "Derivatives", "Risk Modeling"],
    },
    "consulting_strategy": {
        "id": "consulting_strategy",
        "label": "Strategy & Consulting",
        "description": "Management consulting, business operations, strategy, and Chief of Staff roles",
        "icon": "Briefcase",
        "curated_tracks": [
            "Management Consulting Associate",
            "Business Operations (BizOps)",
            "Chief of Staff",
            "Corporate Strategy Analyst",
        ],
        "synonyms": [
            "management consultant",
            "consultant",
            "strategy analyst",
            "business operations",
            "bizops",
            "chief of staff",
            "corporate strategy",
            "operations associate",
        ],
        "related_skills": ["Financial Modeling", "Market Analysis", "Executive Communication", "Process Optimization"],
    },
    "sales_gtm": {
        "id": "sales_gtm",
        "label": "Sales & Go-to-Market",
        "description": "Technical sales, solutions architecture, account executive, and business development",
        "icon": "Target",
        "curated_tracks": [
            "Sales Engineer",
            "Enterprise Account Executive",
            "Business Development Representative (BDR)",
            "Solutions Architect",
        ],
        "synonyms": [
            "account executive",
            "sales engineer",
            "solutions architect",
            "business development representative",
            "bdr",
            "sdr",
            "gtm lead",
        ],
        "related_skills": ["Enterprise Sales", "Technical Demos", "Pipeline Generation", "Customer Discovery"],
    },
    "marketing": {
        "id": "marketing",
        "label": "Growth & Marketing",
        "description": "Growth marketing, developer relations, product marketing, and content strategy",
        "icon": "Megaphone",
        "curated_tracks": [
            "Growth Marketing Associate",
            "Developer Relations / Advocate",
            "Product Marketing Manager (PMM)",
            "Technical Content Strategist",
        ],
        "synonyms": [
            "growth marketer",
            "product marketing manager",
            "pmm",
            "developer advocate",
            "developer relations",
            "devrel",
            "content strategist",
        ],
        "related_skills": ["SEO", "Content Marketing", "Developer Advocacy", "Conversion Rate Optimization"],
    },
}


def get_all_categories() -> List[Dict[str, Any]]:
    """
    Returns list of all categories with their display labels, descriptions, and curated tracks.
    """
    return list(CATEGORIES_TAXONOMY.values())


def get_category_by_id(cat_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetches category metadata by ID.
    """
    return CATEGORIES_TAXONOMY.get(cat_id.strip().lower())


def match_category_phrase(phrase: str) -> Optional[Dict[str, Any]]:
    """
    Maps conversational role track phrases (e.g. "product entry level", "junior machine learning", "swe new grad")
    into canonical category, inferred seniority, and matching title synonyms.
    """
    p = phrase.strip().lower()

    # Detect seniority
    seniority = None
    if re.search(r"\b(entry level|entry-level|junior|jr|new grad|new graduate|fresh grad|associate|early career)\b", p):
        seniority = "entry"
    elif re.search(r"\b(intern|internship|co-op|coop)\b", p):
        seniority = "intern"
    elif re.search(r"\b(lead|principal|staff|director|head of)\b", p):
        seniority = "lead"
    elif re.search(r"\b(senior|sr|sr\.)\b", p):
        seniority = "senior"

    # Match category
    for cat_id, meta in CATEGORIES_TAXONOMY.items():
        # 1. Direct curated track match
        for track in meta["curated_tracks"]:
            if track.lower() in p or p in track.lower():
                return {
                    "category": cat_id,
                    "seniority": seniority or ("entry" if "entry" in track.lower() or "grad" in track.lower() or "junior" in track.lower() else None),
                    "label": meta["label"],
                    "synonyms": meta["synonyms"],
                    "matched_track": track,
                }

        # 2. Synonym match
        for syn in meta["synonyms"]:
            if re.search(rf"\b{re.escape(syn)}\b", p):
                return {
                    "category": cat_id,
                    "seniority": seniority,
                    "label": meta["label"],
                    "synonyms": meta["synonyms"],
                    "matched_track": None,
                }

    return None

import re
from typing import Any, Dict, List, Optional


CATEGORY_CLUSTERS: Dict[str, Dict[str, Any]] = {
    "product_cluster": {
        "id": "product_cluster",
        "label": "Product & Technical Leadership",
        "description": "Product management, technical product direction, and product operations",
        "icon": "Package",
        "categories": ["product", "technical_product", "product_ops"],
    },
    "strategy_cluster": {
        "id": "strategy_cluster",
        "label": "Strategy, Consulting & Founder's Office",
        "description": "Management consulting, corporate strategy, executive operations, and Chief of Staff",
        "icon": "Briefcase",
        "categories": ["management_consulting", "corporate_strategy", "founders_office"],
    },
    "engineering_cluster": {
        "id": "engineering_cluster",
        "label": "Engineering & Technology",
        "description": "Full stack, backend, frontend, infrastructure, and distributed systems",
        "icon": "Code",
        "categories": ["software_engineering"],
    },
    "data_cluster": {
        "id": "data_cluster",
        "label": "Data & Artificial Intelligence",
        "description": "Machine learning, AI research, computer vision, data engineering, and data science",
        "icon": "Cpu",
        "categories": ["data_ai"],
    },
    "design_cluster": {
        "id": "design_cluster",
        "label": "Design & User Experience",
        "description": "Product design, UI/UX, interaction design, and design systems",
        "icon": "Palette",
        "categories": ["design"],
    },
    "finance_cluster": {
        "id": "finance_cluster",
        "label": "Quantitative & Finance",
        "description": "Quantitative trading, algorithmic research, risk modeling, and financial analytics",
        "icon": "TrendingUp",
        "categories": ["finance_quant"],
    },
    "sales_cluster": {
        "id": "sales_cluster",
        "label": "Sales & Go-to-Market",
        "description": "Technical sales, solutions architecture, account executive, and business development",
        "icon": "Target",
        "categories": ["sales_gtm"],
    },
    "marketing_cluster": {
        "id": "marketing_cluster",
        "label": "Growth & Marketing",
        "description": "Growth marketing, developer relations, product marketing, and content strategy",
        "icon": "Megaphone",
        "categories": ["marketing"],
    },
}


CATEGORIES_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "product": {
        "id": "product",
        "cluster": "product_cluster",
        "label": "Product Management",
        "description": "Product discovery, roadmap strategy, feature delivery, and user lifecycle optimization",
        "icon": "Package",
        "curated_tracks": [
            "Associate Product Manager (APM)",
            "Product Manager",
            "Senior Product Manager",
            "Group Product Manager (GPM)",
            "Director / VP Product",
            "Growth Product Manager",
            "AI Product Manager",
        ],
        "synonyms": [
            "product",
            "product entry level",
            "product manager",
            "product management",
            "pm",
            "apm",
            "associate product manager",
            "senior product manager",
            "sr pm",
            "group product manager",
            "gpm",
            "principal product manager",
            "director of product",
            "vp product",
            "vp of product",
            "head of product",
            "growth product manager",
            "ai product manager",
            "product lead",
            "product owner",
        ],
        "related_skills": ["Roadmap Strategy", "User Research", "Metrics & KPIs", "A/B Testing", "Agile", "PRD Writing"],
    },
    "technical_product": {
        "id": "technical_product",
        "cluster": "product_cluster",
        "label": "Technical Product Management",
        "description": "Technical architecture, API/Platform products, infrastructure PM, and systems engineering",
        "icon": "Layers",
        "curated_tracks": [
            "Technical Product Manager (TPM)",
            "Principal TPM",
            "Platform Product Manager",
            "Infrastructure Product Manager",
            "Data Product Manager",
        ],
        "synonyms": [
            "technical product manager",
            "technical pm",
            "tpm",
            "principal tpm",
            "lead tpm",
            "platform product manager",
            "platform pm",
            "infrastructure product manager",
            "infrastructure pm",
            "data product manager",
            "data pm",
            "core tech pm",
            "api product manager",
        ],
        "related_skills": ["System Architecture", "API Design", "Distributed Systems", "Cloud Infrastructure", "Developer Tooling"],
    },
    "product_ops": {
        "id": "product_ops",
        "cluster": "product_cluster",
        "label": "Product Operations",
        "description": "Product operational efficiency, launch management, feature governance, and analytics enablement",
        "icon": "Sliders",
        "curated_tracks": [
            "Product Operations Manager",
            "ProdOps Lead",
            "Product Program Manager",
            "Product Enablement Specialist",
        ],
        "synonyms": [
            "product operations",
            "product ops",
            "prodops",
            "prod ops",
            "product operations manager",
            "prodops lead",
            "product program manager",
            "product enablement",
            "product enablement specialist",
        ],
        "related_skills": ["Launch Governance", "Process Optimization", "Cross-Functional Alignment", "Tooling Workflows"],
    },
    "management_consulting": {
        "id": "management_consulting",
        "cluster": "strategy_cluster",
        "label": "Management Consulting",
        "description": "High-stakes management consulting, organizational transformation, and strategic advisory",
        "icon": "Briefcase",
        "curated_tracks": [
            "Management Consultant",
            "Associate Consultant",
            "Engagement Manager",
            "Strategy Consultant",
            "Case Team Leader",
            "Principal Consultant",
        ],
        "synonyms": [
            "management consultant",
            "management consulting",
            "strategy consultant",
            "strategy consulting",
            "consultant",
            "associate consultant",
            "consulting associate",
            "engagement manager",
            "case team leader",
            "senior consultant",
            "principal consultant",
            "practice manager",
            "practice lead",
        ],
        "related_skills": ["Executive Communication", "Hypothesis-Driven Problem Solving", "Market Due Diligence", "Financial Modeling"],
    },
    "corporate_strategy": {
        "id": "corporate_strategy",
        "cluster": "strategy_cluster",
        "label": "Corporate Strategy & Planning",
        "description": "Long-range corporate strategic planning, M&A due diligence, corporate development, and venture building",
        "icon": "Compass",
        "curated_tracks": [
            "Corporate Strategy Analyst",
            "Strategic Planning Manager",
            "Corporate Development (CorpDev)",
            "Venture Architect",
            "Strategy & Business Development",
        ],
        "synonyms": [
            "corporate strategy",
            "strategic planning",
            "strategy analyst",
            "strategy associate",
            "corpdev",
            "corporate development",
            "venture architect",
            "venture architecture",
            "strategic finance",
            "strategy & operations",
            "strategy and operations",
            "strategic initiatives",
        ],
        "related_skills": ["Market Due Diligence", "Financial Valuation", "M&A Modeling", "Competitive Intelligence"],
    },
    "founders_office": {
        "id": "founders_office",
        "cluster": "strategy_cluster",
        "label": "Founder's Office & BizOps",
        "description": "Chief of Staff, Executive Operations, business operations (BizOps), and high-leverage special projects",
        "icon": "Crown",
        "curated_tracks": [
            "Chief of Staff",
            "Founder's Office Associate",
            "Executive Operations Lead",
            "Business Operations (BizOps) Manager",
            "Special Projects Lead",
        ],
        "synonyms": [
            "chief of staff",
            "founder's office",
            "founders office",
            "founder office",
            "founding team",
            "executive office",
            "special projects",
            "strategic initiatives",
            "bizops",
            "business operations",
            "biz ops",
            "operations associate",
            "operations manager",
        ],
        "related_skills": ["Executive Alignment", "Cross-Functional Execution", "P&L Analysis", "Zero-to-One Projects"],
    },
    "consulting_strategy": {
        "id": "consulting_strategy",
        "cluster": "strategy_cluster",
        "label": "Strategy & Consulting (Legacy)",
        "description": "Legacy umbrella category mapping to Strategy & Consulting cluster",
        "icon": "Briefcase",
        "curated_tracks": [
            "Management Consulting Associate",
            "Business Operations (BizOps)",
            "Chief of Staff",
            "Corporate Strategy Analyst",
        ],
        "synonyms": [
            "consulting",
            "strategy",
        ],
        "related_skills": ["Financial Modeling", "Market Analysis", "Executive Communication"],
    },
    "software_engineering": {
        "id": "software_engineering",
        "cluster": "engineering_cluster",
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
            "sde",
            "sde 1",
            "sde 2",
            "sde 3",
            "sde-1",
            "sde-2",
            "sde-3",
            "sde i",
            "sde ii",
            "sde iii",
            "mts",
            "smts",
            "member of technical staff",
            "engineering manager",
            "em",
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
        "cluster": "data_cluster",
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
        "cluster": "design_cluster",
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
        "cluster": "finance_cluster",
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
    "sales_gtm": {
        "id": "sales_gtm",
        "cluster": "sales_cluster",
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
        "cluster": "marketing_cluster",
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


# Evaluation precedence: specialized categories evaluate before generic ones
CATEGORY_PRECEDENCE_ORDER = [
    "founders_office",
    "technical_product",
    "product_ops",
    "management_consulting",
    "corporate_strategy",
    "product",
    "data_ai",
    "software_engineering",
    "design",
    "finance_quant",
    "sales_gtm",
    "marketing",
]


def get_all_categories() -> List[Dict[str, Any]]:
    """Returns list of active categories excluding the legacy umbrella alias."""
    return [c for c in CATEGORIES_TAXONOMY.values() if c["id"] != "consulting_strategy"]


def get_all_clusters() -> List[Dict[str, Any]]:
    """Returns list of all domain clusters."""
    return list(CATEGORY_CLUSTERS.values())


def get_cluster_by_id(cluster_id: str) -> Optional[Dict[str, Any]]:
    """Fetches cluster metadata by ID."""
    return CATEGORY_CLUSTERS.get(cluster_id.strip().lower())


def get_categories_in_cluster(cluster_id: str) -> List[str]:
    """Returns list of category IDs belonging to a cluster."""
    cl = get_cluster_by_id(cluster_id)
    if cl:
        return cl.get("categories", [])
    return []


def resolve_category_or_cluster(query_term: str) -> List[str]:
    """
    Expands a broad query term, category ID, or cluster alias into matching category IDs.
    Examples:
      'product' -> ['product', 'technical_product', 'product_ops']
      'strategy' -> ['management_consulting', 'corporate_strategy', 'founders_office']
      'founders_office' -> ['founders_office']
    """
    qt = query_term.strip().lower()
    if qt in CATEGORY_CLUSTERS:
        return CATEGORY_CLUSTERS[qt]["categories"]
    if qt in ("product", "products", "product_cluster"):
        return ["product", "technical_product", "product_ops"]
    if qt in ("strategy", "consulting", "strategy_cluster", "consulting_strategy", "management_consulting"):
        return ["management_consulting", "corporate_strategy", "founders_office"]
    if qt in CATEGORIES_TAXONOMY:
        return [qt]
    return [qt]


def get_category_by_id(cat_id: str) -> Optional[Dict[str, Any]]:
    """Fetches category metadata by ID."""
    return CATEGORIES_TAXONOMY.get(cat_id.strip().lower())


def match_category_phrase(phrase: str) -> Optional[Dict[str, Any]]:
    """
    Maps conversational role track phrases into canonical category, inferred seniority,
    matching track name, and parent cluster.
    """
    p = phrase.strip().lower()

    # Detect seniority
    seniority = None
    if re.search(r"\b(entry level|entry-level|junior|jr|new grad|new graduate|fresh grad|associate|early career|apm)\b", p):
        seniority = "entry"
    elif re.search(r"\b(intern|internship|co-op|coop)\b", p):
        seniority = "intern"
    elif re.search(r"\b(lead|principal|staff|director|head of|vp|partner|chief of staff|engagement manager)\b", p):
        seniority = "lead"
    elif re.search(r"\b(senior|sr|sr\.)\b", p):
        seniority = "senior"

    # Match in strict priority order (specific before broad)
    for cat_id in CATEGORY_PRECEDENCE_ORDER:
        meta = CATEGORIES_TAXONOMY.get(cat_id)
        if not meta:
            continue

        # 1. Direct curated track match
        for track in meta["curated_tracks"]:
            t_low = track.lower()
            if t_low in p or (len(p) > 3 and p in t_low):
                return {
                    "category": cat_id,
                    "cluster": meta.get("cluster"),
                    "seniority": seniority or ("entry" if "entry" in t_low or "grad" in t_low or "apm" in t_low or "associate" in t_low else None),
                    "label": meta["label"],
                    "synonyms": meta["synonyms"],
                    "matched_track": track,
                }

        # 2. Synonym match
        for syn in meta["synonyms"]:
            if re.search(rf"\b{re.escape(syn)}\b", p):
                return {
                    "category": cat_id,
                    "cluster": meta.get("cluster"),
                    "seniority": seniority,
                    "label": meta["label"],
                    "synonyms": meta["synonyms"],
                    "matched_track": meta["curated_tracks"][0] if meta["curated_tracks"] else None,
                }

    return None


TRACK_SYNONYMS_MAP: Dict[str, List[str]] = {
    "Chief of Staff": ["chief of staff", "cos", "executive operations", "special projects lead"],
    "Founder's Office Associate": ["founder's office", "founders office", "founder office", "founding team"],
    "Business Operations (BizOps) Manager": ["bizops", "business operations", "biz ops"],
    "Technical Product Manager (TPM)": ["technical product manager", "tpm", "technical pm"],
    "Principal TPM": ["principal tpm", "lead tpm", "staff tpm"],
    "Platform Product Manager": ["platform product manager", "platform pm"],
    "Infrastructure Product Manager": ["infrastructure product manager", "infrastructure pm"],
    "Data Product Manager": ["data product manager", "data pm"],
    "Product Operations Manager": ["product operations", "product ops", "prodops"],
    "Product Program Manager": ["product program manager", "product pgmp"],
    "Product Enablement Specialist": ["product enablement", "prodops enablement"],
    "Associate Product Manager (APM)": ["associate product manager", "apm", "rotational product manager", "rpm"],
    "Growth Product Manager": ["growth product manager", "growth pm"],
    "AI Product Manager": ["ai product manager", "ai pm", "machine learning product manager"],
    "Group Product Manager (GPM)": ["group product manager", "gpm", "lead product manager"],
    "Director / VP Product": ["director of product", "vp of product", "vp product", "head of product"],
    "Product Manager": ["product manager", "pm", "product lead", "product owner"],
    "Engagement Manager": ["engagement manager", "case team leader", "case leader", "project leader"],
    "Associate Consultant": ["associate consultant", "consulting associate", "business analyst"],
    "Management Consultant": ["management consultant", "strategy consultant", "consultant"],
    "Principal Consultant": ["principal consultant", "partner", "associate partner"],
    "Corporate Development (CorpDev)": ["corpdev", "corporate development", "corp dev", "m&a"],
    "Venture Architect": ["venture architect", "venture architecture"],
    "Strategic Planning Manager": ["strategic planning", "strategy manager", "corporate strategy"],
    "Strategy & Business Development": ["strategy & business development", "strategy and business development"],
    "Corporate Strategy Analyst": ["corporate strategy analyst", "strategy analyst", "strategy associate"],
}


def get_track_synonyms(track_name: str) -> List[str]:
    """Returns title synonyms and variations for a given track."""
    for key, syns in TRACK_SYNONYMS_MAP.items():
        if key.lower() == track_name.strip().lower():
            return syns
    return [track_name.strip().lower()]


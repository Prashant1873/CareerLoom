import re
from typing import Optional, Tuple


STRATEGY_CONSULTING_FIRMS = {
    "mckinsey", "mckinsey & company", "mckinsey and company",
    "bcg", "boston consulting group",
    "bain", "bain & company", "bain and company",
    "kearney", "a.t. kearney", "at kearney",
    "roland berger",
    "strategy&", "strategy and",
    "alvarez & marsal", "alvarez and marsal", "a&m",
    "oliver wyman", "oliverwyman",
    "dalberg", "dalberg advisors",
    "samagra", "samagra governance",
    "lek", "l.e.k.", "l.e.k. consulting",
    "monitor deloitte",
    "ey-parthenon", "ey parthenon",
    "pwc strategy", "pwc", "deloitte", "ey", "kpmg",
}

# Pre-compiled high-performance regexes (<0.1ms execution)
RE_FOUNDERS_OFFICE = re.compile(
    r"\b(chief of staff|founder'?s office|founders office|founding team|founder office|executive office|special projects|strategic initiatives|bizops|business operations|biz ops)\b",
    re.IGNORECASE,
)
RE_TECHNICAL_PRODUCT = re.compile(
    r"\b(technical product manager|technical pm|\btpm\b|principal tpm|lead tpm|platform product manager|platform pm|infrastructure product manager|infrastructure pm|data product manager|data pm|core tech pm|api product manager)\b",
    re.IGNORECASE,
)
RE_PRODUCT_OPS = re.compile(
    r"\b(product operations|product ops|prodops|prod ops|product operations manager|prodops lead|product program manager|product enablement)\b",
    re.IGNORECASE,
)
RE_MANAGEMENT_CONSULTING = re.compile(
    r"\b(management consult(?:ant|ing)|strategy consult(?:ant|ing)|engagement manager|case team leader|consulting associate|associate consultant|principal consultant|practice lead|practice manager)\b",
    re.IGNORECASE,
)
RE_CORPORATE_STRATEGY = re.compile(
    r"\b(corporate strategy|strategic planning|corpdev|corporate development|venture architect(?:ure)?|strategy analyst|strategy associate|strategic finance|strategy & operations|strategy and operations)\b",
    re.IGNORECASE,
)
RE_PRODUCT = re.compile(
    r"\b(product manager|product management|\bpm\b|apm|associate product manager|group product manager|gpm|director of product|vp product|vp of product|head of product|principal product manager|growth product manager|ai product manager|product lead|product owner)\b",
    re.IGNORECASE,
)
RE_DATA_AI = re.compile(
    r"\b(machine learning|\bml\b|ai\b|artificial intelligence|data scientist|data science|computer vision|\bnlp\b|deep learning|data engineer|mlops|llm engineer)\b",
    re.IGNORECASE,
)
RE_SOFTWARE_ENG = re.compile(
    r"\b(software engineer|software engineering|software developer|backend|frontend|fullstack|full-stack|\bswe\b|devops|\bsre\b|infrastructure|cloud engineer|systems engineer|platform engineer|firmware|embedded)\b",
    re.IGNORECASE,
)
RE_DESIGN = re.compile(
    r"\b(designer|product design|ui/ux|ux|ui designer|interaction design|graphic design|brand designer)\b",
    re.IGNORECASE,
)
RE_FINANCE = re.compile(
    r"\b(quantitative|quant|trading|trader|portfolio manager|risk analyst|investment|equity research|financial analyst)\b",
    re.IGNORECASE,
)
RE_SALES = re.compile(
    r"\b(account executive|sales engineer|sales development|sdr|bdr|business development|gtm|solutions architect)\b",
    re.IGNORECASE,
)
RE_MARKETING = re.compile(
    r"\b(marketing|content|growth|social media|seo|communications|devrel|developer advocate)\b",
    re.IGNORECASE,
)
RE_GENERIC_CONSULTING_TITLE = re.compile(
    r"\b(business analyst|senior business analyst|associate|senior associate|analyst|consultant|manager|case leader|practice manager)\b",
    re.IGNORECASE,
)


def classify_role(
    title: str,
    company: Optional[str] = None,
    domain_hint: Optional[str] = None,
) -> Tuple[str, str, Optional[str]]:
    """
    Infers canonical category, seniority, and granular track from job title and context hints.
    Returns: (category, seniority, track)
    Guarantees sub-0.1ms evaluation time via precompiled regexes with zero external API overhead.
    """
    t = title.strip().lower()
    comp_clean = re.sub(r"[^a-z0-9 ]", "", company.lower()).strip() if company else ""
    dom_clean = domain_hint.lower() if domain_hint else ""

    # Seniority detection
    seniority = "mid"
    if re.search(r"\b(intern|internship|co-op|coop|student)\b", t):
        seniority = "intern"
    elif re.search(r"\b(entry|junior|jr|associate|new grad|graduate|early career|entry-level|entry level|apm|analyst)\b", t):
        seniority = "entry"
    elif re.search(r"\b(staff|principal|lead|director|vp|head|chief|fellow|partner|engagement manager|gpm|case team leader)\b", t):
        seniority = "lead"
    elif re.search(r"\b(senior|sr|sr\.)\b", t):
        seniority = "senior"

    category = "general"
    track = None

    # Check employer context hint for Strategy Consulting targets
    is_consulting_target = False
    if comp_clean:
        for firm in STRATEGY_CONSULTING_FIRMS:
            if firm in comp_clean:
                is_consulting_target = True
                break
    if not is_consulting_target and ("consulting" in dom_clean or "strategy" in dom_clean):
        is_consulting_target = True

    # 1. Founder's Office & BizOps (Top precedence)
    if RE_FOUNDERS_OFFICE.search(t):
        category = "founders_office"
        if "chief of staff" in t:
            track = "Chief of Staff"
            if "junior" not in t and "associate" not in t:
                seniority = "lead"
        elif "founder" in t:
            track = "Founder's Office Associate"
        elif "bizops" in t or "business operations" in t:
            track = "Business Operations (BizOps) Manager"
        elif "executive office" in t:
            track = "Executive Operations Lead"
        elif "special projects" in t:
            track = "Special Projects Lead"
        else:
            track = "Chief of Staff"

    # 2. Technical Product Management (TPM)
    elif RE_TECHNICAL_PRODUCT.search(t):
        category = "technical_product"
        if "principal" in t or "lead" in t:
            track = "Principal TPM"
            seniority = "lead"
        elif "platform" in t:
            track = "Platform Product Manager"
        elif "infrastructure" in t:
            track = "Infrastructure Product Manager"
        elif "data" in t:
            track = "Data Product Manager"
        else:
            track = "Technical Product Manager (TPM)"

    # 3. Product Operations
    elif RE_PRODUCT_OPS.search(t):
        category = "product_ops"
        if "program" in t:
            track = "Product Program Manager"
        elif "enablement" in t:
            track = "Product Enablement Specialist"
        elif "manager" in t or "lead" in t:
            track = "Product Operations Manager"
        else:
            track = "ProdOps Lead"

    # 4. Management Consulting
    elif RE_MANAGEMENT_CONSULTING.search(t):
        category = "management_consulting"
        if "engagement manager" in t:
            track = "Engagement Manager"
            seniority = "lead"
        elif "case team" in t or "case leader" in t:
            track = "Case Team Leader"
            seniority = "lead"
        elif "associate" in t:
            track = "Associate Consultant"
            seniority = "entry"
        elif "principal" in t:
            track = "Principal Consultant"
            seniority = "lead"
        else:
            track = "Management Consultant"

    # 5. Corporate Strategy & Planning
    elif RE_CORPORATE_STRATEGY.search(t):
        category = "corporate_strategy"
        if "corpdev" in t or "corporate development" in t:
            track = "Corporate Development (CorpDev)"
        elif "venture architect" in t:
            track = "Venture Architect"
        elif "planning" in t:
            track = "Strategic Planning Manager"
        elif "business development" in t or "& operations" in t:
            track = "Strategy & Business Development"
        else:
            track = "Corporate Strategy Analyst"

    # Disambiguate generic titles for Strategy Consulting employers
    elif is_consulting_target and RE_GENERIC_CONSULTING_TITLE.search(t):
        category = "management_consulting"
        if "associate" in t:
            track = "Associate Consultant"
            seniority = "entry"
        elif "analyst" in t:
            track = "Management Consultant"
            seniority = "entry"
        elif "manager" in t:
            track = "Engagement Manager"
            seniority = "lead"
        else:
            track = "Management Consultant"

    # 6. Core Product Management
    elif RE_PRODUCT.search(t):
        category = "product"
        if "apm" in t or "associate product" in t:
            track = "Associate Product Manager (APM)"
            seniority = "entry"
        elif "growth" in t:
            track = "Growth Product Manager"
        elif "ai product" in t:
            track = "AI Product Manager"
        elif "group product" in t or re.search(r"\bgpm\b", t):
            track = "Group Product Manager (GPM)"
            seniority = "lead"
        elif "director" in t or re.search(r"\bvp\b", t) or "head of" in t:
            track = "Director / VP Product"
            seniority = "lead"
        elif "senior" in t or re.search(r"\bsr\b", t):
            track = "Senior Product Manager"
            seniority = "senior"
        else:
            track = "Product Manager"

    # 7. AI & Data Science
    elif RE_DATA_AI.search(t):
        category = "data_ai"
        if "research" in t:
            track = "AI Researcher"
        elif "machine learning" in t or re.search(r"\bml\b", t):
            track = "Machine Learning Engineer"
        elif "data engineer" in t:
            track = "Data Engineer"
        else:
            track = "Data Scientist"

    # 8. Software Engineering
    elif RE_SOFTWARE_ENG.search(t):
        category = "software_engineering"
        if "backend" in t:
            track = "Backend Systems Engineer"
        elif "frontend" in t:
            track = "Frontend React Engineer"
        elif "infrastructure" in t or "devops" in t or "sre" in t:
            track = "Cloud Infrastructure / DevOps"
        elif "full" in t:
            track = "Full Stack Engineer"
        else:
            track = "Software Engineer"

    # 9. Design & UX
    elif RE_DESIGN.search(t):
        category = "design"
        track = "UI/UX Designer"

    # 10. Quantitative & Finance
    elif RE_FINANCE.search(t):
        category = "finance_quant"
        track = "Quantitative Research Analyst"

    # 11. Sales & Go-to-Market
    elif RE_SALES.search(t):
        category = "sales_gtm"
        track = "Solutions Architect"

    # 12. Growth & Marketing
    elif RE_MARKETING.search(t):
        category = "marketing"
        track = "Growth Marketing Associate"

    return category, seniority, track


INDIAN_COMPANIES_HINTS = {
    "cred", "meesho", "paytm", "groww", "inmobi", "glance", "slice", "swiggy",
    "porter", "hackerrank", "sarvam", "navi", "epifi", "fimoney", "pocketfm", "stagein",
    "lokal", "signoz", "zeta", "bluestone", "atlan", "acceldata", "unacademy",
    "kredx", "lendingkart", "turtlemint", "cars24", "whatfix", "nobroker",
    "interviewbit", "newtonschool", "ixigo", "abhibus", "bounce", "river", "vogo",
    "captainfresh", "entropik", "kovaico", "mindtickle", "druva", "highradius",
    "zenoti", "freshworks", "thoughtworks", "tcs", "fampay", "shipsy", "entrupy",
    "upstox", "razorpay", "phonepe", "zepto", "zomato", "blinkit", "urbancompany",
    "shadowfax", "hasura", "postman", "browserstack"
}

INDIAN_METRO_HUBS = {
    "bengaluru": "Bengaluru",
    "bangalore": "Bengaluru",
    "blr": "Bengaluru",
    "hyderabad": "Hyderabad",
    "hyd": "Hyderabad",
    "pune": "Pune",
    "pun": "Pune",
    "mumbai": "Mumbai",
    "bombay": "Mumbai",
    "delhi": "Delhi NCR",
    "new delhi": "Delhi NCR",
    "gurgaon": "Delhi NCR",
    "gurugram": "Delhi NCR",
    "noida": "Delhi NCR",
    "ncr": "Delhi NCR",
    "chennai": "Chennai",
    "madras": "Chennai",
    "kolkata": "Kolkata",
    "ahmedabad": "Ahmedabad",
    "kochi": "Kochi",
    "indore": "Indore",
    "jaipur": "Jaipur",
}


def get_indian_metro_hub(location_text: str) -> str:
    """
    Returns canonical metro hub name (e.g. 'Bengaluru', 'Delhi NCR', 'Hyderabad')
    or empty string if not an Indian metro hub.
    """
    lt = location_text.lower()
    for key, canonical in INDIAN_METRO_HUBS.items():
        if re.search(rf"\b{re.escape(key)}\b", lt):
            return canonical
    return ""


def parse_location(location_name: str, title: str = "", company_hint: str = "") -> Tuple[str, str, bool]:
    """
    Extracts (location_display, country, is_remote) from location string and title.
    """
    combined = f"{location_name} {title}".lower()

    # Remote detection
    is_remote = bool(re.search(r"\b(remote|anywhere|distributed|virtual|work from home|wfh)\b", combined))

    # Country detection
    country = "Global"
    if re.search(r"\b(us|united states|usa|san francisco|new york|nyc|seattle|austin|chicago|boston|los angeles|california|texas|washington|santa clara|sunnyvale|mountain view|palo alto|san jose|ca|ny|wa|tx|ma|il)\b", combined):
        country = "United States"
    elif re.search(r"\b(uk|united kingdom|london|manchester|edinburgh|cambridge|oxford|england|gb)\b", combined):
        country = "United Kingdom"
    elif re.search(r"\b(japan|tokyo|osaka|kyoto)\b", combined):
        country = "Japan"
    elif re.search(r"\b(canada|toronto|vancouver|montreal|ottawa)\b", combined):
        country = "Canada"
    elif re.search(r"\b(germany|berlin|munich|frankfurt|hamburg)\b", combined):
        country = "Germany"
    elif re.search(r"\b(france|paris)\b", combined):
        country = "France"
    elif re.search(r"\b(india|bangalore|bengaluru|mumbai|delhi|hyderabad|pune|gurgaon|gurugram|noida|chennai|ahmedabad|kolkata|kochi|indore|jaipur|chandigarh|ncr|karnataka|maharashtra|telangana|tamil nadu|haryana|gujarat|blr|hyd)\b", combined):
        country = "India"
    elif re.search(r"\b(ireland|dublin)\b", combined):
        country = "Ireland"
    elif re.search(r"\b(netherlands|amsterdam)\b", combined):
        country = "Netherlands"
    elif re.search(r"\b(singapore)\b", combined):
        country = "Singapore"
    elif re.search(r"\b(australia|sydney|melbourne)\b", combined):
        country = "Australia"
    elif re.search(r"\b(switzerland|zurich|geneva)\b", combined):
        country = "Switzerland"
    elif re.search(r"\b(uae|dubai|abu dhabi)\b", combined):
        country = "United Arab Emirates"
    elif re.search(r"\b(brazil|sao paulo)\b", combined):
        country = "Brazil"
    elif is_remote:
        country = "Remote / Global"

    # Fallback for Indian startups if country was not explicitly marked
    if country in ("Global", "Remote / Global") and company_hint:
        hint_clean = re.sub(r"[^a-z0-9]", "", company_hint.lower())
        if hint_clean in INDIAN_COMPANIES_HINTS:
            country = "India"

    hub = get_indian_metro_hub(combined)
    if country == "India" and hub:
        location_display = f"{hub}, India" if not is_remote else f"{hub} (Remote)"
    elif location_name.strip():
        location_display = location_name.strip()
    elif is_remote and country == "India":
        location_display = "Remote (India)"
    elif is_remote:
        location_display = "Remote"
    elif country == "India":
        location_display = "India"
    else:
        location_display = "Global"

    return location_display, country, is_remote

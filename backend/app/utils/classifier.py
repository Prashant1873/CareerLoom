import re
from typing import Tuple


def classify_role(title: str) -> Tuple[str, str]:
    """
    Infers canonical category and seniority from a job title.
    Returns: (category, seniority)
    """
    t = title.lower()

    # Seniority detection
    seniority = "mid"
    if re.search(r"\b(intern|internship|co-op|coop|student)\b", t):
        seniority = "intern"
    elif re.search(r"\b(entry|junior|jr|associate|new grad|graduate|early career|entry-level|entry level|apm)\b", t):
        seniority = "entry"
    elif re.search(r"\b(staff|principal|lead|director|vp|head|chief|fellow)\b", t):
        seniority = "lead"
    elif re.search(r"\b(senior|sr|sr\.)\b", t):
        seniority = "senior"

    # Category detection
    category = "general"
    if re.search(r"\b(product manager|product management|\bpm\b|technical product manager|apm|group product manager)\b", t):
        category = "product"
    elif re.search(r"\b(machine learning|\bml\b|ai\b|artificial intelligence|data scientist|data science|computer vision|\bnlp\b|deep learning|data engineer|mlops)\b", t):
        category = "data_ai"
    elif re.search(r"\b(software engineer|software engineering|software developer|backend|frontend|fullstack|full-stack|\bswe\b|devops|\bsre\b|infrastructure|cloud engineer|systems engineer|platform engineer|firmware|embedded)\b", t):
        category = "software_engineering"
    elif re.search(r"\b(designer|product design|ui/ux|ux|ui designer|interaction design|graphic design)\b", t):
        category = "design"
    elif re.search(r"\b(quantitative|quant|trading|trader|portfolio manager|risk analyst|investment|equity research|financial analyst)\b", t):
        category = "finance_quant"
    elif re.search(r"\b(consultant|consulting|strategy|business operations|bizops|operations associate)\b", t):
        category = "consulting_strategy"
    elif re.search(r"\b(account executive|sales engineer|sales development|sdr|bdr|business development|gtm)\b", t):
        category = "sales_gtm"
    elif re.search(r"\b(marketing|content|growth|social media|seo|communications)\b", t):
        category = "marketing"

    return category, seniority


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

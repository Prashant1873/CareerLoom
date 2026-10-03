import json
import logging
import os
import re
from typing import Any, Dict, Optional
import httpx

from backend.app.utils.query_cache import query_cache

logger = logging.getLogger("careerloom.llm_adapter")


class HeuristicQueryParser:
    """
    High-speed, offline rule-based natural language parser.
    Extracts structured query parameters without requiring any external LLM API key.
    """

    CATEGORIES = {
        "product": [
            r"\b(product|product manager|product management|\bpm\b|apm|technical product manager|product lead|product owner)\b"
        ],
        "software_engineering": [
            r"\b(software engineer|software engineering|software developer|backend|frontend|fullstack|full-stack|\bswe\b|devops|\bsre\b|infrastructure|cloud engineer|systems engineer|firmware|embedded|web developer)\b"
        ],
        "data_ai": [
            r"\b(machine learning|\bml\b|ai\b|artificial intelligence|data scientist|data science|computer vision|\bnlp\b|deep learning|data engineer|mlops|llm)\b"
        ],
        "design": [
            r"\b(designer|product design|ui/ux|ux designer|ui designer|interaction design|graphic design|brand designer)\b"
        ],
        "finance_quant": [
            r"\b(quantitative|quant|trader|trading|portfolio manager|risk analyst|investment|equity research|financial analyst|fintech)\b"
        ],
        "consulting_strategy": [
            r"\b(consultant|consulting|strategy|business operations|bizops|operations associate|chief of staff)\b"
        ],
        "sales_gtm": [
            r"\b(account executive|sales engineer|sales development|sdr|bdr|business development|gtm|account manager)\b"
        ],
        "marketing": [
            r"\b(marketing|growth marketer|content strategist|seo|social media|developer advocate|developer relations)\b"
        ],
    }

    SENIORITIES = {
        "intern": r"\b(intern|internship|co-op|coop|student)\b",
        "entry": r"\b(entry level|entry-level|junior|jr|new grad|new graduate|fresh graduate|associate|early career)\b",
        "lead": r"\b(lead|principal|staff|director|vp|head of|chief)\b",
        "senior": r"\b(senior|sr|sr\.)\b",
    }

    GEOGRAPHIES = {
        "Germany": r"\b(germany|berlin|munich|frankfurt|hamburg)\b",
        "United Kingdom": r"\b(uk|united kingdom|london|manchester|edinburgh|cambridge|oxford)\b",
        "France": r"\b(france|paris)\b",
        "Canada": r"\b(canada|toronto|vancouver|montreal|ottawa)\b",
        "India": r"\b(india|bangalore|bengaluru|mumbai|delhi|hyderabad|pune|gurgaon)\b",
        "Singapore": r"\b(singapore)\b",
        "Australia": r"\b(australia|sydney|melbourne)\b",
        "United States": r"\b(us|usa|united states|san francisco|sf|bay area|new york|nyc|seattle|austin|chicago|boston|los angeles)\b",
        "Europe": r"\b(europe|eu|netherlands|ireland|amsterdam|dublin|switzerland|zurich)\b",
    }

    DOMAINS = {
        "Fintech": r"\b(fintech|payments|banking|trading|crypto|defi)\b",
        "AI / Research": r"\b(ai|artificial intelligence|foundation models|genai|llm)\b",
        "DevTools": r"\b(devtools|developer tools|infrastructure|cloud)\b",
        "Design": r"\b(design|creative|3d|graphics)\b",
        "Healthcare": r"\b(health|healthcare|biotech|pharma)\b",
    }

    def parse(self, prompt: str) -> Dict[str, Any]:
        p = prompt.strip().lower()

        # 1. Category extraction
        detected_category = None
        for cat, patterns in self.CATEGORIES.items():
            for pat in patterns:
                if re.search(pat, p):
                    detected_category = cat
                    break
            if detected_category:
                break

        # 2. Seniority extraction
        detected_seniority = None
        for sen, pat in self.SENIORITIES.items():
            if re.search(pat, p):
                detected_seniority = sen
                break

        # 3. Remote detection
        is_remote = bool(re.search(r"\b(remote|anywhere|distributed|virtual|work from home|wfh)\b", p))

        # 4. Geography extraction
        detected_country = None
        for country, pat in self.GEOGRAPHIES.items():
            if re.search(pat, p):
                detected_country = country
                break
        if not detected_country and is_remote:
            detected_country = "Remote"

        # 5. Domain extraction
        detected_domain = None
        for domain, pat in self.DOMAINS.items():
            if re.search(pat, p):
                detected_domain = domain
                break

        # 6. Freshness / Date posted extraction
        posted_within_days = None
        if re.search(r"\b(today|past 24 hours|last 24 hours|1 day)\b", p):
            posted_within_days = 1
        elif re.search(r"\b(this week|past week|last week|past 7 days|last 7 days)\b", p):
            posted_within_days = 7
        elif re.search(r"\b(past 2 weeks|last 2 weeks|past 14 days)\b", p):
            posted_within_days = 14
        elif re.search(r"\b(this month|past month|last month|past 30 days)\b", p):
            posted_within_days = 30

        # 7. Extract remaining keywords for search
        # Strip stop words, category phrases, geographic words, freshness words, and conjunctions
        cleaned = p
        # Strip category patterns if matched
        if detected_category:
            for pat in self.CATEGORIES.get(detected_category, []):
                cleaned = re.sub(pat, " ", cleaned)
        # Strip seniority words
        for pat in self.SENIORITIES.values():
            cleaned = re.sub(pat, " ", cleaned)
        # Strip geography words
        for pat in self.GEOGRAPHIES.values():
            cleaned = re.sub(pat, " ", cleaned)
        # Strip stop words and time terms
        cleaned = re.sub(
            r"\b(find|search|jobs|roles|positions|looking for|in|at|for|with|posted|recent|recently|remote|anywhere|wfh|today|yesterday|week|month|days|hours|or|and|the|a|an|of|to|this|past|last|engineer|developer|manager|specialist)\b",
            " ",
            cleaned,
        )
        remaining_terms = " ".join(cleaned.split())
        search_terms = remaining_terms if len(remaining_terms) >= 3 else None

        return {
            "search_terms": search_terms,
            "category": detected_category,
            "seniority": detected_seniority,
            "country": detected_country,
            "is_remote": is_remote if is_remote else None,
            "domain": detected_domain,
            "posted_within_days": posted_within_days,
            "parser_used": "heuristic",
        }


class LLMQueryService:
    """
    Orchestrates natural language parsing using free online LLM APIs
    (Groq, Google Gemini, OpenRouter) with seamless fallback to HeuristicQueryParser.
    """

    def __init__(self):
        self.heuristic_parser = HeuristicQueryParser()
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

    async def parse(self, prompt: str) -> Dict[str, Any]:
        cleaned_prompt = prompt.strip()
        if not cleaned_prompt:
            return {
                "search_terms": None,
                "category": None,
                "seniority": None,
                "country": None,
                "is_remote": None,
                "domain": None,
                "posted_within_days": None,
                "parser_used": "empty",
            }

        # Check in-memory LRU query cache
        cached = query_cache.get(cleaned_prompt)
        if cached:
            cached_copy = dict(cached)
            cached_copy["cached"] = True
            return cached_copy

        # Try Groq API if key is available
        if self.groq_api_key:
            res = await self._call_groq(cleaned_prompt)
            if res:
                query_cache.set(cleaned_prompt, res)
                return res

        # Try Gemini API if key is available
        if self.gemini_api_key:
            res = await self._call_gemini(cleaned_prompt)
            if res:
                query_cache.set(cleaned_prompt, res)
                return res

        # Try OpenRouter API if key is available
        if self.openrouter_api_key:
            res = await self._call_openrouter(cleaned_prompt)
            if res:
                query_cache.set(cleaned_prompt, res)
                return res

        # Fallback to local heuristic parser
        result = self.heuristic_parser.parse(cleaned_prompt)
        query_cache.set(cleaned_prompt, result)
        return result

    async def _call_groq(self, prompt: str) -> Optional[Dict[str, Any]]:
        url = "https://api.groq.com/openai/v1/chat/completions"
        system_prompt = """You are a job search query parser. Extract structured parameters from user job search input.
Output ONLY a valid JSON object matching this schema:
{
  "search_terms": string or null (specific tech or company keywords like 'python', 'stripe', 'react'),
  "category": "product" | "software_engineering" | "data_ai" | "design" | "finance_quant" | "consulting_strategy" | "sales_gtm" | null,
  "seniority": "intern" | "entry" | "mid" | "senior" | "lead" | null,
  "country": string or null (e.g. "United States", "United Kingdom", "Europe", "India", "Remote"),
  "is_remote": boolean or null,
  "domain": string or null (e.g. "Fintech", "AI / Research"),
  "posted_within_days": integer or null (e.g. 1, 7, 14, 30)
}"""

        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.0,
            "max_tokens": 200,
        }

        try:
            async with httpx.AsyncClient(timeout=3.5) as client:
                resp = await client.post(url, headers=headers, json=body)
                if resp.status_code == 200:
                    data = resp.json()
                    content = data["choices"][0]["message"]["content"]
                    parsed = json.loads(content)
                    parsed["parser_used"] = "groq-llama-3.3"
                    return parsed
        except Exception as e:
            logger.warning(f"Groq API call failed or timed out: {e}")
        return None

    async def _call_gemini(self, prompt: str) -> Optional[Dict[str, Any]]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        instruction = """Extract structured parameters from this job query as pure JSON:
Schema:
{"search_terms": string or null, "category": string or null, "seniority": string or null, "country": string or null, "is_remote": boolean or null, "domain": string or null, "posted_within_days": int or null}
Categories: product, software_engineering, data_ai, design, finance_quant, consulting_strategy, sales_gtm."""

        body = {
            "contents": [
                {"parts": [{"text": f"{instruction}\n\nQuery: {prompt}"}]}
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.0,
            }
        }

        try:
            async with httpx.AsyncClient(timeout=3.5) as client:
                resp = await client.post(url, json=body)
                if resp.status_code == 200:
                    data = resp.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(text)
                    parsed["parser_used"] = "gemini-1.5-flash"
                    return parsed
        except Exception as e:
            logger.warning(f"Gemini API call failed: {e}")
        return None

    async def _call_openrouter(self, prompt: str) -> Optional[Dict[str, Any]]:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": "meta-llama/llama-3.3-70b-instruct:free",
            "messages": [
                {"role": "system", "content": "Extract structured job filters as pure JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.0,
        }
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.post(url, headers=headers, json=body)
                if resp.status_code == 200:
                    data = resp.json()
                    content = data["choices"][0]["message"]["content"]
                    # Extract JSON from markdown
                    match = re.search(r"\{.*\}", content, re.DOTALL)
                    if match:
                        parsed = json.loads(match.group(0))
                        parsed["parser_used"] = "openrouter-free"
                        return parsed
        except Exception as e:
            logger.warning(f"OpenRouter call failed: {e}")
        return None


# Module-level convenience function
_service = LLMQueryService()


async def parse_natural_language_query(prompt: str) -> Dict[str, Any]:
    return await _service.parse(prompt)

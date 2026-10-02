# Great Ideas & Vision

## 1. Natural Language Career Discovery Engine
- **Core Concept**: An intelligent aggregator that queries major firms' direct career sites (Greenhouse, Lever, Ashby, Workday, custom enterprise portals) across domains, companies, and countries.
- **Natural Language Query Parser**:
  - Uses a free online AI/LLM API model (e.g. Groq free tier, Hugging Face Inference API, OpenRouter free models, or Google Gemini API).
  - Users can enter freeform prompts like *"entry level product management in Europe or remote"* or *"roles for junior Python engineers posted recently"*.
  - Query parser extracts structured search parameters: role category, seniority level, country/region, tech stack, remote preferences, and posting freshness.
- **Category-Based & Exploratory Browsing**:
  - Eliminates strict title mismatch issues by mapping queries to semantic categories (e.g. "Product Entry Level", "Data Science New Grad", "Infrastructure Engineer").

## 2. Dynamic Filtering & Card-Based Experience
- **Fluid Filtering**: Natural language filtering layered on top of structured faceted filters (date posted, location, firm tier, domain).
- **Rich Result Cards**: High-density, elegant cards displaying role title, company, location, employment type, direct apply link, and explicitly highlighted date posted.
- **Aesthetic Floor**: Anti-slop, clean visual hierarchy, keyboard navigation, fluid transitions (complying with modern UX and frontend principles).

## 3. Community Intelligence & Context (Phase 2)
- **Reddit & Forum Sentiment Extraction**: Pull authentic threads, interview timelines, salary discussions, and candidate reviews from Reddit (e.g. r/cscareerquestions, r/ProductManagement) and public career communities.
- **Company Vibe & Timeline Meter**: Display expected turnaround time, interview rounds, and insider advice directly alongside the job listing.

## 4. Intelligent Scraping & Ingestion Strategy
- **Scraper Pipeline Exploration**: Investigate AI-assisted web scraping engines like [Scrapegraph-ai](https://github.com/ScrapeGraphAI/Scrapegraph-ai) for unstructured career sites.
- **Standard ATS Direct Feed Ingestion**: Connect directly to public JSON feeds of Greenhouse, Lever, Ashby, and Workday boards for fast, reliable, zero-block data ingestion.

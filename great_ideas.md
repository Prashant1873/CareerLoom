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
- **Standard ATS Direct Feed Ingestion**: Connect directly to public JSON feeds of Greenhouse, Lever, and Ashby boards for fast, reliable, zero-block data ingestion.
- **Enterprise ATS Direct API Connectors**:
  - **Workday Candidate Experience Service (CXS)**: Direct REST endpoint (`POST /wday/cxs/{tenant}/{career_site}/jobs`) enabling zero-scraping, zero-bot-block ingestion of Fortune 500 companies (Pfizer, Target, Adobe, Morgan Stanley).
  - **SmartRecruiters Public API**: Zero-auth public postings feed (`GET /v1/companies/{company}/postings`) for tier-1 global employers (Visa, Bosch, IKEA, Ubisoft).
  - **Lightweight Semantic DOM Cleaner**: BS4 HTML boilerplate stripper + free online LLM semantic normalizer for unstructured enterprise career portals (McKinsey, Apple, BCG, Bain, Goldman Sachs).

## 5. v2 Visual Overhaul: Desktop-Grade Control Center (Linear / Raycast Style)
- **Master-Detail 3-Column Architecture**:
  - **Column 1 (Navigation Rail)**: Collapsible icon/expanded sidebar with quick-views (All, Saved, Fresh <24h), taxonomy category badges, and faceted filter accordions.
  - **Column 2 (Master Job Stream)**: Omnibox conversational search bar (`/`), active filter pills, sort controls, and scannable cards with `J`/`K` keyboard cursor navigation.
  - **Column 3 (Inspector & Community Intel Pane)**: Persistent right-hand inspector pane showing role breakdown, direct ATS apply button, and embedded tabbed Reddit community intel (turnaround estimate, interview roadmap, candidate tips, discussion links) without intrusive modal interruptions.
- **Obsidian Studio Palette**: Deep charcoal canvas, hairline borders, emerald active indicators, amber Reddit badges, and WCAG 2.2 AA optical hierarchy.
- **Tactile Fluid Physics**: Apple HIG interruptible spring physics, instant pointer-down state response, and keyboard ergonomics.

## 6. Massive Global Portal Expansion & Multi-ATS Ingestion (200+ Firms)
- **Full Global Spectrum**: Broadening career feed sources across 200+ elite global firms across:
  - **AI Labs & High-Growth Unicorns**: OpenAI, Anthropic, Scale AI, Databricks, Mistral AI, Cohere, Perplexity, Cursor/Anysphere, Modal, Replit, ElevenLabs, Together AI, Retool, Supabase, Vercel, Linear, Canva, PostHog, Rippling.
  - **Big Tech & Cloud Platforms**: Stripe, Figma, Airbnb, DoorDash, Pinterest, Coinbase, GitLab, Cloudflare, Twilio, MongoDB, Elastic, HashiCorp, Unity, Datadog, Samsara, Toast, Asana, HubSpot, Box.
  - **Quantitative Finance, Hedge Funds & Prop Trading**: Citadel, Jane Street, Two Sigma, Jump Trading, Hudson River Trading (HRT), D.E. Shaw, Point72, Millennium, Bridgewater, Optiver, IMC Trading, Akuna Capital.
  - **Global Investment Banking & Financial Infrastructure**: Goldman Sachs, Morgan Stanley, JPMorgan Chase, Bloomberg, BlackRock, Barclays, Deutsche Bank, Revolut, Monzo, Klarna, Plaid, Chime, Brex, Ramp.
  - **Tier-1 Strategy & Management Consulting**: McKinsey & Company, Boston Consulting Group (BCG), Bain & Company, Oliver Wyman, Kearney, Roland Berger, Strategy&.
  - **Global Healthcare, Biopharma & Biotech**: Pfizer, Moderna, Abbott, Roche, Novartis, Johnson & Johnson, Genentech, Eli Lilly, Illumina, Gilead.
  - **European & Global Tech Leaders**: Spotify, Wise, Adyen, Delivery Hero, Celonis, Checkout.com, Personio, Bolt, N26.
- **Pre-Populated & Instant Search**: Massive concurrent batch sync pipeline populating SQLite cache to deliver thousands of verified direct listings with sub-50ms query response times.



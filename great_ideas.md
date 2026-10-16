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
## 7. Deep India Tech Ecosystem & Startup Coverage
- **Core Value**: Direct-from-source visibility into India's vibrant startup and high-growth tech ecosystem without ATS friction or aggregator spam.
- **Top Indian Unicorns & Startups**:
  - **Fintech & Banking**: Paytm (One97), CRED, Groww, Zeta, Fi Money (EpiFi), KredX, Lendingkart, Turtlemint.
  - **Ecommerce & Quick Commerce**: Swiggy, Meesho, Cars24, Captain Fresh.
  - **Generative AI & Data Infrastructure**: Sarvam AI (foundational Indian LLMs), Atlan (data governance & metadata AI), SigNoz (open-source observability & APM), Acceldata (data observability).
  - **Enterprise SaaS & DevTools**: InMobi, Glance, Freshworks, HackerRank, HighRadius, Zenoti, Mindtickle, Druva, Kovai.co, Whatfix, Entropik Tech.
  - **EdTech & Career Prep**: Unacademy, InterviewBit, Newton School.
  - **Travel, Media & Consumer Tech**: Ixigo, AbhiBus, Pocket FM, Lokal, NoBroker, Truecaller India, Instawork, Thoughtworks India.
- **Regional Tech Hub Mapping**: Comprehensive normalization for Indian metropolitan tech hubs (Bengaluru, Hyderabad, Mumbai, Delhi NCR / Gurugram / Noida, Pune, Chennai, Ahmedabad) guaranteeing instant discovery and sub-50ms filtering by Country = "India".

## 8. Milestone v4: India Launch & Indian Leads Maximization Engine
- **India-First Discovery Controls**:
  - Direct "India Direct" toggle in navigation rail for instant 1-click filtering to all verified Indian listings.
  - Metro Tech Hub Quick Filter ribbon: Bengaluru (BLR), NCR / Gurgaon / Noida, Hyderabad (HYD), Pune (PUN), Mumbai (BOM), Chennai (MAA), and Remote (India).
  - INR CTC Compensation parsing and prominent badges (e.g. ₹20-35 LPA, ₹45L+).
- **Candidate Lead Capture & Fast Referral Engine**:
  - "Ask for Referral / Submit Lead" CTA on job cards and the persistent inspector.
  - Candidate lead capture drawer/modal collecting LinkedIn profile, YoE, target role, expected CTC, and resume link.
  - SQLite `candidate_leads` registry with exportable lead cards for recruiters and talent pools.
  - Fast one-click copy of candidate lead summaries for sharing in peer referral Slack/Discord/WhatsApp communities.
- **Indian Developer Community Intel**:
  - Ingest authentic candidate reviews and interview timelines from `r/developersIndia`, `r/IndianStartups`, and `r/IndiaTech`.
  - Realistic Indian hiring stage breakdown: Online Assessment, Machine Coding, System Design / Low Level Design (LLD/HLD), Hiring Manager, and HR/Notice Period negotiation.

## 9. Milestone v5: Indian Career Repository & Continuous Batch Scraping Engine
- **Career Targets Registry as Core Source of Truth**:
  - Move away from static company lists to a dedicated SQLite `career_targets` table.
  - Tracks 200+ Indian companies (Startups, Unicorns, Conglomerates, Strategy Consulting), their career links, ATS connectors, scraping status, role focus tags, and sync timestamps.
- **Reddit-Driven Continuous Discovery**:
  - Automated mining of `r/developersIndia`, `r/IndianStartups`, `r/ProductManagement`, `r/consulting`, and `r/bangalore` to discover trending companies and career portals.
  - Dynamic probing of ATS endpoints (Ashby, Lever, Greenhouse, SmartRecruiters, Workday).
- **Emphasis on Product Management & Strategy Consulting**:
  - Dedicated taxonomies and sub-50ms search tracks for PM (APM, PM, Senior PM, Group PM, VP Product, TPM, ProdOps) and Strategy & Consulting (Consultant, Strategy Analyst, Chief of Staff, Founder's Office, BizOps).
- **Continuous High-Throughput Batch Scraping with Stale Job Pruning**:
  - Async concurrent scraping engine with bounded concurrency and error isolation.
  - Automatic pruning/archiving of listings no longer found on source career portals, preventing ghost jobs and broken links.
- **Frontend Career Directory Hub**:
  - Obsidian dark directory view allowing users to inspect monitored companies, direct career URLs, ATS types, and live job counts.

## 10. Milestone v6: Obsidian Light & Dual-Theme Ergonomics
- **Obsidian Porcelain & Cool Slate Palette**:
  - Anti-slop light mode using an off-white porcelain canvas (`#f8fafc`) paired with crisp white card surfaces (`#ffffff`) and deep slate typography (`#0f172a`), preserving the premium craft of the dark theme.
- **Perceptual Contrast Standards & WCAG 2.2 AA Compliance**:
  - Darkened primary emerald accent (`#059669`) achieving 4.6:1 contrast against pure white, overcoming the readability failure of bright mint accents on white.
  - Saturated typography for semantic pills (Domain, Match, Remote, Tier, Compensation) ensuring >4.5:1 contrast over subtle 10-14% alpha backgrounds.
- **Viscoelastic Dual-Theme Toggle**:
  - Tactile theme switcher with Apple fluid spring kinetics (`damping: 1.0`) embedded cleanly in the left navigation rail.
  - Zero-flash theme hydration via local storage synchronization and system `prefers-color-scheme` support.

## 11. Cross-Platform Tiranga SVG & Unicode Fallback Elimination
- **Zero-Dependency SVG Tiranga**:
  - Windows 10/11 system font `Segoe UI Emoji` lacks regional indicator flag glyphs by OS policy, rendering `🇮🇳` as literal letters "IN".
  - Standardized vector `<IndiaFlag />` component featuring accurate 3:2 tricolor geometry (saffron `#FF9933`, white `#FFFFFF`, green `#138808`) and central 24-spoke Ashoka Chakra (`#000080`).
  - Seamlessly embedded in navigation rails, category cluster pills, active filter badges, job card locations, and Reddit community insights across all platforms and themes.


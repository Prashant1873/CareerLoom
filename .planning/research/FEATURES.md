# Features & Scope Analysis: Milestone v5.0

## Feature Breakdown

### 1. Table Stakes (Core Baseline)
- **SQLite Career Targets Registry (`career_targets`)**:
  - Persistent database table storing 200+ Indian companies (Startups, Unicorns, Established Conglomerates, Strategy Consulting firms).
  - Schema tracking company name, slug, tier, career URL, ATS provider, direct feed endpoint, role tags, sync health, last scraped timestamp, and active job count.
- **Reddit Company & Career URL Discovery Pipeline**:
  - Automated scanner mining Reddit communities (`r/developersIndia`, `r/IndianStartups`, `r/ProductManagement`, `r/consulting`, `r/bangalore`) for company names, hiring discussions, and career portal links.
  - LLM/Regex entity extraction to resolve mentions into normalized candidate company records.
- **Expansive Indian Ecosystem Ingestion**:
  - **High-Growth Startups & Unicorns (100+ firms)**: Zomato, Swiggy, Zepto, Blinkit, Razorpay, CRED, Meesho, Groww, PhonePe, Flipkart, Urban Company, Zerodha, Cleartax, Porter, Postman, BrowserStack, Hasura, etc.
  - **Established Indian Enterprises & Conglomerates (40+ firms)**: Tata Digital, Reliance Jio, Infosys, Wipro, TCS, HCL, L&T Technology Services, Mahindra, Titan, Aditya Birla Digital.
  - **Global & Tier-1 Strategy Consulting (40+ firms)**: McKinsey India, BCG India, Bain & Company India, Kearney, Roland Berger, Alvarez & Marsal, Strategy&, Monitor Deloitte, Arthur D. Little, Dalberg, Samagra, Zinnov.
- **Specialized Role Taxonomy & Classification**:
  - **Product Management Track**: Associate Product Manager (APM), Product Manager (PM), Senior PM (SPM), Group Product Manager (GPM), VP of Product, Technical PM (TPM), Product Operations.
  - **Strategy & Consulting Track**: Management Consultant, Strategy Analyst, Chief of Staff, Founder's Office, Business Operations (BizOps), Corporate Strategy, Growth Strategy.
- **Continuous Batch Ingestion Runner (`sync_batch.py`)**:
  - Bounded concurrency (`asyncio.Semaphore(15)`) to scrape all active targets in batches.
  - Stale job pruning: Automatically marks or archives job listings no longer found on the target career board.
  - Error isolation: Individual company failures do not halt batch execution.

### 2. Differentiators (High-Craft Experience)
- **Career Repository Directory Hub (Frontend UI)**:
  - Dedicated view / modal in the UI displaying all indexed companies, their verified career portals, ATS type badges, and total active listings.
  - Search and filter companies by sector (Startup, Enterprise, Consulting, Fintech) and role focus (Product, Strategy, Tech).
- **1-Click Strategy & PM Discovery Filters**:
  - Dedicated navigation pills and quick-filters in the left rail for "Product Management (India)" and "Strategy & Consulting (India)".
  - Role-specific card badges highlighting APM/PM and Strategy Consulting designations.
- **Live Sync Status Dashboard**:
  - Displays sync freshness indicator ("Updated 12 mins ago", "185 companies active", "4,200 live jobs").

### 3. Anti-Features & Out of Scope
- **Automated Job Applications**: Not building bot-based auto-apply; all apply buttons route cleanly to verified official company portals.
- **Paid Aggregator API Reliance**: No reliance on paid services (RapidAPI / JSearch); maintain 100% zero-cost architecture.
- **Heavy Enterprise Message Queues**: No Celery or Redis dependencies.

import asyncio
import json
import logging
from pathlib import Path
import sys

# Setup path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.db.database import init_db, upsert_jobs, get_connection
from backend.app.services.sync import JobSyncService

INDIAN_COMPANIES_CATALOG = [
    # Top Tier Indian Unicorns & Startups
    {"name": "Paytm", "slug": "paytm", "ats_type": "lever", "domain": "Fintech / Payments"},
    {"name": "CRED", "slug": "cred", "ats_type": "lever", "domain": "Fintech / Premium Credit"},
    {"name": "Meesho", "slug": "meesho", "ats_type": "lever", "domain": "Ecommerce / Social Commerce"},
    {"name": "Groww", "slug": "groww", "ats_type": "greenhouse", "domain": "Fintech / WealthTech"},
    {"name": "InMobi", "slug": "inmobi", "ats_type": "greenhouse", "domain": "AdTech / AI"},
    {"name": "Glance", "slug": "glance", "ats_type": "greenhouse", "domain": "Consumer Tech / AI"},
    {"name": "Freshworks", "slug": "freshworks", "ats_type": "smartrecruiters", "domain": "Enterprise SaaS"},
    {"name": "Slice", "slug": "slice", "ats_type": "greenhouse", "domain": "Fintech / Banking"},
    {"name": "Swiggy", "slug": "swiggy", "ats_type": "smartrecruiters", "domain": "Food Delivery & Quick Commerce"},
    {"name": "Porter", "slug": "porter", "ats_type": "lever", "domain": "Logistics & On-Demand Delivery"},
    {"name": "HackerRank", "slug": "hackerrank", "ats_type": "greenhouse", "domain": "Developer Tools & Assessment"},
    {"name": "Sarvam AI", "slug": "sarvam", "ats_type": "ashby", "domain": "Generative AI / Foundational Models"},
    {"name": "Atlan", "slug": "atlan", "ats_type": "ashby", "domain": "Data Governance & Metadata AI"},
    {"name": "Navi", "slug": "navi", "ats_type": "ashby", "domain": "Fintech / Digital Lending"},
    {"name": "Fi Money", "slug": "fi", "ats_type": "lever", "domain": "Fintech / Neo-Banking"},
    {"name": "Pocket FM", "slug": "pocketfm", "ats_type": "lever", "domain": "Audio OTT / Entertainment"},
    {"name": "Stage", "slug": "stage", "ats_type": "greenhouse", "domain": "Media & Dialect OTT"},
    {"name": "Lokal", "slug": "lokal", "ats_type": "smartrecruiters", "domain": "Hyperlocal News & Classifieds"},
    {"name": "Druva", "slug": "druva", "ats_type": "greenhouse", "domain": "Cloud Data Protection & Cyber Resilience"},
    {"name": "HighRadius", "slug": "highradius", "ats_type": "greenhouse", "domain": "Fintech SaaS / Autonomous Finance"},
    {"name": "Zenoti", "slug": "zenoti", "ats_type": "greenhouse", "domain": "Wellness & Spa Enterprise SaaS"},
    {"name": "Mindtickle", "slug": "mindtickle", "ats_type": "lever", "domain": "Sales Enablement SaaS"},
    {"name": "Kovai.co", "slug": "kovaico", "ats_type": "smartrecruiters", "domain": "Enterprise Cloud Management SaaS"},
    {"name": "SigNoz", "slug": "signoz", "ats_type": "ashby", "domain": "Open-Source APM & Observability"},
    {"name": "Zeta", "slug": "zeta", "ats_type": "lever", "domain": "Banking Tech / Next-Gen Core Banking"},
    {"name": "Bluestone", "slug": "bluestone", "ats_type": "greenhouse", "domain": "Omnichannel Fine Jewellery Tech"},
    {"name": "Thoughtworks India", "slug": "thoughtworks", "ats_type": "greenhouse", "domain": "Global Tech Engineering & Consulting"},
    {"name": "Truecaller India", "slug": "truecaller", "ats_type": "greenhouse", "domain": "Communications & Caller ID Tech"},
    {"name": "Instawork", "slug": "instawork", "ats_type": "greenhouse", "domain": "Flexible Work Marketplace"},
    {"name": "Acceldata", "slug": "acceldata", "ats_type": "lever", "domain": "Enterprise Data Observability"},
    {"name": "Entropik Tech", "slug": "entropik", "ats_type": "smartrecruiters", "domain": "Emotion & Cognitive AI"},
    {"name": "Captain Fresh", "slug": "captainfresh", "ats_type": "smartrecruiters", "domain": "B2B Supply Chain & Seafood Tech"},
    {"name": "NoBroker", "slug": "nobroker", "ats_type": "smartrecruiters", "domain": "PropTech & Real Estate Marketplace"},
    {"name": "InterviewBit", "slug": "interviewbit", "ats_type": "smartrecruiters", "domain": "EdTech & Tech Career Prep"},
    {"name": "Newton School", "slug": "newtonschool", "ats_type": "smartrecruiters", "domain": "EdTech Academy & Upskilling"},
    {"name": "Ixigo", "slug": "ixigo", "ats_type": "smartrecruiters", "domain": "Travel Tech & AI Booking"},
    {"name": "AbhiBus", "slug": "abhibus", "ats_type": "smartrecruiters", "domain": "Mobility & Bus Ticketing"},
    {"name": "Bounce", "slug": "bounce", "ats_type": "ashby", "domain": "Smart EV Mobility"},
    {"name": "River", "slug": "river", "ats_type": "ashby", "domain": "Electric Utility Mobility & Two-Wheelers"},
    {"name": "Vogo", "slug": "vogo", "ats_type": "lever", "domain": "Urban Scooter Sharing"},
    {"name": "Unacademy", "slug": "unacademy", "ats_type": "smartrecruiters", "domain": "EdTech Learning Platform"},
    {"name": "KredX", "slug": "kredx", "ats_type": "smartrecruiters", "domain": "Fintech / Supply Chain Financing"},
    {"name": "Lendingkart", "slug": "lendingkart", "ats_type": "smartrecruiters", "domain": "Fintech / MSME Lending"},
    {"name": "Turtlemint", "slug": "turtlemint", "ats_type": "smartrecruiters", "domain": "InsurTech Distribution"},
    {"name": "Cars24", "slug": "cars24", "ats_type": "smartrecruiters", "domain": "Used Cars Ecommerce & AutoTech"},
    {"name": "Whatfix", "slug": "whatfix", "ats_type": "smartrecruiters", "domain": "Digital Adoption Platform SaaS"},
]


async def merge_and_sync():
    companies_file = PROJECT_ROOT / "backend" / "app" / "data" / "companies.json"
    with open(companies_file, "r", encoding="utf-8") as f:
        existing = json.load(f)

    existing_slugs = {f"{c['slug']}:{c['ats_type']}" for c in existing}
    added_count = 0

    for item in INDIAN_COMPANIES_CATALOG:
        key = f"{item['slug']}:{item['ats_type']}"
        if key not in existing_slugs:
            existing.append(item)
            existing_slugs.add(key)
            added_count += 1

    with open(companies_file, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)

    print(f"Catalog updated! Added {added_count} Indian companies. Total in catalog: {len(existing)}")

    # Now run ingestion for all Indian companies
    await init_db()
    sync_service = JobSyncService()
    sem = asyncio.Semaphore(10)
    total_ingested = 0

    print(f"\nIngesting live listings for {len(INDIAN_COMPANIES_CATALOG)} Indian companies...")

    async def ingest_one(comp):
        nonlocal total_ingested
        name = comp["name"]
        slug = comp["slug"]
        ats_type = comp["ats_type"]
        domain = comp["domain"]

        connector = sync_service.connectors.get(ats_type)
        if not connector:
            return

        async with sem:
            try:
                jobs = await connector.fetch_jobs(company_name=name, company_slug=slug, domain=domain)
                if jobs:
                    # Enforce country = India if classified as Global
                    for j in jobs:
                        if j.country in ("Global", "Remote / Global"):
                            j.country = "India"
                    inserted = await upsert_jobs(jobs)
                    total_ingested += inserted
                    print(f"  [OK]   {name:<24} ({ats_type:<14}) -> {len(jobs)} jobs fetched, {inserted} inserted/updated", flush=True)
                else:
                    print(f"  [-]    {name:<24} ({ats_type:<14}) -> 0 jobs", flush=True)
            except Exception as e:
                print(f"  [FAIL] {name:<24} ({ats_type:<14}) -> Error: {e}", flush=True)

    await asyncio.gather(*[ingest_one(c) for c in INDIAN_COMPANIES_CATALOG])

    print(f"\nDone! Ingested total of {total_ingested} job listings from Indian startups and firms.")

    # Query database stats for India
    async with get_connection() as conn:
        async with conn.execute("SELECT COUNT(*) FROM jobs WHERE country = 'India'") as cur:
            row = await cur.fetchone()
            india_total = row[0] if row else 0

        async with conn.execute("SELECT COUNT(*) FROM jobs") as cur:
            row = await cur.fetchone()
            db_total = row[0] if row else 0

    print(f"\nUpdated SQLite Database Stats:")
    print(f"  Total listings in DB: {db_total:,}")
    print(f"  Total listings in India: {india_total:,}")


if __name__ == "__main__":
    asyncio.run(merge_and_sync())

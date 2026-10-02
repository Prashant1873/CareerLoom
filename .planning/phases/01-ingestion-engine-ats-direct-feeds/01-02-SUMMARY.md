# Plan 01-02 Summary: Direct ATS Connectors & UTC Date Normalizer

## Outcome

Successfully built and verified live ingestion connectors for the top 3 developer and enterprise ATS platforms:
- Universal date normalizer in [backend/app/utils/date_parser.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/utils/date_parser.py) that handles ISO 8601 strings, millisecond epoch timestamps (Lever), and relative strings ("2 days ago"), outputting timezone-aware UTC `datetime`.
- Role & location classification helper in [backend/app/utils/classifier.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/utils/classifier.py) that extracts canonical categories (`product`, `software_engineering`, `data_ai`, `design`, `finance_quant`, `consulting_strategy`), seniority levels (`entry`, `mid`, `senior`, `lead`, `intern`), and countries/remote flags.
- Base connector in [backend/app/scrapers/base.py](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/scrapers/base.py).
- [GreenhouseConnector](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/scrapers/greenhouse.py) verified live against Figma (163 jobs).
- [LeverConnector](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/scrapers/lever.py) verified live against Spotify (82 jobs).
- [AshbyConnector](file:///c:/Users/u1233270/Downloads/Personal%20Apps/Temporal%20Loom/backend/app/scrapers/ashby.py) verified live against Linear (30 jobs).

## Verification Evidence

- Live Greenhouse fetch: 163 jobs returned with UTC timestamps and verified application URLs.
- Live Lever fetch: 82 jobs returned with parsed epoch ms timestamps.
- Live Ashby fetch: 30 jobs returned with publishedAt timestamps and remote tags.
- Zero API keys or subscriptions required; 100% public JSON endpoints.

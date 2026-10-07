# Walking Skeleton: Phase 1 Ingestion Engine

## Purpose

Prove the thinnest possible end-to-end slice of the CareerLoom ingestion architecture before broad catalog expansion.

## Architecture Slice

```
[Public Greenhouse API: Figma] ──> [GreenhouseConnector] ──> [Universal Date Parser]
                                                                        │
                                                                        ▼
[Client: GET /api/jobs] <── [FastAPI Controller] <── [SQLite DB: jobs.db] <── [JobItem Normalizer]
```

## Proof Checkpoints

1. **Connector**: `GreenhouseConnector` fetches live JSON from `https://boards-api.greenhouse.io/v1/boards/figma/jobs`.
2. **Date Parser**: Converts ISO timestamps into timezone-aware UTC `datetime`.
3. **Database**: Upserts jobs into `data/jobs.db` with indexed `date_posted`.
4. **Endpoint**: `GET /api/jobs?limit=5` returns structured JSON with exact dates in under 50ms.

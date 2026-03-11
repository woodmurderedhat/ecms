# Expose Corruption with Machine Speed

ECMS (Exposure and Corruption Monitoring System) is a South Africa-focused platform for detecting suspicious procurement patterns and turning them into reviewable evidence.

The system combines automated ingestion, normalization, OCR, and anomaly scoring with a human verification and legal review process. The goal is not to publish accusations automatically, but to help investigators move faster from scattered records to defensible, privacy-aware evidence.

## The Ultimate Concept

The long-term concept is a trusted civic accountability engine that can:
- continuously monitor procurement and related public records at machine speed
- surface suspicious contract patterns early, with transparent scoring reasons
- preserve provenance and chain-of-custody metadata for auditability
- support analyst and legal workflows before any external publication

In practical terms, ECMS is designed as a full pipeline from raw public data to publication-ready evidence packages, with legal and privacy guardrails built into each stage.

## How The System Works

### 1. Ingest Source Data
`src/scheduler.py` runs fetch cycles and calls connectors under `src/ingest/` for configured sources such as eTender, municipal data resources, and gazette pages.

### 2. Normalize and Enrich Records
`src/pipeline.py` stores raw records, normalizes them into a unified contract shape via `src/etl/normalize.py`, and extracts document text when files are available using `src/ocr/extract.py`.

### 3. Score Irregularity Risk
The ML stage (`src/ml/features.py`, `src/ml/anomaly.py`) engineers features and applies baseline anomaly detection (Isolation Forest), then combines model output with rule-based reasons to compute `flag_score` and `flag_reasons`.

### 4. Create Analyst Cases
Contracts that meet case criteria are persisted as analyst cases in SQLite (`src/storage.py`). Cases are reviewed in the Flask API/UI layer (`src/ui/app.py`) where analysts update state, corroboration, and legal review status.

### 5. Build Evidence Packages
`src/evidence/package.py` creates redacted evidence exports. Packages are marked publication-ready only when corroboration and legal approval thresholds are met.

Architecture flow and automation context: `docs/architecture/overview.md`.

## Guardrails and Trust Model

ECMS is built to support responsible reporting, not automated accusation.

- Privacy: direct identifiers such as emails and South African ID-like numbers are redacted in evidence payloads.
- POPIA alignment: the project emphasizes data minimization and prefers organization-level procurement context where possible.
- Publication gating: evidence is considered ready only when at least two corroborating sources exist and legal review is approved.
- Auditability: transform logs and source references are retained to preserve provenance and reproducibility.

Policy details: `docs/DATA_PRIVACY.md`.

## Current Status and Scope

- End-to-end local workflow is implemented: ingest -> normalize/OCR -> score -> case management -> evidence packaging.
- Runtime source targets are configured in `config/default.json`.
- eTender ingestion runs out of the box with configured base URL.
- Municipal and gazette ingestion are connector-driven and activated by populating `municipal_resources` and `gazette_paths` in config.

## Quickstart

### Prerequisites
- Python 3.10+
- Node.js 20+
- Docker + Docker Compose (optional)

### Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm install
```

### Run checks
```bash
pytest -q
```

### Run one fetch-and-process cycle
```bash
python -m src.scheduler --config config/default.json
```

### Run recurring cycles locally
```bash
python -m src.scheduler --config config/default.json --interval-seconds 300 --max-cycles 20
```

### One-command local run
Start the analyst API/UI and scheduler together:

```bash
./scripts/run-local.sh
```

Optional environment variables:
- `ECMS_CONFIG_PATH` (default: `config/default.json`)
- `ECMS_UI_HOST` (default: `0.0.0.0`)
- `ECMS_UI_PORT` (default: `8000`)
- `ECMS_SCHED_INTERVAL_SECONDS` (default: `0`, run once)
- `ECMS_SCHED_MAX_CYCLES` (default: `1`)

Example recurring local run:

```bash
ECMS_SCHED_INTERVAL_SECONDS=300 ECMS_SCHED_MAX_CYCLES=20 ./scripts/run-local.sh
```

## Analyst Workflow API

- `GET /health`
- `GET /cases?limit=50`
- `GET /case/<id>`
- `PATCH /case/<id>` to update `state`, `legal_review_status`, `corroborating_sources`
- `GET /dashboard/summary`
- `POST /evidence/<case_id>`
- `GET /evidence/<case_id>`
- `GET /evidence/package/<package_id>`

Typical investigation flow:
1. Pull recent cases from `/cases`.
2. Update analyst and legal progression with `PATCH /case/<id>`.
3. Generate a redacted package using `POST /evidence/<case_id>`.
4. Verify `publication_ready` before any downstream external use.

## Repository Layout

- `src/ingest/`: source connectors and crawlers
- `src/etl/`: normalization and pipeline logic
- `src/ocr/`: OCR helpers for scanned documents
- `src/ml/`: feature engineering and anomaly scoring
- `src/ui/`: analyst-facing Flask application
- `src/evidence/`: evidence export and redaction logic
- `src/social/`: social/report template generation
- `data/schema/`: versioned data schemas
- `docs/`: architecture, governance, legal, and process documentation
- `.github/`: CI/CD workflows and collaboration templates

## Roadmap Snapshot

Near-term delivery tracks:
- strengthen source coverage across eTender, municipal, and gazette channels
- deepen model quality and feature richness for risk prioritization
- harden verification workflows, testing depth, and deployment posture

Full phased plan: `docs/ROADMAP.md`.

## Branching Model

- `main`: protected, release-ready
- `develop`: integration branch
- `feature/*`: feature work from `develop`
- `hotfix/*`: urgent fixes from `main`

## Contributing

See `CONTRIBUTING.md`.

## License

MIT. See `LICENSE`.

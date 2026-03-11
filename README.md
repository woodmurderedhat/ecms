# Expose Corruption with Machine Speed

A South Africa-focused platform for ingesting procurement and public finance data, detecting irregular patterns, and supporting analyst verification and evidence packaging.

## Project Overview
This repository contains a modular system for:
- ingesting data from eTender, municipal finance, and gazette sources
- transforming and normalizing records into a common schema
- scoring potential irregularities with ML and graph analytics
- reviewing flagged cases in a verification UI
- packaging evidence with privacy-preserving redaction

## Repository Layout
- `src/ingest/`: source connectors and crawlers
- `src/etl/`: normalization and pipeline logic
- `src/ocr/`: OCR helpers for scanned documents
- `src/ml/`: features, anomaly detection, entity resolution
- `src/ui/`: analyst-facing web application
- `src/evidence/`: export and redaction tools
- `src/social/`: social messaging and report templates
- `data/schema/`: versioned data schemas
- `docs/`: architecture, governance, legal, and process docs
- `.github/`: CI/CD workflows and collaboration templates

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

### Run live fetch cycle locally
Run one cycle and exit:

```bash
python -m src.scheduler --config config/default.json
```

Run repeatedly with a pause between cycles (local daemon-style):

```bash
python -m src.scheduler --config config/default.json --interval-seconds 300 --max-cycles 20
```

### One-command local run
Start the analyst UI and run the scheduler in one command:

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

### Analyst API endpoints
- `GET /health`
- `GET /cases?limit=50`
- `GET /case/<id>`
- `PATCH /case/<id>` (update `state`, `legal_review_status`, `corroborating_sources`)
- `GET /dashboard/summary`
- `POST /evidence/<case_id>`
- `GET /evidence/<case_id>`
- `GET /evidence/package/<package_id>`

## Branching Model
- `main`: protected, release-ready
- `develop`: integration branch
- `feature/*`: feature work from `develop`
- `hotfix/*`: urgent fixes from `main`

## Contributing
See `CONTRIBUTING.md`.

## License
MIT. See `LICENSE`.

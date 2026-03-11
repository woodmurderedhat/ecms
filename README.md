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

## Branching Model
- `main`: protected, release-ready
- `develop`: integration branch
- `feature/*`: feature work from `develop`
- `hotfix/*`: urgent fixes from `main`

## Contributing
See `CONTRIBUTING.md`.

## License
MIT. See `LICENSE`.

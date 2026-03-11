# Contributing Guide

## Workflow
1. Create an issue describing the change.
2. Branch from `develop` using `feature/<short-name>`.
3. Commit with clear messages (prefer Conventional Commits).
4. Open a pull request to `develop`.
5. Ensure CI checks pass and at least one reviewer approves.

## Development Standards
- Python style: PEP 8 + type hints for new modules.
- Testing: add or update tests for behavior changes.
- Docs: update docs for new config, API, and workflows.
- Security: do not commit secrets, credentials, or personal data.

## Local Commands
```bash
pip install -r requirements.txt
pytest -q
```

## Copilot Usage
- Include context-rich prompts with file names, input schema, and expected output.
- Validate generated code with tests and static checks.
- Prefer explicit error handling for data ingestion paths.

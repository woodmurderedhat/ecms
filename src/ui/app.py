"""Minimal Flask app for analyst case review."""

from __future__ import annotations

import os

from flask import Flask, jsonify, request

from src.evidence.package import package_case_evidence
from src.storage import Repository



def create_app(database_path: str | None = None) -> Flask:
    app = Flask(__name__)
    repository = Repository(database_path or os.environ.get("ECMS_DB_PATH", "data/ecms.db"))
    repository.initialize()

    @app.get("/health")
    def health() -> tuple[dict, int]:
        """Health endpoint for local checks and orchestrators."""
        return {"status": "ok"}, 200

    @app.get("/cases")
    def list_cases():
        """Return the most recent analyst cases."""
        limit = request.args.get("limit", default=50, type=int) or 50
        return jsonify({"items": repository.list_cases(limit=min(limit, 200))})

    @app.get("/case/<int:case_id>")
    def view_case(case_id: int):
        """Return one analyst case with its contract details."""
        case = repository.get_case(case_id)
        if case is None:
            return jsonify({"error": "case_not_found", "case_id": case_id}), 404
        return jsonify(case)

    @app.patch("/case/<int:case_id>")
    def update_case(case_id: int):
        """Update analyst-managed case fields such as state and legal status."""
        payload = request.get_json(silent=True) or {}
        case = repository.update_case(
            case_id,
            state=payload.get("state"),
            legal_review_status=payload.get("legal_review_status"),
            corroborating_sources=payload.get("corroborating_sources"),
        )
        if case is None:
            return jsonify({"error": "case_not_found", "case_id": case_id}), 404
        return jsonify(case)

    @app.get("/dashboard/summary")
    def dashboard_summary():
        """Return aggregate analyst workflow metrics for quick triage."""
        return jsonify(repository.get_case_summary())

    @app.post("/evidence/<int:case_id>")
    def create_evidence(case_id: int):
        """Create a fresh evidence package for a case and return payload metadata."""
        try:
            payload = package_case_evidence(case_id, repository)
        except KeyError:
            return jsonify({"error": "case_not_found", "case_id": case_id}), 404
        return jsonify(payload), 201

    @app.get("/evidence/<int:case_id>")
    def list_evidence(case_id: int):
        """List recent evidence package exports for a case."""
        limit = request.args.get("limit", default=10, type=int) or 10
        return jsonify({"items": repository.list_evidence_packages(case_id, limit=min(limit, 50))})

    @app.get("/evidence/package/<int:package_id>")
    def get_evidence(package_id: int):
        """Fetch one evidence package by package identifier."""
        package = repository.get_evidence_package(package_id)
        if package is None:
            return jsonify({"error": "package_not_found", "package_id": package_id}), 404
        return jsonify(package)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

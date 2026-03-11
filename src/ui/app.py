"""Minimal Flask app for analyst case review."""

from __future__ import annotations

from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/health")
def health() -> tuple[dict, int]:
    """Health endpoint for local checks and orchestrators."""
    return {"status": "ok"}, 200


@app.get("/case/<int:case_id>")
def view_case(case_id: int):
    """Temporary case endpoint until DB integration is added."""
    return jsonify({"case_id": case_id, "state": "pending_verification"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

"""Evidence packaging and privacy-aware redaction helpers."""

from __future__ import annotations

import re
from typing import Any

from src.storage import Repository


EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
SA_ID_PATTERN = re.compile(r"\b\d{13}\b")


def _publication_ready(case: dict[str, Any]) -> bool:
    return case["corroborating_sources"] >= 2 and case["legal_review_status"] == "approved"


def _document_excerpt(document_text: str, max_chars: int = 400) -> str:
    if not document_text:
        return ""
    excerpt = document_text[:max_chars].strip()
    return excerpt if len(document_text) <= max_chars else f"{excerpt}..."


def redact_text(raw: str) -> str:
    """Redact common direct identifiers from evidence text."""
    redacted = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", raw)
    return SA_ID_PATTERN.sub("[REDACTED_ID]", redacted)


def build_evidence_package(case: dict[str, Any]) -> dict[str, Any]:
    """Build a redacted evidence payload suitable for analyst review."""
    contract = case["contract"]
    supporting_text = contract.get("document_text") or contract.get("description") or ""
    narrative = (
        f"Supplier {contract['supplier']} was linked to tender {contract['tender_id']} "
        f"for buyer {contract['buyer_org']} at value R{contract['value']:,.2f}."
    )
    if contract.get("description"):
        narrative = f"{narrative} Description: {contract['description']}"

    return {
        "case_id": case["id"],
        "state": case["state"],
        "flag_score": case["flag_score"],
        "flag_reasons": case["flag_reasons"],
        "corroborating_sources": case["corroborating_sources"],
        "legal_review_status": case["legal_review_status"],
        "publication_ready": _publication_ready(case),
        "summary": redact_text(narrative),
        "document_excerpt": redact_text(_document_excerpt(supporting_text)),
        "contract": {
            "tender_id": contract["tender_id"],
            "buyer_org": contract["buyer_org"],
            "supplier": redact_text(contract["supplier"]),
            "award_date": contract["award_date"],
            "value": contract["value"],
            "currency": contract["currency"],
            "source_url": contract["source_url"],
        },
    }


def package_case_evidence(case_id: int, repository: Repository) -> dict[str, Any]:
    """Create and persist a redacted evidence package for a stored case."""
    case = repository.get_case(case_id)
    if case is None:
        raise KeyError(f"Unknown case_id: {case_id}")

    payload = build_evidence_package(case)
    export_status = "ready_for_publication" if payload["publication_ready"] else "draft"
    package_id = repository.create_evidence_package(case_id, payload, export_status=export_status)
    payload["package_id"] = package_id
    return payload

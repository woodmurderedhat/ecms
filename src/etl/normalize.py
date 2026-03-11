"""Normalization helpers for unified contracts records."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
from urllib.parse import urlparse


def normalize_currency(value: float, currency: str) -> tuple[float, str]:
    """Ensure currency defaults to ZAR and value is numeric."""
    return float(value), (currency or "ZAR").upper()


def _pick(data: dict[str, Any], *paths: str) -> Any:
    for path in paths:
        current: Any = data
        for part in path.split("."):
            if isinstance(current, list):
                if not current:
                    current = None
                    break
                current = current[0]
            if not isinstance(current, dict) or part not in current:
                current = None
                break
            current = current[part]
        if current not in (None, ""):
            return current
    return None


def _normalize_award_date(raw_value: Any) -> str:
    if isinstance(raw_value, datetime):
        return raw_value.date().isoformat()
    if isinstance(raw_value, date):
        return raw_value.isoformat()
    if raw_value is None:
        raise ValueError("award_date is required")
    text = str(raw_value).strip()
    if not text:
        raise ValueError("award_date is required")
    if "T" in text:
        text = text.split("T", 1)[0]
    return date.fromisoformat(text).isoformat()


def _normalize_flag_reasons(raw_value: Any) -> list[str]:
    if raw_value in (None, ""):
        return []
    if isinstance(raw_value, list):
        return [str(item).strip() for item in raw_value if str(item).strip()]
    return [str(raw_value).strip()]


def _require_text(value: Any, field_name: str) -> str:
    text = "" if value is None else str(value).strip()
    if not text:
        raise ValueError(f"{field_name} is required")
    return text


def _validate_source_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme and parsed.netloc:
        return value
    raise ValueError("source_url must be a valid absolute URL")


def _normalize_document_text(value: Any) -> str:
    if value in (None, ""):
        return ""
    return " ".join(str(value).split())


def normalize_contract_record(
    raw: dict[str, Any],
    source_url: str | None = None,
    document_text: str | None = None,
) -> dict[str, Any]:
    """Map source-specific procurement records into the canonical contract shape."""
    tender_id = _require_text(_pick(raw, "tender_id", "ocid", "id", "tender.id"), "tender_id")
    buyer_org = _require_text(_pick(raw, "buyer_org", "buyer.name", "buyer", "procuring_entity"), "buyer_org")
    supplier = _require_text(
        _pick(raw, "supplier", "supplier.name", "awards.suppliers.name", "award.suppliers.name"),
        "supplier",
    )
    award_date = _normalize_award_date(_pick(raw, "award_date", "date_awarded", "awards.date", "award.date"))
    raw_value = _pick(raw, "value", "amount", "awards.value.amount", "award.value.amount")
    value, currency = normalize_currency(raw_value, _pick(raw, "currency", "awards.value.currency", "award.value.currency"))
    canonical_source_url = _validate_source_url(
        _require_text(source_url or _pick(raw, "source_url", "url"), "source_url")
    )

    flag_score = _pick(raw, "flag_score")
    normalized: dict[str, Any] = {
        "tender_id": tender_id,
        "buyer_org": buyer_org,
        "supplier": supplier,
        "award_date": award_date,
        "value": value,
        "currency": currency,
        "description": _pick(raw, "description", "tender.title", "title") or "",
        "flag_score": float(flag_score) if flag_score is not None else None,
        "flag_reasons": _normalize_flag_reasons(_pick(raw, "flag_reasons", "risk_reasons")),
        "corroborating_sources": max(1, int(_pick(raw, "corroborating_sources") or 1)),
        "document_text": _normalize_document_text(document_text or _pick(raw, "document_text", "document_text_raw")),
        "source_url": canonical_source_url,
    }
    return normalized


def normalize_contract_batch(raw_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize a collection of raw records into the contracts schema."""
    return [normalize_contract_record(raw_record) for raw_record in raw_records]

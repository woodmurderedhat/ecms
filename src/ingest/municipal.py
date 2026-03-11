"""Connector stubs for municipal finance data sources."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import requests


def build_municipal_endpoint(base_url: str, resource: str) -> str:
    """Construct endpoint URL for a municipal API resource."""
    return f"{base_url.rstrip('/')}/{resource.lstrip('/')}"


def fetch_municipal_resource(
    base_url: str,
    resource: str,
    *,
    timeout: int = 30,
    params: dict[str, Any] | None = None,
    session: requests.sessions.Session | None = None,
) -> dict[str, Any]:
    """Fetch one municipal resource and return the decoded JSON payload."""
    url = build_municipal_endpoint(base_url, resource)
    client = session or requests
    response = client.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def _first_present(data: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = data.get(key)
        if value not in (None, ""):
            return value
    return None


def _coerce_municipal_items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    items = payload.get("items") or payload.get("results") or payload.get("data") or []
    if isinstance(items, list):
        return [item for item in items if isinstance(item, dict)]
    return []


def parse_municipal_contract_records(payload: Any, resource: str, source_url: str) -> list[dict[str, Any]]:
    """Parse municipal source payloads into canonical contract-like records."""
    records: list[dict[str, Any]] = []
    for index, item in enumerate(_coerce_municipal_items(payload), start=1):
        tender_id = _first_present(
            item,
            "tender_id",
            "tender_number",
            "tenderNumber",
            "contract_id",
            "reference_number",
            "referenceNumber",
            "id",
        )
        buyer_org = _first_present(
            item,
            "buyer_org",
            "municipality",
            "municipality_name",
            "department",
            "entity_name",
            "procuring_entity",
            "institution",
        )
        supplier = _first_present(
            item,
            "supplier",
            "supplier_name",
            "vendor",
            "vendor_name",
            "awarded_to",
            "beneficiary",
        )
        award_date = _first_present(item, "award_date", "date_awarded", "awardDate", "date", "created_at")
        value = _first_present(item, "value", "amount", "award_value", "total_amount", "contract_value")

        if tender_id in (None, "") or buyer_org in (None, "") or supplier in (None, "") or value in (None, ""):
            continue

        records.append(
            {
                "tender_id": str(tender_id),
                "buyer_org": str(buyer_org),
                "supplier": str(supplier),
                "award_date": str(award_date or datetime.now(tz=UTC).date().isoformat()),
                "value": value,
                "currency": str(_first_present(item, "currency", "currency_code") or "ZAR"),
                "description": str(
                    _first_present(item, "description", "project_description", "title", "contract_description") or ""
                ),
                "source_url": f"{source_url}#record-{index}",
                "corroborating_sources": int(_first_present(item, "corroborating_sources") or 1),
                "flag_reasons": item.get("flag_reasons") or [],
                "flag_score": item.get("flag_score"),
                "source_resource": resource,
            }
        )
    return records

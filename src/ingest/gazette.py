"""Live helpers for fetching South African gazette pages."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any

import requests


TENDER_PATTERN = re.compile(r"\b(?:RFP|RFQ|BID|TN|CONTRACT)[-\s]*([A-Z0-9]{2,})\b", re.IGNORECASE)
BUYER_PATTERN = re.compile(r"(?:municipality|department|city|province)\s+of\s+([A-Za-z0-9\-\s]+)", re.IGNORECASE)
SUPPLIER_PATTERN = re.compile(
    r"(?:awarded\s+to|supplier\s*[:\-])\s*([A-Za-z0-9&.,'\-\s]+?)(?:\s+for\s+|\s+value\s+|\s+on\s+|\.|$)",
    re.IGNORECASE,
)
VALUE_PATTERN = re.compile(r"R\s*([0-9][0-9,\s]*(?:\.\d{1,2})?)", re.IGNORECASE)
DATE_PATTERN = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")


def fetch_gazette_page(
    base_url: str,
    path: str = "/",
    *,
    timeout: int = 30,
    params: dict[str, Any] | None = None,
    session: requests.sessions.Session | None = None,
) -> str:
    """Fetch a gazette page and return the raw HTML body."""
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    client = session or requests
    response = client.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.text


def _clean_html_text(html: str) -> str:
    without_scripts = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.IGNORECASE)
    without_styles = re.sub(r"<style[\s\S]*?</style>", " ", without_scripts, flags=re.IGNORECASE)
    plain = re.sub(r"<[^>]+>", " ", without_styles)
    return " ".join(plain.split())


def _split_notices(text: str) -> list[str]:
    parts = re.split(r"(?=\b(?:RFP|RFQ|BID|CONTRACT|TENDER)\b)", text, flags=re.IGNORECASE)
    return [part.strip() for part in parts if part.strip()]


def parse_gazette_contract_records(html: str, source_url: str) -> list[dict[str, Any]]:
    """Extract contract-like records from gazette notices."""
    cleaned = _clean_html_text(html)
    records: list[dict[str, Any]] = []
    for index, notice in enumerate(_split_notices(cleaned), start=1):
        tender_match = TENDER_PATTERN.search(notice)
        value_match = VALUE_PATTERN.search(notice)
        if tender_match is None or value_match is None:
            continue

        supplier_match = SUPPLIER_PATTERN.search(notice)
        buyer_match = BUYER_PATTERN.search(notice)
        date_match = DATE_PATTERN.search(notice)
        value_text = value_match.group(1).replace(",", "").replace(" ", "")
        try:
            value = float(value_text)
        except ValueError:
            continue

        records.append(
            {
                "tender_id": f"GAZ-{tender_match.group(1).upper()}",
                "buyer_org": buyer_match.group(1).strip() if buyer_match else "Unknown Gazette Buyer",
                "supplier": supplier_match.group(1).strip() if supplier_match else "Unknown Supplier",
                "award_date": date_match.group(1) if date_match else datetime.now(tz=UTC).date().isoformat(),
                "value": value,
                "currency": "ZAR",
                "description": notice[:400],
                "source_url": f"{source_url}#notice-{index}",
                "corroborating_sources": 1,
            }
        )
    return records
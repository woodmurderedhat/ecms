"""Ingestion helpers for South Africa eTender OCDS releases."""

from __future__ import annotations

import requests


def fetch_etender_page(base_url: str, page: int = 1, timeout: int = 30) -> dict:
    """Fetch one page of OCDS releases and return JSON payload."""
    url = f"{base_url.rstrip('/')}/releases?page={page}"
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()

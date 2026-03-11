"""Ingestion helpers for South Africa eTender OCDS releases."""

from __future__ import annotations

from typing import Any, Iterable

import requests


def fetch_etender_page(
    base_url: str,
    page: int = 1,
    timeout: int = 30,
    session: requests.sessions.Session | None = None,
) -> dict[str, Any]:
    """Fetch one page of OCDS releases and return JSON payload."""
    url = f"{base_url.rstrip('/')}/releases?page={page}"
    client = session or requests
    response = client.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()


def iter_etender_releases(
    base_url: str,
    start_page: int = 1,
    max_pages: int | None = None,
    timeout: int = 30,
    session: requests.sessions.Session | None = None,
) -> Iterable[dict[str, Any]]:
    """Yield OCDS release objects across sequential pages."""
    page = start_page
    pages_fetched = 0

    while True:
        payload = fetch_etender_page(base_url, page=page, timeout=timeout, session=session)
        releases = payload.get("releases") or payload.get("results") or payload.get("data") or []
        if not releases:
            break

        for release in releases:
            yield release

        pages_fetched += 1
        if max_pages is not None and pages_fetched >= max_pages:
            break

        next_page = payload.get("next_page") or payload.get("nextPage")
        if next_page in (None, False, ""):
            break
        page = int(next_page) if next_page is not True else page + 1


def fetch_etender_releases(
    base_url: str,
    start_page: int = 1,
    max_pages: int | None = None,
    timeout: int = 30,
    session: requests.sessions.Session | None = None,
) -> list[dict[str, Any]]:
    """Collect OCDS releases across one or more pages."""
    return list(
        iter_etender_releases(
            base_url=base_url,
            start_page=start_page,
            max_pages=max_pages,
            timeout=timeout,
            session=session,
        )
    )

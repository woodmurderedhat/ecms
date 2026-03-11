"""Connector stubs for municipal finance data sources."""

from __future__ import annotations


def build_municipal_endpoint(base_url: str, resource: str) -> str:
    """Construct endpoint URL for a municipal API resource."""
    return f"{base_url.rstrip('/')}/{resource.lstrip('/')}"

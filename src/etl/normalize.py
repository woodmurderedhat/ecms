"""Normalization helpers for unified contracts records."""

from __future__ import annotations


def normalize_currency(value: float, currency: str) -> tuple[float, str]:
    """Ensure currency defaults to ZAR and value is numeric."""
    return float(value), (currency or "ZAR").upper()

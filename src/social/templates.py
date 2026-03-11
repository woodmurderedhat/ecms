"""Social post template rendering helpers."""

from __future__ import annotations


def render_alert(company: str, amount_zar: float) -> str:
    """Create a short alert string for verified findings."""
    return (
        f"ALERT: Suspected irregularity detected. "
        f"{company} linked to contract value R{amount_zar:,.2f}."
    )

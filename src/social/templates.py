"""Social post template rendering helpers."""

from __future__ import annotations

from typing import Any


def render_alert(company: str, amount_zar: float) -> str:
    """Create a short alert string for verified findings."""
    return (
        f"ALERT: Suspected irregularity detected. "
        f"{company} linked to contract value R{amount_zar:,.2f}."
    )


def render_case_alert(case: dict[str, Any]) -> str:
    """Render a public-facing alert only for publication-ready cases."""
    if case["corroborating_sources"] < 2:
        raise ValueError("At least two corroborating sources are required before publication")
    if case["legal_review_status"] != "approved":
        raise ValueError("Legal review approval is required before publication")
    contract = case["contract"]
    return render_alert(contract["supplier"], float(contract["value"]))

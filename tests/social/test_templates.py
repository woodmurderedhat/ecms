import pytest

from src.social.templates import render_case_alert


def test_render_case_alert_requires_publication_guards():
    case = {
        "corroborating_sources": 1,
        "legal_review_status": "pending",
        "contract": {"supplier": "Example Co", "value": 1234.0},
    }

    with pytest.raises(ValueError):
        render_case_alert(case)


def test_render_case_alert_for_ready_case():
    case = {
        "corroborating_sources": 2,
        "legal_review_status": "approved",
        "contract": {"supplier": "Example Co", "value": 1234.0},
    }

    message = render_case_alert(case)

    assert "Example Co" in message
    assert "R1,234.00" in message
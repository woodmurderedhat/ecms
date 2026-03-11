from src.evidence.package import build_evidence_package, package_case_evidence, redact_text
from src.pipeline import run_contract_pipeline
from src.storage import Repository


def test_redact_text_masks_emails_and_sa_ids():
    text = "Contact person@example.org with ID 9001011234088"

    redacted = redact_text(text)

    assert "person@example.org" not in redacted
    assert "9001011234088" not in redacted
    assert "[REDACTED_EMAIL]" in redacted
    assert "[REDACTED_ID]" in redacted


def test_build_evidence_package_marks_publication_gate():
    case = {
        "id": 4,
        "state": "pending_verification",
        "flag_score": 0.8,
        "flag_reasons": ["repeat_supplier"],
        "corroborating_sources": 1,
        "legal_review_status": "pending",
        "contract": {
            "tender_id": "TN-2",
            "buyer_org": "Metro",
            "supplier": "Vendor 9001011234088",
            "award_date": "2026-03-03",
            "value": 5000.0,
            "currency": "ZAR",
            "description": "Review person@example.org",
            "source_url": "https://example.org/TN-2",
        },
    }

    payload = build_evidence_package(case)

    assert payload["publication_ready"] is False
    assert "9001011234088" not in payload["contract"]["supplier"]
    assert "person@example.org" not in payload["summary"]
    assert payload["document_excerpt"]


def test_package_case_evidence_persists_payload(tmp_path):
    repository = Repository(tmp_path / "evidence.db")
    result = run_contract_pipeline(
        source_name="etenders",
        raw_records=[
            {
                "tender_id": "TN-9",
                "buyer_org": "Metro Municipality",
                "supplier": "Roadworks Ltd",
                "award_date": "2026-03-02",
                "value": 9800000,
                "currency": "ZAR",
                "description": "Road resurfacing",
                "source_url": "https://example.org/contracts/TN-9",
                "flag_score": 0.91,
                "flag_reasons": ["single_bidder"],
                "corroborating_sources": 2,
            }
        ],
        repository=repository,
    )

    with repository.connection() as conn:
        conn.execute(
            "UPDATE cases SET legal_review_status = 'approved' WHERE id = ?",
            (result.case_ids[0],),
        )

    payload = package_case_evidence(result.case_ids[0], repository)
    stored_package = repository.get_evidence_package(payload["package_id"])

    assert payload["publication_ready"] is True
    assert stored_package is not None
    assert stored_package["export_status"] == "ready_for_publication"
from src.pipeline import run_contract_pipeline
from src.storage import Repository


def test_run_contract_pipeline_persists_case(tmp_path):
    repository = Repository(tmp_path / "ecms.db")
    result = run_contract_pipeline(
        source_name="etenders",
        raw_records=[
            {
                "tender_id": "TN-001",
                "buyer_org": "Metro Municipality",
                "supplier": "Roadworks Ltd",
                "award_date": "2026-03-02",
                "value": 9800000,
                "currency": "ZAR",
                "description": "Road resurfacing",
                "source_url": "https://example.org/contracts/TN-001",
                "flag_score": 0.91,
                "flag_reasons": ["single_bidder"],
                "corroborating_sources": 2,
            }
        ],
        repository=repository,
    )

    assert result.processed_count == 1
    assert len(result.case_ids) == 1

    case = repository.get_case(result.case_ids[0])
    assert case is not None
    assert case["state"] == "pending_verification"
    assert case["corroborating_sources"] == 2
    assert case["contract"]["supplier"] == "Roadworks Ltd"


def test_run_contract_pipeline_creates_case_from_computed_signals(tmp_path):
    document_path = tmp_path / "notice.txt"
    document_path.write_text("Urgent deviation and extension approved", encoding="utf-8")
    repository = Repository(tmp_path / "computed.db")

    result = run_contract_pipeline(
        source_name="etenders",
        raw_records=[
            {
                "tender_id": "TN-101",
                "buyer_org": "Metro Municipality",
                "supplier": "Roadworks Ltd",
                "award_date": "2026-03-02",
                "value": 100000,
                "currency": "ZAR",
                "source_url": "https://example.org/contracts/TN-101",
                "document_path": str(document_path),
                "corroborating_sources": 1,
            },
            {
                "tender_id": "TN-102",
                "buyer_org": "Metro Municipality",
                "supplier": "Roadworks Ltd",
                "award_date": "2026-03-03",
                "value": 9000000,
                "currency": "ZAR",
                "source_url": "https://example.org/contracts/TN-102",
                "corroborating_sources": 1,
            },
        ],
        repository=repository,
    )

    assert result.case_ids
    case = repository.get_case(result.case_ids[0])
    assert case is not None
    assert case["flag_reasons"]
    assert case["contract"]["document_text"]

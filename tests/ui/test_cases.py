from src.pipeline import run_contract_pipeline
from src.storage import Repository
from src.ui.app import create_app


def test_case_route_returns_persisted_case(tmp_path):
    database_path = tmp_path / "ui.db"
    repository = Repository(database_path)
    result = run_contract_pipeline(
        source_name="municipal",
        raw_records=[
            {
                "tender_id": "MUN-7",
                "buyer_org": "Example District",
                "supplier": "Water Services Co",
                "award_date": "2026-02-12",
                "value": 450000,
                "currency": "ZAR",
                "source_url": "https://example.org/contracts/MUN-7",
                "flag_score": 0.67,
                "flag_reasons": ["repeat_supplier"],
            }
        ],
        repository=repository,
    )

    app = create_app(str(database_path))
    client = app.test_client()

    response = client.get(f"/case/{result.case_ids[0]}")

    assert response.status_code == 200
    assert response.json["contract"]["tender_id"] == "MUN-7"
    assert "repeat_supplier" in response.json["flag_reasons"]


def test_cases_route_returns_collection(tmp_path):
    database_path = tmp_path / "ui-list.db"
    repository = Repository(database_path)
    run_contract_pipeline(
        source_name="municipal",
        raw_records=[
            {
                "tender_id": "MUN-8",
                "buyer_org": "Example District",
                "supplier": "Water Services Co",
                "award_date": "2026-02-15",
                "value": 250000,
                "currency": "ZAR",
                "source_url": "https://example.org/contracts/MUN-8",
                "flag_score": 0.72,
                "flag_reasons": ["value_spike"],
            }
        ],
        repository=repository,
    )

    app = create_app(str(database_path))
    client = app.test_client()

    response = client.get("/cases")

    assert response.status_code == 200
    assert len(response.json["items"]) == 1
    assert response.json["items"][0]["contract"]["tender_id"] == "MUN-8"
from src.pipeline import run_contract_pipeline
from src.storage import Repository
from src.ui.app import create_app


def _seed_case(database_path):
    repository = Repository(database_path)
    result = run_contract_pipeline(
        source_name="etenders",
        raw_records=[
            {
                "tender_id": "TN-300",
                "buyer_org": "Metro Municipality",
                "supplier": "Alpha Works",
                "award_date": "2026-03-10",
                "value": 1250000,
                "currency": "ZAR",
                "description": "Roads upgrade",
                "source_url": "https://example.org/contracts/TN-300",
                "corroborating_sources": 2,
                "flag_score": 0.77,
                "flag_reasons": ["repeat_supplier"],
            }
        ],
        repository=repository,
    )
    return repository, result.case_ids[0]


def test_dashboard_and_evidence_endpoints(tmp_path):
    database_path = tmp_path / "ui-evidence.db"
    repository, case_id = _seed_case(database_path)
    with repository.connection() as conn:
        conn.execute("UPDATE cases SET legal_review_status = 'approved' WHERE id = ?", (case_id,))

    app = create_app(str(database_path))
    client = app.test_client()

    summary = client.get("/dashboard/summary")
    assert summary.status_code == 200
    assert summary.json["total_cases"] == 1

    created = client.post(f"/evidence/{case_id}")
    assert created.status_code == 201
    package_id = created.json["package_id"]

    listed = client.get(f"/evidence/{case_id}")
    assert listed.status_code == 200
    assert listed.json["items"]
    assert listed.json["items"][0]["id"] == package_id

    fetched = client.get(f"/evidence/package/{package_id}")
    assert fetched.status_code == 200
    assert fetched.json["id"] == package_id


def test_patch_case_route_updates_case(tmp_path):
    database_path = tmp_path / "ui-update.db"
    _, case_id = _seed_case(database_path)

    app = create_app(str(database_path))
    client = app.test_client()

    response = client.patch(
        f"/case/{case_id}",
        json={"state": "under_review", "legal_review_status": "approved", "corroborating_sources": 3},
    )
    assert response.status_code == 200
    assert response.json["state"] == "under_review"
    assert response.json["legal_review_status"] == "approved"
    assert response.json["corroborating_sources"] == 3
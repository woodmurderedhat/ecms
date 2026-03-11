from src.etl.normalize import normalize_contract_record


def test_normalize_contract_record_maps_nested_fields():
    raw_record = {
        "ocid": "ocds-123",
        "buyer": {"name": "City of Example"},
        "awards": [
            {
                "date": "2026-03-01T12:34:56Z",
                "suppliers": [{"name": "Example Supplier"}],
                "value": {"amount": 125000.0, "currency": "zar"},
            }
        ],
        "title": "Waste removal services",
        "flag_score": 0.88,
        "flag_reasons": ["high_value", "repeat_supplier"],
        "url": "https://example.org/releases/ocds-123",
    }

    normalized = normalize_contract_record(raw_record)

    assert normalized["tender_id"] == "ocds-123"
    assert normalized["buyer_org"] == "City of Example"
    assert normalized["supplier"] == "Example Supplier"
    assert normalized["award_date"] == "2026-03-01"
    assert normalized["value"] == 125000.0
    assert normalized["currency"] == "ZAR"
    assert normalized["flag_reasons"] == ["high_value", "repeat_supplier"]

from src.ingest.gazette import parse_gazette_contract_records
from src.ingest.municipal import parse_municipal_contract_records


def test_parse_municipal_contract_records_maps_source_payload():
    payload = {
        "items": [
            {
                "tenderNumber": "MUN-123",
                "municipality": "Cape District",
                "vendor_name": "Water Works Ltd",
                "awardDate": "2026-03-01",
                "total_amount": 420000.0,
                "currency": "ZAR",
                "project_description": "Water treatment upgrade",
            }
        ]
    }

    records = parse_municipal_contract_records(payload, resource="awards", source_url="https://municipal.example/awards")

    assert len(records) == 1
    assert records[0]["tender_id"] == "MUN-123"
    assert records[0]["buyer_org"] == "Cape District"
    assert records[0]["supplier"] == "Water Works Ltd"
    assert records[0]["value"] == 420000.0


def test_parse_gazette_contract_records_extracts_contract_like_notice():
    html = """
    <html><body>
      <p>Contract BID-778 awarded to Alpha Civils for City of eThekwini value R 1,250,000 on 2026-02-14.</p>
    </body></html>
    """

    records = parse_gazette_contract_records(html, source_url="https://gazette.example/notices")

    assert len(records) == 1
    assert records[0]["tender_id"] == "GAZ-778"
    assert records[0]["supplier"].startswith("Alpha Civils")
    assert records[0]["value"] == 1250000.0
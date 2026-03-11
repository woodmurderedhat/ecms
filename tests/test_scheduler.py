import json

from src.scheduler import run_recurring, run_scheduled_cycle
from src.storage import Repository


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload
        self.text = payload if isinstance(payload, str) else ""

    def raise_for_status(self):
        return None

    def json(self):
        if isinstance(self._payload, str):
            raise ValueError("No JSON payload")
        return self._payload


class _FakeSession:
    def __init__(self, payloads):
        self.payloads = payloads

    def get(self, url, timeout=30, params=None):
        return _FakeResponse(self.payloads.pop(0))


def test_run_scheduled_cycle_pulls_live_records_into_pipeline(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "environment": "test",
                "sources": {
                    "etender_base_url": "https://example.org/api",
                    "municipal_data_url": "https://municipal.example",
                    "gazette_url": "https://gazette.example",
                    "municipal_resources": ["awards"],
                    "gazette_paths": ["/notices"],
                },
                "pipeline": {
                    "poll_interval_minutes": 60,
                    "score_threshold": 0.4,
                    "request_timeout_seconds": 5,
                    "etender_max_pages": 1,
                },
            }
        ),
        encoding="utf-8",
    )
    session = _FakeSession(
        [
            {
                "releases": [
                    {
                        "tender_id": "TN-201",
                        "buyer_org": "Metro",
                        "supplier": "Vendor",
                        "award_date": "2026-03-04",
                        "value": 700000.0,
                        "currency": "ZAR",
                        "source_url": "https://example.org/contracts/TN-201",
                        "document_text": "Emergency extension approved",
                        "corroborating_sources": 1,
                    }
                ]
            },
            {
                "items": [
                    {
                        "tenderNumber": "MUN-201",
                        "municipality": "Metro",
                        "vendor_name": "Vendor Two",
                        "awardDate": "2026-03-05",
                        "total_amount": 900000,
                        "currency": "ZAR",
                    }
                ]
            },
            "<html><body><p>Contract BID-301 awarded to Vendor Three for City of Metro value R 850,000 on 2026-03-05.</p></body></html>",
        ]
    )

    result = run_scheduled_cycle(
        config_path=config_path,
        repository=Repository(tmp_path / "scheduler.db"),
        session=session,
    )

    assert result["environment"] == "test"
    assert len(result["sources"]) == 3
    assert result["sources"][0]["processed_count"] == 1
    assert result["sources"][1]["processed_count"] == 1
    assert result["sources"][2]["processed_count"] == 1


def test_run_recurring_respects_max_cycles(tmp_path):
    config_path = tmp_path / "config-recurring.json"
    config_path.write_text(
        json.dumps(
            {
                "environment": "test",
                "sources": {
                    "etender_base_url": "https://example.org/api",
                    "municipal_data_url": "https://municipal.example",
                    "gazette_url": "https://gazette.example",
                    "municipal_resources": [],
                    "gazette_paths": [],
                },
                "pipeline": {
                    "poll_interval_minutes": 60,
                    "score_threshold": 0.4,
                    "request_timeout_seconds": 5,
                    "etender_max_pages": 1,
                },
            }
        ),
        encoding="utf-8",
    )
    session = _FakeSession([{"releases": []}, {"releases": []}])

    results = run_recurring(
        config_path=config_path,
        interval_seconds=0,
        max_cycles=2,
        repository=Repository(tmp_path / "scheduler-recurring.db"),
        session=session,
    )

    assert len(results) == 1
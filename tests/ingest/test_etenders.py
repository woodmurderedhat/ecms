from src.ingest.etenders import fetch_etender_releases


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class _FakeSession:
    def __init__(self, payloads):
        self.payloads = payloads
        self.urls = []

    def get(self, url, timeout):
        self.urls.append(url)
        return _FakeResponse(self.payloads.pop(0))


def test_fetch_etender_releases_follows_next_page_marker():
    session = _FakeSession(
        [
            {"releases": [{"ocid": "one"}], "next_page": 2},
            {"releases": [{"ocid": "two"}]},
        ]
    )

    releases = fetch_etender_releases("https://example.org/api", session=session)

    assert [release["ocid"] for release in releases] == ["one", "two"]
    assert session.urls == [
        "https://example.org/api/releases?page=1",
        "https://example.org/api/releases?page=2",
    ]
from src.ingest.municipal import build_municipal_endpoint, fetch_municipal_resource


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class _FakeSession:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def get(self, url, params, timeout):
        self.calls.append({"url": url, "params": params, "timeout": timeout})
        return _FakeResponse(self.payload)


def test_build_municipal_endpoint_trims_slashes():
    assert build_municipal_endpoint("https://municipal.example/", "/votes") == "https://municipal.example/votes"


def test_fetch_municipal_resource_uses_built_endpoint_and_params():
    session = _FakeSession({"items": [1, 2]})

    payload = fetch_municipal_resource(
        "https://municipal.example/",
        "/votes",
        params={"year": 2026},
        session=session,
    )

    assert payload == {"items": [1, 2]}
    assert session.calls == [
        {
            "url": "https://municipal.example/votes",
            "params": {"year": 2026},
            "timeout": 30,
        }
    ]
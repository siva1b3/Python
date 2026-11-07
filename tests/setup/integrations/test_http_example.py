"""Toy test using a mock HTTP service."""

import httpx


def test_http_client_reads_mock_response() -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/status"
        return httpx.Response(200, json={"status": "ok"})

    with httpx.Client(
        base_url="https://example.test", transport=httpx.MockTransport(respond)
    ) as client:
        response = client.get("/status")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

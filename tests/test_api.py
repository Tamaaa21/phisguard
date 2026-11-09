"""Integration tests for PhishGuard FastAPI endpoints."""

from __future__ import annotations

import time
from fastapi.testclient import TestClient
import numpy as np
import pytest

from src.api.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model_loaded"] is True
    assert "version" in data


def test_model_info_endpoint():
    response = client.get("/api/model-info")
    assert response.status_code == 200
    data = response.json()
    assert "model_name" in data
    assert "model_version" in data
    assert data["feature_count"] == 49
    assert "metrics_test" in data
    assert "metrics_validation" in data
    assert len(data["top_features"]) > 0


def test_check_legitimate_url():
    payload = {"url": "https://www.google.com/search?q=fastapi"}
    response = client.post("/api/check", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["url"] == payload["url"]
    assert data["label"] == "legitimate"
    assert data["risk_level"] in ["low", "medium"]
    assert 0.0 <= data["score"] <= 1.0
    assert isinstance(data["reasons"], list)
    assert len(data["reasons"]) > 0
    assert "disclaimer" in data
    assert len(data["disclaimer"]) > 10


def test_check_phishing_url():
    payload = {"url": "http://paypal.com.verification-security-update.xyz/login?token=938472938472394872"}
    response = client.post("/api/check", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["url"] == payload["url"]
    assert data["label"] == "phishing"
    assert data["risk_level"] in ["medium", "high"]
    assert data["score"] >= 0.50
    assert isinstance(data["reasons"], list)
    assert len(data["reasons"]) > 0
    assert any("subdomain" in r.lower() or "merek" in r.lower() or "sensitif" in r.lower() for r in data["reasons"])


def test_check_url_too_long_413():
    long_url = "https://example.com/" + "a" * 2100
    response = client.post("/api/check", json={"url": long_url})
    assert response.status_code == 413
    assert "terlalu panjang" in response.json()["detail"].lower()


def test_check_empty_url_400():
    response = client.post("/api/check", json={"url": "    "})
    assert response.status_code == 400
    assert "tidak boleh kosong" in response.json()["detail"].lower()


def test_check_unsupported_scheme_400():
    for bad_scheme in ["javascript:alert(1)", "ftp://example.com/file", "data:text/html,<html>"]:
        response = client.post("/api/check", json={"url": bad_scheme})
        assert response.status_code == 400
        assert "skema" in response.json()["detail"].lower()


def test_check_no_host_400():
    response = client.post("/api/check", json={"url": "http://"})
    assert response.status_code == 400
    assert "host" in response.json()["detail"].lower() or "domain" in response.json()["detail"].lower()


def test_check_latency_p95_under_500ms():
    test_urls = [
        "https://www.google.com",
        "https://bankmandiri.co.id/personal",
        "http://paypal.com.account-update.xyz/login",
        "https://github.com/tiangolo/fastapi",
        "http://192.168.1.1/admin",
    ]

    # Warmup
    client.post("/api/check", json={"url": test_urls[0]})

    durations = []
    for _ in range(6):
        for u in test_urls:
            t0 = time.perf_counter()
            resp = client.post("/api/check", json={"url": u})
            durations.append((time.perf_counter() - t0) * 1000)
            assert resp.status_code == 200

    p95 = np.percentile(durations, 95)
    avg_latency = np.mean(durations)
    print(f"\n[LATENCY BENCHMARK] Mean: {avg_latency:.2f} ms | p95: {p95:.2f} ms across {len(durations)} calls")
    assert p95 < 500.0, f"p95 latency exceeded 500 ms: {p95:.2f} ms"


def test_frontend_index_and_static_assets():
    """Verify that root endpoint serves the HTML frontend and static assets are accessible."""
    # Test root endpoint
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    html_content = response.text
    assert "PhishGuard" in html_content
    assert "resultUrl" in html_content
    # Ensure there is NO <a href="{{url}}"> or similar dangerous link rendering in the UI template
    assert '<a id="resultUrl"' not in html_content
    assert '<a href=' not in html_content.split('id="resultUrl"')[0][-100:]

    # Test static assets
    css_resp = client.get("/static/style.css")
    assert css_resp.status_code == 200
    assert "text/css" in css_resp.headers.get("content-type", "")

    js_resp = client.get("/static/app.js")
    assert js_resp.status_code == 200
    assert "javascript" in js_resp.headers.get("content-type", "")


"""Security, rate limiting, and robustness test suite for PhishGuard (M09)."""

from __future__ import annotations

import json
from pathlib import Path
import socket
from unittest.mock import patch

from fastapi.testclient import TestClient
import pytest

from src.api.main import app, sanitize_url_for_logging
from src.api.rate_limiter import InMemoryRateLimiter, limiter

client = TestClient(app)


def test_zero_ssrf_guarantee_no_outbound_network_calls():
    """
    STRICT ZERO-SSRF VERIFICATION:
    Ensure backend never attempts any outbound HTTP requests or connections to the inspected URL.
    """
    with patch("http.client.HTTPConnection.connect") as mock_http, \
         patch("http.client.HTTPSConnection.connect") as mock_https, \
         patch("urllib.request.urlopen") as mock_urlopen:

        # Pass a target URL that looks like an active phishing domain
        payload = {"url": "http://evil-credential-harvester-target.xyz/login"}
        response = client.post("/api/check", json=payload)

        assert response.status_code == 200
        # Assert no outbound HTTP/HTTPS connections were initiated
        assert mock_http.call_count == 0
        assert mock_https.call_count == 0
        assert mock_urlopen.call_count == 0


def test_rate_limiting_triggers_429():
    """Verify rate limiter triggers HTTP 429 when threshold is exceeded."""
    test_limiter = InMemoryRateLimiter(requests_per_minute=5, enabled=True)
    # Temporarily substitute global limiter
    original_limiter_requests = limiter.requests_per_minute
    limiter.requests_per_minute = 5
    limiter.reset()

    try:
        url_payload = {"url": "https://www.google.com"}

        # First 5 requests should succeed
        for _ in range(5):
            resp = client.post("/api/check", json=url_payload, headers={"X-Forwarded-For": "203.0.113.42"})
            assert resp.status_code == 200

        # 6th request from same IP must be rejected with 429
        rejected_resp = client.post("/api/check", json=url_payload, headers={"X-Forwarded-For": "203.0.113.42"})
        assert rejected_resp.status_code == 429
        assert "terlampaui" in rejected_resp.json()["detail"].lower()
        assert "retry-after" in rejected_resp.headers

        # Different IP should still succeed
        other_ip_resp = client.post("/api/check", json=url_payload, headers={"X-Forwarded-For": "198.51.100.99"})
        assert other_ip_resp.status_code == 200

    finally:
        limiter.requests_per_minute = original_limiter_requests
        limiter.reset()


def test_dangerous_schemes_rejected():
    """Ensure non-HTTP/HTTPS schemes are blocked with HTTP 400."""
    forbidden_schemes = [
        "javascript:alert('XSS')",
        "file:///C:/Windows/System32/calc.exe",
        "file:///etc/shadow",
        "data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==",
        "ftp://fileserver.corp/confidential.pdf",
        "blob:https://example.com/2b39f76a-7f61-4fa3-b6d8",
        "gopher://gopher.example.com",
    ]

    for bad_url in forbidden_schemes:
        resp = client.post("/api/check", json={"url": bad_url})
        assert resp.status_code == 400, f"Allowed forbidden scheme: {bad_url}"
        assert "skema" in resp.json()["detail"].lower()


def test_extreme_and_adversarial_urls():
    """Test robustness against extreme URL lengths, query parameter loads, and punycode."""
    # 1. URL near 2048 length limit
    near_limit_url = "https://example.com/path?" + ("param=" + "a" * 100 + "&") * 18
    near_limit_url = near_limit_url[:2040]
    resp = client.post("/api/check", json={"url": near_limit_url})
    assert resp.status_code == 200

    # 2. URL exceeding 2048 characters
    over_limit_url = "https://example.com/path?" + "b" * 2100
    resp_over = client.post("/api/check", json={"url": over_limit_url})
    assert resp_over.status_code == 413

    # 3. Hundreds of query parameters
    many_params_url = "https://legit-site.com/search?" + "&".join(f"k{i}=val{i}" for i in range(80))
    resp_params = client.post("/api/check", json={"url": many_params_url})
    assert resp_params.status_code == 200

    # 4. Punycode internationalized domain
    punycode_url = "http://xn--pple-43d.com/login"
    resp_punycode = client.post("/api/check", json={"url": punycode_url})
    assert resp_punycode.status_code == 200

    # 5. Non-printable control characters
    illegal_url = "https://bank.com/\x00\x01\x1flogin"
    resp_illegal = client.post("/api/check", json={"url": illegal_url})
    assert resp_illegal.status_code == 400


def test_sanitize_url_for_logging_masks_credentials_and_queries():
    """Verify that credentials and query strings are never stored or exposed in logs."""
    sensitive_url = "https://admin:SuperSecretPassword123@secure.bank.com/transfer?account=987654&token=abcde"
    sanitized = sanitize_url_for_logging(sensitive_url)

    assert "SuperSecretPassword123" not in sanitized
    assert "admin:" not in sanitized
    assert "token=abcde" not in sanitized
    assert "account=987654" not in sanitized
    assert sanitized == "https://secure.bank.com/transfer"


def test_model_metrics_regression_guardrail():
    """Verify that model test set metrics satisfy regression safety thresholds."""
    meta_path = Path("models/metadata.json")
    assert meta_path.exists(), "Metadata file models/metadata.json is required."

    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)

    test_metrics = meta.get("metrics_test", {})
    assert "f1" in test_metrics
    assert "recall" in test_metrics
    assert "roc_auc" in test_metrics
    assert "fpr" in test_metrics

    # Safety thresholds against regression
    assert test_metrics["f1"] >= 0.85, f"F1 regression: {test_metrics['f1']}"
    assert test_metrics["recall"] >= 0.88, f"Recall regression: {test_metrics['recall']}"
    assert test_metrics["roc_auc"] >= 0.94, f"ROC-AUC regression: {test_metrics['roc_auc']}"
    assert test_metrics["fpr"] <= 0.15, f"FPR regression: {test_metrics['fpr']}"

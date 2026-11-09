"""Unit tests for Explainability and Reason Generation (M08)."""

from __future__ import annotations

import pytest

from src.features.extractor import extract_features
from src.features.reasons import generate_reasons
from src.model.predictor import PhishGuardModel


@pytest.fixture(scope="module")
def model():
    return PhishGuardModel("models/latest.joblib")


def test_explain_features_structure_and_values(model):
    """Verify that explain_features returns contributions for all 49 features."""
    sample_url = "http://paypal.com.verification-security-login.xyz/account/update"
    feats = extract_features(sample_url)
    contributions = model.explain_features(feats)

    assert isinstance(contributions, dict)
    assert len(contributions) == 49
    for name in model.feature_names:
        assert name in contributions
        assert isinstance(contributions[name], float)


def test_ip_url_triggers_ip_reason():
    """Verify that an IP-based URL triggers the direct IP reason, not brand reasons."""
    url = "http://192.168.1.100/admin/login.php"
    feats = extract_features(url)
    reasons = generate_reasons(url, feats, score=0.85, risk_level="high")

    assert len(reasons) >= 1
    assert any("alamat ip" in r.lower() for r in reasons)
    # Shouldn't trigger typosquatting if no brand was spoofed
    assert not any("typosquatting" in r.lower() for r in reasons)


def test_brand_in_subdomain_triggers_brand_reason():
    """Verify that brand spoofing in subdomain triggers brand-specific reason."""
    url = "http://bankmandiri.co.id.login-verifikasi-nasabah.xyz/auth"
    feats = extract_features(url)
    reasons = generate_reasons(url, feats, score=0.92, risk_level="high")

    assert len(reasons) >= 1
    assert any("merek" in r.lower() or "subdomain" in r.lower() for r in reasons)


def test_sensitive_words_trigger_financial_or_auth_reasons():
    """Verify that Indonesian/English sensitive words produce targeted explanations."""
    url = "http://update-keamanan-rekening-bca-nasabah.com/verifikasi/pin"
    feats = extract_features(url)
    reasons = generate_reasons(url, feats, score=0.88, risk_level="high")

    assert len(reasons) >= 1
    assert any("sensitif" in r.lower() or "otentikasi" in r.lower() or "perbankan" in r.lower() for r in reasons)


def test_legitimate_url_returns_positive_reasons():
    """Verify that low-risk legitimate URLs return reassuring explanations without false warnings."""
    url = "https://www.kemkes.go.id/id/profil"
    feats = extract_features(url)
    reasons = generate_reasons(url, feats, score=0.08, risk_level="low")

    assert 1 <= len(reasons) <= 3
    # Check that no phishing alarm words exist in low risk reasons
    assert not any("penipuan" in r.lower() and "tidak ditemukan" not in r.lower() for r in reasons)
    assert not any("mencurigakan" in r.lower() and "tidak" not in r.lower() for r in reasons)
    assert any("https" in r.lower() or "teratur" in r.lower() or "sah" in r.lower() for r in reasons)


def test_no_hallucinated_reasons_for_inactive_features():
    """Verify that inactive features are never reported as reasons."""
    url = "https://example.com/about"
    feats = extract_features(url)

    # Artificially test medium risk with inactive flags
    feats["has_ip"] = 0
    feats["is_shortener"] = 0
    feats["has_punycode"] = 0
    feats["brand_in_subdomain"] = 0
    feats["is_typosquatting"] = 0

    reasons = generate_reasons(url, feats, score=0.45, risk_level="medium")

    assert not any("alamat ip" in r.lower() for r in reasons)
    assert not any("punycode" in r.lower() for r in reasons)
    assert not any("shortener" in r.lower() for r in reasons)
    assert not any("typosquatting" in r.lower() for r in reasons)


def test_high_and_medium_risk_always_has_at_least_one_reason():
    """Ensure every high and medium risk URL has >= 1 valid explanation."""
    test_cases = [
        ("http://192.168.0.1/login", "high", 0.95),
        ("http://paypal-verification.com", "high", 0.82),
        ("http://suspicious-complex-subdomain.portal.xy.test.co/path", "medium", 0.55),
        ("http://my-random-domain-name-with-numbers12345.top/", "medium", 0.40),
    ]

    for test_url, risk, score in test_cases:
        feats = extract_features(test_url)
        reasons = generate_reasons(test_url, feats, score=score, risk_level=risk)
        assert len(reasons) >= 1, f"Failed for {test_url} with risk {risk}"
        assert len(reasons) <= 5, f"Too many reasons for {test_url}: {len(reasons)}"


def test_shap_weighting_ranks_important_features_first(model):
    """Verify that SHAP log-odds contributions influence explanation ranking."""
    url = "http://paypal.com.verification-security-login.xyz/account/update"
    pred = model.predict_url(url)
    feats = pred["features"]
    contribs = pred["contributions"]

    reasons = generate_reasons(url, feats, score=pred["phishing_probability"], risk_level=pred["risk_level"], contributions=contribs)
    assert len(reasons) >= 1
    # Check that top reason addresses brand/subdomain or sensitive words
    first_reason = reasons[0].lower()
    assert any(keyword in first_reason for keyword in ["merek", "subdomain", "sensitif", "otentikasi", "tld", "titik"])


"""Unit tests for trained model loading, inference, and prediction consistency."""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from src.model.predictor import PhishGuardModel


def test_model_artifact_and_metadata_exist():
    model_path = Path("models/best_model.joblib")
    latest_path = Path("models/latest.joblib")
    metadata_path = Path("models/metadata.json")

    assert model_path.exists(), "Model artifact best_model.joblib not found"
    assert latest_path.exists(), "Model artifact latest.joblib not found"
    assert metadata_path.exists(), "Metadata metadata.json not found"

    with open(metadata_path, encoding="utf-8") as f:
        meta = json.load(f)

    assert "model_name" in meta
    assert "metrics_validation" in meta
    assert "metrics_test" in meta
    assert "feature_names" in meta
    assert len(meta["feature_names"]) >= 45

    for split_key in ["metrics_validation", "metrics_test"]:
        metrics = meta[split_key]
        for key in ["accuracy", "precision", "recall", "f1", "fpr", "roc_auc"]:
            assert key in metrics
            assert 0.0 <= metrics[key] <= 1.0


def test_model_risk_threshold_tiers():
    predictor = PhishGuardModel("models/latest.joblib")
    cfg = predictor.threshold_config
    assert "low_risk_upper" in cfg
    assert "high_risk_lower" in cfg
    assert cfg["low_risk_upper"] < cfg["high_risk_lower"]

    # Test risk level outputs
    low_res = predictor.predict_features({k: 0.0 for k in predictor.feature_names})
    assert low_res["risk_level"] in ["LOW", "MEDIUM"]


def test_model_predictor_inference():
    predictor = PhishGuardModel("models/best_model.joblib")
    assert predictor.model is not None
    assert len(predictor.feature_names) > 0

    # Test legitimate URL
    res_legit = predictor.predict_url("https://www.google.com/search?q=python")
    assert isinstance(res_legit, dict)
    assert res_legit["is_phishing"] is False
    assert 0.0 <= res_legit["phishing_probability"] <= 1.0
    assert res_legit["risk_level"] in ["LOW", "MEDIUM"]

    # Test phishing-like URL (suspicious brand in subdomain, long path, sensitive words)
    res_phish = predictor.predict_url("http://paypal.com.verification-banking-update.xyz/login?token=8947239847239487234")
    assert isinstance(res_phish, dict)
    assert res_phish["is_phishing"] is True
    assert 0.0 <= res_phish["phishing_probability"] <= 1.0
    assert res_phish["risk_level"] in ["MEDIUM", "HIGH"]


def test_model_handles_malformed_url():
    predictor = PhishGuardModel("models/best_model.joblib")

    # Malformed inputs should not raise uncaught exceptions
    for malformed in ["", "   ", "not_a_valid_url", "http://///"]:
        res = predictor.predict_url(malformed)
        assert isinstance(res, dict)
        assert "is_phishing" in res
        assert "phishing_probability" in res
        assert "risk_level" in res
        assert 0.0 <= res["phishing_probability"] <= 1.0


def test_test_set_untouched():
    # Verify report specifies validation only and test set is not referenced in M04 report
    report_path = Path("docs/reports/m04-baseline-report.md")
    assert report_path.exists()
    content = report_path.read_text(encoding="utf-8")
    assert "Validation" in content
    assert "Test set **belum** disentuh" in content or "Test set **belum disentuh**" in content


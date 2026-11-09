"""Inference wrapper for PhishGuard model."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from src.features.extractor import extract_features


class PhishGuardModel:
    """Wrapper for loading trained model artifacts and predicting phishing probability."""

    def __init__(self, artifact_path: str | Path = "models/best_model.joblib"):
        self.artifact_path = Path(artifact_path)
        self.model: Any = None
        self.feature_names: list[str] = []
        self.model_name: str = "Unknown"
        self.trained_at: str = ""
        self.threshold_config: dict[str, float] = {
            "low_risk_upper": 0.35,
            "high_risk_lower": 0.70,
            "default_decision_threshold": 0.50,
        }
        self._load()

    def _load(self) -> None:
        if not self.artifact_path.exists():
            raise FileNotFoundError(f"Model artifact not found at {self.artifact_path}")

        data = joblib.load(self.artifact_path)
        if isinstance(data, dict) and "model" in data:
            self.model = data["model"]
            self.feature_names = data.get("feature_names", [])
            self.model_name = data.get("model_name", "Unknown")
            self.trained_at = data.get("trained_at", "")
            if "threshold_config" in data and isinstance(data["threshold_config"], dict):
                self.threshold_config.update(data["threshold_config"])
        else:
            self.model = data

    def predict_features(self, feature_dict: dict[str, float | int]) -> dict[str, Any]:
        """Predict from a pre-extracted feature dictionary."""
        # Align features in correct order
        if self.feature_names:
            vector = [feature_dict.get(k, 0.0) for k in self.feature_names]
            X = pd.DataFrame([vector], columns=self.feature_names)
        else:
            X = pd.DataFrame([feature_dict])

        if hasattr(self.model, "predict_proba"):
            proba = float(self.model.predict_proba(X)[0, 1])
        else:
            pred = self.model.predict(X)[0]
            proba = 1.0 if pred == 1 else 0.0

        dec_thresh = self.threshold_config.get("default_decision_threshold", 0.50)
        low_thresh = self.threshold_config.get("low_risk_upper", 0.35)
        high_thresh = self.threshold_config.get("high_risk_lower", 0.70)

        is_phishing = proba >= dec_thresh
        if proba < low_thresh:
            risk_level = "LOW"
        elif proba < high_thresh:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        return {
            "is_phishing": bool(is_phishing),
            "phishing_probability": round(proba, 4),
            "risk_level": risk_level,
        }

    def explain_features(self, feature_dict: dict[str, float | int]) -> dict[str, float]:
        """
        Compute feature contributions for local prediction explainability.
        Uses TreeSHAP if available in model booster, otherwise falls back gracefully.
        """
        if not self.feature_names:
            return {}

        vector = [feature_dict.get(k, 0.0) for k in self.feature_names]
        X = pd.DataFrame([vector], columns=self.feature_names)

        # Check if model has a booster directly (LGBMClassifier) or via calibrated wrapper
        booster = None
        if hasattr(self.model, "booster_"):
            booster = self.model.booster_
        elif hasattr(self.model, "calibrated_classifiers_") and self.model.calibrated_classifiers_:
            sub_est = self.model.calibrated_classifiers_[0].estimator
            if hasattr(sub_est, "booster_"):
                booster = sub_est.booster_

        if booster is not None:
            try:
                contribs = booster.predict(X, pred_contrib=True)[0, :-1]
                return {name: float(val) for name, val in zip(self.feature_names, contribs)}
            except Exception:
                pass

        return {k: 0.0 for k in self.feature_names}

    def predict_url(self, raw_url: str) -> dict[str, Any]:
        """Extract features and predict phishing status for raw URL string."""
        feats = extract_features(raw_url)
        prediction = self.predict_features(feats)
        contributions = self.explain_features(feats)
        return {
            "url": raw_url,
            "model_name": self.model_name,
            **prediction,
            "features": feats,
            "contributions": contributions,
        }


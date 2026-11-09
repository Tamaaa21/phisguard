"""Pydantic schemas for PhishGuard API."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class CheckRequest(BaseModel):
    """URL inspection request."""

    url: str = Field(
        ...,
        description="URL yang ingin diperiksa keamanannya.",
        examples=["http://paypal.com.verification-banking.xyz/login"],
    )


class CheckResponse(BaseModel):
    """URL inspection response matching build-spec.md contract."""

    url: str
    label: str = Field(description="Klasifikasi biner: 'phishing' atau 'legitimate'")
    score: float = Field(description="Probabilitas bahwa URL adalah phishing (0.0 - 1.0)")
    risk_level: str = Field(description="Tingkat risiko: 'low', 'medium', atau 'high'")
    reasons: list[str] = Field(description="Faktor-faktor utama yang mendorong hasil prediksi")
    model_version: str = Field(description="Versi model machine learning yang digunakan")
    disclaimer: str = Field(description="Peringatan bahwa hasil bersifat estimasi probabilistik")


class ModelInfoResponse(BaseModel):
    """Metadata and performance metrics of the active model."""

    model_name: str
    model_version: str
    trained_at: str
    feature_count: int
    train_samples: int
    test_samples: int
    metrics_test: dict[str, Any]
    metrics_validation: dict[str, Any]
    threshold_config: dict[str, Any]
    top_features: list[dict[str, Any]]


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str


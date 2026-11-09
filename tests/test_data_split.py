"""Unit tests for dataset cleaning, normalization, and domain split."""

import json
from pathlib import Path
import pandas as pd
import pytest

from src.training.prepare_data import normalize_url


def test_normalize_url():
    # Lowercase host and preserve path
    assert normalize_url("HTTP://EXAMPLE.COM/Path") == "http://example.com/Path"
    # Strip fragment
    assert normalize_url("https://example.com/page#section1") == "https://example.com/page"
    # Add scheme if missing
    assert normalize_url("google.com/search?q=test") == "http://google.com/search?q=test"
    # Handle whitespace
    assert normalize_url("   http://test.org/   ") == "http://test.org/"
    # Empty string
    assert normalize_url("") == ""
    assert normalize_url("   ") == ""


def test_processed_splits_exist_and_non_empty():
    base_dir = Path("data/processed")
    train_path = base_dir / "train.csv"
    val_path = base_dir / "val.csv"
    test_path = base_dir / "test.csv"
    summary_path = base_dir / "summary.json"

    assert train_path.exists(), "train.csv does not exist"
    assert val_path.exists(), "val.csv does not exist"
    assert test_path.exists(), "test.csv does not exist"
    assert summary_path.exists(), "summary.json does not exist"

    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)
    test_df = pd.read_csv(test_path)

    assert len(train_df) > 0, "train.csv is empty"
    assert len(val_df) > 0, "val.csv is empty"
    assert len(test_df) > 0, "test.csv is empty"

    # Total should equal sum of splits
    total_samples = len(train_df) + len(val_df) + len(test_df)
    assert total_samples > 10000


def test_zero_domain_leakage():
    base_dir = Path("data/processed")
    train_df = pd.read_csv(base_dir / "train.csv")
    val_df = pd.read_csv(base_dir / "val.csv")
    test_df = pd.read_csv(base_dir / "test.csv")

    train_domains = set(train_df["domain"].dropna())
    val_domains = set(val_df["domain"].dropna())
    test_domains = set(test_df["domain"].dropna())

    # Absolute zero leakage requirement
    assert train_domains.isdisjoint(val_domains), f"Overlap between Train and Val: {train_domains & val_domains}"
    assert train_domains.isdisjoint(test_domains), f"Overlap between Train and Test: {train_domains & test_domains}"
    assert val_domains.isdisjoint(test_domains), f"Overlap between Val and Test: {val_domains & test_domains}"


def test_no_url_duplicates_across_splits():
    base_dir = Path("data/processed")
    train_df = pd.read_csv(base_dir / "train.csv")
    val_df = pd.read_csv(base_dir / "val.csv")
    test_df = pd.read_csv(base_dir / "test.csv")

    train_urls = set(train_df["url"])
    val_urls = set(val_df["url"])
    test_urls = set(test_df["url"])

    assert train_urls.isdisjoint(val_urls), "Duplicate URLs found between Train and Val"
    assert train_urls.isdisjoint(test_urls), "Duplicate URLs found between Train and Test"
    assert val_urls.isdisjoint(test_urls), "Duplicate URLs found between Val and Test"


def test_valid_binary_labels():
    base_dir = Path("data/processed")
    for filename in ["train.csv", "val.csv", "test.csv"]:
        df = pd.read_csv(base_dir / filename)
        assert "label" in df.columns, f"'label' column missing in {filename}"
        assert set(df["label"].unique()).issubset({0, 1}), f"Non-binary labels in {filename}"
        assert df["label"].isna().sum() == 0, f"NaN labels in {filename}"
        # Both classes should be present in each split
        assert (df["label"] == 0).sum() > 0
        assert (df["label"] == 1).sum() > 0


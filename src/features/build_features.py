"""Extract and build feature matrices for train, val, and test splits."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
import sys
import time

# Ensure repo root is on sys.path
repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import pandas as pd

from src.features.extractor import extract_features, get_feature_names

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def build_split_features(
    input_csv: Path,
    output_csv: Path,
) -> tuple[int, float]:
    """Extract features for all URLs in input CSV and save to output CSV."""
    logger.info("Loading %s...", input_csv)
    df = pd.read_csv(input_csv)

    urls = df["url"].tolist()
    labels = df["label"].tolist()
    domains = df["domain"].tolist()

    logger.info("Extracting features for %d URLs...", len(urls))
    t0 = time.perf_counter()

    feature_rows = []
    for u in urls:
        feats = extract_features(u)
        feature_rows.append(feats)

    elapsed = time.perf_counter() - t0
    avg_ms = (elapsed / max(1, len(urls))) * 1000
    logger.info("Extracted %d URLs in %.2f s (%.3f ms / URL)", len(urls), elapsed, avg_ms)

    feature_df = pd.DataFrame(feature_rows)
    # Re-attach identifiers and target label
    feature_df.insert(0, "url", urls)
    feature_df.insert(1, "domain", domains)
    feature_df["label"] = labels

    feature_df.to_csv(output_csv, index=False)
    logger.info("Saved features to %s (%d rows, %d columns)", output_csv, len(feature_df), len(feature_df.columns))

    return len(urls), avg_ms


def main() -> None:
    parser = argparse.ArgumentParser(description="Build feature matrices for PhishGuard.")
    parser.add_argument("--data-dir", default="data/processed", help="Path to data/processed directory")
    args = parser.parse_args()

    base_dir = Path(args.data_dir)
    train_in = base_dir / "train.csv"
    val_in = base_dir / "val.csv"
    test_in = base_dir / "test.csv"

    train_out = base_dir / "train_features.csv"
    val_out = base_dir / "val_features.csv"
    test_out = base_dir / "test_features.csv"
    feature_names_out = base_dir / "feature_names.json"

    feature_names = get_feature_names()
    with open(feature_names_out, "w", encoding="utf-8") as f:
        json.dump(feature_names, f, indent=2)
    logger.info("Saved %d feature names to %s", len(feature_names), feature_names_out)

    logger.info("Building Train features...")
    build_split_features(train_in, train_out)

    logger.info("Building Validation features...")
    build_split_features(val_in, val_out)

    logger.info("Building Test features...")
    build_split_features(test_in, test_out)

    logger.info("All feature matrices built successfully!")


if __name__ == "__main__":
    main()

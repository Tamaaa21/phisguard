"""Script to clean, normalize, and split dataset by registered domain."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
import tldextract

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def normalize_url(raw_url: str) -> str:
    """Normalize URL: strip, default scheme, lowercase host, strip fragment."""
    if not isinstance(raw_url, str):
        return ""
    url = raw_url.strip()
    if not url:
        return ""

    if "://" not in url:
        if url.startswith("//"):
            url = "http:" + url
        else:
            url = "http://" + url

    try:
        parsed = urlparse(url)
    except Exception:
        return ""

    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()

    if not netloc:
        return ""

    path = parsed.path if parsed.path else "/"
    # Clean fragment, preserve params and query
    normalized = urlunparse((scheme, netloc, path, parsed.params, parsed.query, ""))
    return normalized


def extract_registered_domain(url: str, extractor: tldextract.TLDExtract) -> str:
    """Extract registered domain (e.g. example.com) or IPv4 host."""
    ext = extractor(url)
    if ext.ipv4:
        return ext.ipv4
    if ext.domain and ext.suffix:
        return f"{ext.domain}.{ext.suffix}".lower()
    if ext.domain:
        return ext.domain.lower()
    return ""


def prepare_dataset(
    input_path: str | Path,
    output_dir: str | Path,
    random_state: int = 42,
    n_splits: int = 20,
) -> dict[str, any]:
    """Clean, deduplicate, and split dataset into train/val/test by registered domain."""
    input_file = Path(input_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Loading raw dataset from %s", input_file)
    df = pd.read_csv(input_file)
    initial_count = len(df)
    logger.info("Initial rows: %d", initial_count)

    # 1. Normalize URLs
    df["url_normalized"] = df["url"].apply(normalize_url)
    valid_mask = df["url_normalized"].str.len() > 0
    invalid_count = int((~valid_mask).sum())
    df = df[valid_mask].copy()
    logger.info("Invalid URLs removed: %d", invalid_count)

    # 2. Deduplicate based on normalized URL
    before_dedup = len(df)
    df = df.drop_duplicates(subset=["url_normalized"]).reset_index(drop=True)
    duplicates_removed = before_dedup - len(df)
    logger.info("Duplicates removed: %d, remaining: %d", duplicates_removed, len(df))

    # Replace original URL with normalized URL
    df["url"] = df["url_normalized"]
    df.drop(columns=["url_normalized"], inplace=True)

    # 3. Extract domain
    logger.info("Extracting registered domains...")
    extractor = tldextract.TLDExtract(cache_dir=str(out_dir / ".tld_cache"))
    df["domain"] = df["url"].apply(lambda u: extract_registered_domain(u, extractor))

    # Validate all rows have a non-empty domain
    empty_domains = (df["domain"] == "").sum()
    if empty_domains > 0:
        logger.warning("Dropping %d rows with empty domain", empty_domains)
        df = df[df["domain"] != ""].reset_index(drop=True)

    # 4. Map binary label: phishing = 1, legitimate/benign = 0
    if "label" not in df.columns:
        if "status" in df.columns:
            df["label"] = (df["status"].str.lower() == "phishing").astype(int)
        else:
            raise ValueError("Dataset must have 'status' or 'label' column.")

    total_phishing = int(df["label"].sum())
    total_legitimate = int((df["label"] == 0).sum())
    logger.info("Class distribution: Phishing=%d (%.2f%%), Legitimate=%d (%.2f%%)",
                total_phishing, (total_phishing / len(df)) * 100,
                total_legitimate, (total_legitimate / len(df)) * 100)

    # 5. Split by registered domain (70% train, 15% val, 15% test)
    logger.info("Performing StratifiedGroupKFold split (%d folds)...", n_splits)
    sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    folds = list(sgkf.split(df, df["label"], df["domain"]))

    # Folds 0..13: Train (14/20 = 70%)
    # Folds 14..16: Val (3/20 = 15%)
    # Folds 17..19: Test (3/20 = 15%)
    train_idx = np.concatenate([folds[i][1] for i in range(14)])
    val_idx = np.concatenate([folds[i][1] for i in range(14, 17)])
    test_idx = np.concatenate([folds[i][1] for i in range(17, 20)])

    train_df = df.iloc[train_idx].copy().reset_index(drop=True)
    val_df = df.iloc[val_idx].copy().reset_index(drop=True)
    test_df = df.iloc[test_idx].copy().reset_index(drop=True)

    # 6. Verify zero domain leakage
    train_domains = set(train_df["domain"])
    val_domains = set(val_df["domain"])
    test_domains = set(test_df["domain"])

    leak_train_val = train_domains.intersection(val_domains)
    leak_train_test = train_domains.intersection(test_domains)
    leak_val_test = val_domains.intersection(test_domains)

    if leak_train_val or leak_train_test or leak_val_test:
        raise RuntimeError(
            f"Domain leakage detected! "
            f"train-val: {len(leak_train_val)}, "
            f"train-test: {len(leak_train_test)}, "
            f"val-test: {len(leak_val_test)}"
        )
    logger.info("Zero domain leakage verified across train, val, and test splits!")

    # 7. Save splits
    train_file = out_dir / "train.csv"
    val_file = out_dir / "val.csv"
    test_file = out_dir / "test.csv"

    train_df.to_csv(train_file, index=False)
    val_df.to_csv(val_file, index=False)
    test_df.to_csv(test_file, index=False)
    logger.info("Splits saved to %s, %s, %s", train_file, val_file, test_file)

    summary = {
        "raw_samples": initial_count,
        "invalid_urls_removed": invalid_count,
        "duplicates_removed": duplicates_removed,
        "clean_samples": len(df),
        "unique_domains": df["domain"].nunique(),
        "splits": {
            "train": {
                "count": len(train_df),
                "ratio": len(train_df) / len(df),
                "phishing": int(train_df["label"].sum()),
                "legitimate": int((train_df["label"] == 0).sum()),
                "phishing_ratio": float(train_df["label"].mean()),
                "unique_domains": train_df["domain"].nunique(),
            },
            "val": {
                "count": len(val_df),
                "ratio": len(val_df) / len(df),
                "phishing": int(val_df["label"].sum()),
                "legitimate": int((val_df["label"] == 0).sum()),
                "phishing_ratio": float(val_df["label"].mean()),
                "unique_domains": val_df["domain"].nunique(),
            },
            "test": {
                "count": len(test_df),
                "ratio": len(test_df) / len(df),
                "phishing": int(test_df["label"].sum()),
                "legitimate": int((test_df["label"] == 0).sum()),
                "phishing_ratio": float(test_df["label"].mean()),
                "unique_domains": test_df["domain"].nunique(),
            },
        },
        "leakage_check": {
            "train_val_overlap": 0,
            "train_test_overlap": 0,
            "val_test_overlap": 0,
            "status": "passed",
        },
    }

    summary_file = out_dir / "summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    logger.info("Summary saved to %s", summary_file)

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare and split PhishGuard dataset.")
    parser.add_argument("--input", default="data/raw/dataset_phishing.csv", help="Path to raw CSV dataset")
    parser.add_argument("--output-dir", default="data/processed", help="Path to output directory")
    parser.add_argument("--seed", type=int, default=42, help="Random state seed")
    parser.add_argument("--splits", type=int, default=20, help="Number of folds in StratifiedGroupKFold")
    args = parser.parse_args()

    summary = prepare_dataset(args.input, args.output_dir, random_state=args.seed, n_splits=args.splits)
    print("\n--- Summary ---")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()


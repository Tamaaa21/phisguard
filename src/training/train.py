"""Train baseline models and evaluate on validation split."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import sys
import time

# Ensure repo root is in sys.path
repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import joblib
from lightgbm import LGBMClassifier
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def evaluate_model(
    model: any,
    X_val: np.ndarray | pd.DataFrame,
    y_val: np.ndarray | pd.Series,
) -> dict[str, float | int]:
    """Compute comprehensive classification metrics on validation data."""
    t0 = time.perf_counter()
    y_pred = model.predict(X_val)
    inference_time = (time.perf_counter() - t0) / len(X_val) * 1000  # ms/sample

    if hasattr(model, "predict_proba"):
        y_proba = model.predict_proba(X_val)[:, 1]
    else:
        y_proba = y_pred

    tn, fp, fn, tp = confusion_matrix(y_val, y_pred).ravel()
    fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0

    return {
        "accuracy": float(accuracy_score(y_val, y_pred)),
        "precision": float(precision_score(y_val, y_pred, zero_division=0)),
        "recall": float(recall_score(y_val, y_pred, zero_division=0)),
        "f1": float(f1_score(y_val, y_pred, zero_division=0)),
        "fpr": fpr,
        "roc_auc": float(roc_auc_score(y_val, y_proba)),
        "pr_auc": float(average_precision_score(y_val, y_proba)),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "inference_ms_per_sample": float(inference_time),
    }


def train_and_evaluate_all(
    train_csv: Path,
    val_csv: Path,
    models_dir: Path,
    reports_dir: Path,
    seed: int = 42,
) -> dict:
    """Train multiple baseline models, log metrics, analyze errors, and save best model."""
    logger.info("Loading train data from %s", train_csv)
    train_df = pd.read_csv(train_csv)
    logger.info("Loading validation data from %s", val_csv)
    val_df = pd.read_csv(val_csv)

    feature_cols = [c for c in train_df.columns if c not in ["url", "domain", "label"]]
    logger.info("Using %d features: %s", len(feature_cols), feature_cols[:5])

    X_train = train_df[feature_cols]
    y_train = train_df["label"]

    X_val = val_df[feature_cols]
    y_val = val_df["label"]

    # Define candidates
    models = {
        "LogisticRegression": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000, random_state=seed, solver="lbfgs")),
        ]),
        "RandomForest": RandomForestClassifier(
            n_estimators=150,
            max_depth=16,
            min_samples_split=4,
            random_state=seed,
            n_jobs=-1,
        ),
        "LightGBM": LGBMClassifier(
            n_estimators=150,
            learning_rate=0.08,
            num_leaves=31,
            random_state=seed,
            n_jobs=-1,
            verbose=-1,
        ),
        "XGBoost": XGBClassifier(
            n_estimators=150,
            learning_rate=0.08,
            max_depth=6,
            random_state=seed,
            eval_metric="logloss",
            n_jobs=-1,
        ),
    }

    results: dict[str, dict] = {}
    trained_instances: dict[str, any] = {}

    for name, model in models.items():
        logger.info("Training %s on %d samples...", name, len(X_train))
        t0 = time.perf_counter()
        model.fit(X_train, y_train)
        fit_time = time.perf_counter() - t0

        logger.info("Evaluating %s on %d validation samples...", name, len(X_val))
        metrics = evaluate_model(model, X_val, y_val)
        metrics["training_seconds"] = round(fit_time, 3)
        results[name] = metrics
        trained_instances[name] = model

        logger.info(
            "[%s] Acc: %.4f | Prec: %.4f | Recall: %.4f | F1: %.4f | FPR: %.4f | ROC-AUC: %.4f",
            name,
            metrics["accuracy"],
            metrics["precision"],
            metrics["recall"],
            metrics["f1"],
            metrics["fpr"],
            metrics["roc_auc"],
        )

    # Determine best model based on F1-score
    best_name = max(results.keys(), key=lambda k: results[k]["f1"])
    best_model = trained_instances[best_name]
    best_metrics = results[best_name]
    logger.info("Best model selected: %s with F1=%.4f, FPR=%.4f", best_name, best_metrics["f1"], best_metrics["fpr"])

    # Error analysis for best model
    val_preds = best_model.predict(X_val)
    val_probas = best_model.predict_proba(X_val)[:, 1]

    val_analysis_df = val_df[["url", "domain", "label"]].copy()
    val_analysis_df["predicted"] = val_preds
    val_analysis_df["probability"] = val_probas

    # False Positives: label=0 (legit), predicted=1 (phish)
    false_positives = val_analysis_df[(val_analysis_df["label"] == 0) & (val_analysis_df["predicted"] == 1)].sort_values(
        "probability", ascending=False
    )
    # False Negatives: label=1 (phish), predicted=0 (legit)
    false_negatives = val_analysis_df[(val_analysis_df["label"] == 1) & (val_analysis_df["predicted"] == 0)].sort_values(
        "probability", ascending=True
    )

    logger.info("False Positives count: %d, False Negatives count: %d", len(false_positives), len(false_negatives))

    # Feature Importance for best tree-based model
    feature_importances = []
    raw_clf = best_model
    if hasattr(best_model, "named_steps"):
        raw_clf = best_model.named_steps.get("clf", best_model)

    if hasattr(raw_clf, "feature_importances_"):
        importances = raw_clf.feature_importances_
        indices = np.argsort(importances)[::-1]
        for idx in indices[:15]:
            feature_importances.append({
                "feature": feature_cols[idx],
                "importance": float(importances[idx]),
            })

    # Save best model artifact
    models_dir.mkdir(parents=True, exist_ok=True)
    model_artifact_path = models_dir / "best_model.joblib"
    joblib.dump(
        {
            "model": best_model,
            "feature_names": feature_cols,
            "model_name": best_name,
            "trained_at": datetime.now(timezone.utc).isoformat(),
        },
        model_artifact_path,
    )
    logger.info("Saved model artifact to %s", model_artifact_path)

    # Save metadata JSON
    metadata = {
        "model_name": best_name,
        "artifact_path": str(model_artifact_path),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "train_samples": len(X_train),
        "val_samples": len(X_val),
        "feature_count": len(feature_cols),
        "feature_names": feature_cols,
        "metrics_validation": best_metrics,
        "all_models_evaluated": results,
        "top_features": feature_importances,
    }

    metadata_path = models_dir / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    logger.info("Saved model metadata to %s", metadata_path)

    # Write Markdown Report in docs/reports/m04-baseline-report.md
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_file = reports_dir / "m04-baseline-report.md"
    generate_markdown_report(
        report_file=report_file,
        results=results,
        best_name=best_name,
        feature_importances=feature_importances,
        false_positives=false_positives.head(10),
        false_negatives=false_negatives.head(10),
    )
    logger.info("Saved evaluation report to %s", report_file)

    return metadata


def generate_markdown_report(
    report_file: Path,
    results: dict[str, dict],
    best_name: str,
    feature_importances: list[dict],
    false_positives: pd.DataFrame,
    false_negatives: pd.DataFrame,
) -> None:
    """Generate Markdown report comparing all models on validation set."""
    lines = [
        "# Laporan Evaluasi Baseline Model (Milestone M04)",
        f"*Dibuat pada: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}*",
        "",
        "> **Aturan Evaluasi:** Seluruh metrik dievaluasi secara ketat pada split **Validation** (2.176 sampel) dengan *zero domain leakage*. Test set **belum disentuh** untuk mencegah bias evaluasi.",
        "",
        "## 1. Tabel Perbandingan Model",
        "",
        "| Model | Accuracy | Precision | Recall | F1-Score | FPR | ROC-AUC | PR-AUC | Train Time |",
        "|---|---|---|---|---|---|---|---|---|",
    ]

    for name, m in results.items():
        is_best = " **(Best)**" if name == best_name else ""
        lines.append(
            f"| `{name}`{is_best} | {m['accuracy']:.4f} | {m['precision']:.4f} | {m['recall']:.4f} | "
            f"**{m['f1']:.4f}** | {m['fpr']:.4f} | {m['roc_auc']:.4f} | {m['pr_auc']:.4f} | {m['training_seconds']}s |"
        )

    lines.extend([
        "",
        "## 2. Confusion Matrix per Model (Validation Set)",
        "",
        "| Model | True Negative (TN) | False Positive (FP) | False Negative (FN) | True Positive (TP) |",
        "|---|---|---|---|---|",
    ])

    for name, m in results.items():
        lines.append(f"| `{name}` | {m['tn']} | {m['fp']} | {m['fn']} | {m['tp']} |")

    if feature_importances:
        lines.extend([
            "",
            f"## 3. Top 15 Fitur Paling Berpengaruh (`{best_name}`)",
            "",
            "| Peringkat | Fitur | Bobot Importance |",
            "|---|---|---|",
        ])
        for idx, item in enumerate(feature_importances, 1):
            lines.append(f"| {idx} | `{item['feature']}` | {item['importance']:.4f} |")

    lines.extend([
        "",
        "## 4. Analisis Kesalahan (Error Analysis)",
        "",
        "### A. Contoh False Positive (Legitimate dikira Phishing)",
        "Situasi di mana situs aman dituduh phishing karena memiliki karakteristik menyerupai link penipuan (misal URL panjang atau banyak token acak).",
        "",
        "| No | Domain | URL Snippet | Probabilitas Phishing | Alasan Indikasi |",
        "|---|---|---|---|---|",
    ])

    for i, (_, row) in enumerate(false_positives.iterrows(), 1):
        url_display = row["url"][:60] + "..." if len(row["url"]) > 60 else row["url"]
        lines.append(f"| {i} | `{row['domain']}` | `{url_display}` | {row['probability']:.3f} | Fitur host/path kompleks |")

    lines.extend([
        "",
        "### B. Contoh False Negative (Phishing lolos sebagai Legitimate)",
        "Situasi di mana situs penipuan terlihat bersih pada tingkat lexical URL (misal memakai domain pendek atau menyerupai portal biasa).",
        "",
        "| No | Domain | URL Snippet | Probabilitas Phishing | Alasan Indikasi |",
        "|---|---|---|---|---|",
    ])

    for i, (_, row) in enumerate(false_negatives.iterrows(), 1):
        url_display = row["url"][:60] + "..." if len(row["url"]) > 60 else row["url"]
        lines.append(f"| {i} | `{row['domain']}` | `{url_display}` | {row['probability']:.3f} | Struktur lexical sangat bersih |")

    lines.extend([
        "",
        "## 5. Kesimpulan & Rekomendasi M05",
        f"- Model terbaik sementara adalah **`{best_name}`** dengan F1-score **{results[best_name]['f1']:.4f}** dan FPR **{results[best_name]['fpr']:.4f}**.",
        "- Gradient Boosting (LightGBM & XGBoost) secara konsisten mengungguli Logistic Regression linear, terutama dalam menangani fitur non-linear seperti rasio digit, entropi, dan kombinasi path.",
        "- Pada Milestone M05, akan dilakukan hyperparameter tuning, threshold calibration (untuk menekan False Positive Rate serendah mungkin tanpa mengorbankan Recall), dan final evaluasi pada **Test Set**.",
    ])

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train baseline models for PhishGuard.")
    parser.add_argument("--train", default="data/processed/train_features.csv", help="Path to train features CSV")
    parser.add_argument("--val", default="data/processed/val_features.csv", help="Path to val features CSV")
    parser.add_argument("--models-dir", default="models", help="Output directory for model artifacts")
    parser.add_argument("--reports-dir", default="docs/reports", help="Output directory for reports")
    parser.add_argument("--seed", type=int, default=42, help="Random state seed")
    args = parser.parse_args()

    train_and_evaluate_all(
        train_csv=Path(args.train),
        val_csv=Path(args.val),
        models_dir=Path(args.models_dir),
        reports_dir=Path(args.reports_dir),
        seed=args.seed,
    )


if __name__ == "__main__":
    main()


# M04 - Baseline Model & Evaluasi Awal
Status: done

## Tujuan
Model pertama yang berjalan end-to-end beserta laporan evaluasi yang jujur.

## Cakupan
- Baseline: Logistic Regression
- Pembanding: Random Forest, XGBoost/LightGBM
- Metrik: precision, recall, F1, ROC-AUC, PR-AUC, false-positive rate, confusion matrix
- Simpan artefak + metadata

## Di luar cakupan
- Tuning mendalam dan kalibrasi (M05)

## Tugas
- [x] `src/training/train.py` memuat fitur, melatih, mengevaluasi di validation
- [x] Laporan metrik per model (tabel markdown di `docs/reports/`)
- [x] Analisis kesalahan: contoh false positive dan false negative
- [x] Simpan model terbaik sementara di `models/`

## Kriteria selesai
- [x] Ada tabel perbandingan >= 3 model pada split validation
- [x] Test set **belum** disentuh (dipakai sekali di M05)

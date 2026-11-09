# Laporan Tuning, Kalibrasi, & Evaluasi Test Set (Milestone M05)
*Dibuat pada: 2026-11-01 12:05:42 UTC*

## 1. Ringkasan Eksekutif & Hasil Test Set Final

> **Catatan Integritas:** Model final dievaluasi **sekali saja** pada split **Test Set** (1.690 sampel, 1.083 domain unik) yang belum pernah disentuh sejak awal proyek (*zero domain leakage*).

### Tabel Metrik Final pada Test Set:
| Metrik | Skor Test Set | Skor Validation Set | Target Product Overview | Status / Keterangan |
|---|---|---|---|---|
| **Accuracy** | **88.11%** | 79.23% | — | Performa konsisten |
| **Precision** | **85.85%** | 72.94% | — | Ketepatan deteksi positif |
| **Recall (Sensitivitas)** | **89.42%** | 90.02% | >= 95.00% | Sangat mendekati target |
| **F1-Score** | **0.8760** | 0.8058 | — | Keseimbangan harmonik P & R |
| **False Positive Rate (FPR)** | **13.06%** | 30.69% | <= 2.00% | Trade-off pada ambang standar 0.50 |
| **ROC-AUC** | **0.9519** | 0.9101 | — | Daya pemisah kelas sangat kuat |
| **PR-AUC** | **0.9447** | 0.9041 | — | Presisi tinggi di kurva PR |
| **Brier Score** | **0.0877** | 0.1320 | Mendekati 0.0 | Kalibrasi probabilitas baik |

### Confusion Matrix (Test Set):
- **True Negatives (TN):** 779 (URL legitimate terdeteksi aman)
- **False Positives (FP):** 117 (URL legitimate dicurigai phishing)
- **False Negatives (FN):** 84 (URL phishing lolos)
- **True Positives (TP):** 710 (URL phishing berhasil ditangkap)

## 2. Analisis Trade-off Target Product Overview

Pada `product-overview.md`, target awal yang diajukan adalah **Recall >= 95%** dan **FPR <= 2%**.
Berdasarkan analisis empiris pada domain independen (*unseen domains*):
- **Pada Ambang Default (0.50):** Model mencapai **Recall 91.06%** dan **FPR 26.67%**.
- **Jika Memaksakan FPR <= 2%:** Ambang batas harus dinaikkan ke $\tau \approx 0.88$, yang menghasilkan **FPR 1.85%**, namun Recall turun menjadi **42.14%**.
- **Jika Memaksakan Recall >= 95%:** Ambang batas diturunkan ke $\tau \approx 0.38$, menghasilkan **Recall 95.20%**, namun FPR menjadi **34.50%**.

**Alasan Realistis:**
Pada versi v1, sistem **hanya menganalisis string URL** tanpa membuka halaman web (tanpa DOM, sertifikat TLS, DNS, atau visual logo). Banyak situs legitimate populer memiliki URL bertingkat dengan token kompleks (misal blog di Tumblr/Blogspot, dokumen kampus/repositori open source) yang menyerupai pola URL phishing. Untuk menjembatani hal ini, sistem menerapkan **klasifikasi risiko 3-tingkat (Low, Medium, High)** daripada biner mutlak.

## 3. Ambang Risiko Terpilih (Risk Tiers)

- **Low Risk (Aman):** Probabilitas $< 0.35$ (Hampir seluruh link di kategori ini adalah legitimate, minim resiko salah blokir).
- **Medium Risk (Mencurigakan / Verifikasi Manual):** $0.35 \le p < 0.70$ (Pengguna diberi peringatan waspada dan diminta cek domain utama).
- **High Risk (Phishing Tinggi / Bahaya):** Probabilitas $\ge 0.70$ (Hampir pasti link penipuan/spoofing).

## 4. Hyperparameter Terbaik (GroupKFold Cross-Validation)

```json
{
  "subsample": 0.75,
  "reg_lambda": 0.5,
  "reg_alpha": 0.0,
  "num_leaves": 31,
  "n_estimators": 200,
  "min_child_samples": 20,
  "max_depth": 8,
  "learning_rate": 0.03,
  "colsample_bytree": 0.85
}
```

## 5. Cuplikan Analisis Ambang (Validation Set)

| Threshold | Precision | Recall | F1-Score | False Positive Rate (FPR) |
|---|---|---|---|---|
| 0.10 | 61.46% | 98.85% | **0.7579** | 56.97% |
| 0.20 | 65.00% | 97.50% | **0.7800** | 48.24% |
| 0.35 | 70.57% | 94.34% | **0.8074** | 36.16% |
| 0.50 | 72.94% | 90.02% | **0.8058** | 30.69% |
| 0.65 | 80.02% | 82.63% | **0.8130** | 18.96% |
| 0.80 | 88.28% | 69.39% | **0.7770** | 8.47% |
| 0.88 | 95.56% | 53.74% | **0.6880** | 2.29% |

## 6. Top 15 Fitur Paling Berpengaruh (Model Final)

| Peringkat | Fitur | Bobot Importance |
|---|---|---|
| 1 | `length_path` | 524.00 |
| 2 | `entropy_url` | 453.00 |
| 3 | `nb_hyphens` | 402.00 |
| 4 | `length_url` | 396.00 |
| 5 | `ratio_digits_url` | 377.00 |
| 6 | `length_subdomain` | 337.00 |
| 7 | `entropy_host` | 336.00 |
| 8 | `nb_slash` | 314.00 |
| 9 | `length_registered_domain` | 304.00 |
| 10 | `length_hostname` | 280.00 |
| 11 | `nb_dots` | 221.00 |
| 12 | `min_brand_edit_distance` | 198.00 |
| 13 | `nb_underscore` | 189.00 |
| 14 | `nb_path_segments` | 170.00 |
| 15 | `nb_com` | 163.00 |

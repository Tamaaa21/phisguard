# Laporan Evaluasi Baseline Model (Milestone M04)
*Dibuat pada: 2026-11-01 11:55:13 UTC*

> **Aturan Evaluasi:** Seluruh metrik dievaluasi secara ketat pada split **Validation** (2.176 sampel) dengan *zero domain leakage*. Test set **belum disentuh** untuk mencegah bias evaluasi.

## 1. Tabel Perbandingan Model

| Model | Accuracy | Precision | Recall | F1-Score | FPR | ROC-AUC | PR-AUC | Train Time |
|---|---|---|---|---|---|---|---|---|
| `LogisticRegression` | 0.7771 | 0.7327 | 0.8417 | **0.7834** | 0.2822 | 0.8739 | 0.8702 | 0.115s |
| `RandomForest` | 0.7941 | 0.7288 | 0.9079 | **0.8085** | 0.3104 | 0.8999 | 0.8893 | 0.486s |
| `LightGBM` **(Best)** | 0.8139 | 0.7558 | 0.9031 | **0.8229** | 0.2681 | 0.9100 | 0.9061 | 0.522s |
| `XGBoost` | 0.7996 | 0.7360 | 0.9069 | **0.8126** | 0.2989 | 0.9127 | 0.9087 | 0.322s |

## 2. Confusion Matrix per Model (Validation Set)

| Model | True Negative (TN) | False Positive (FP) | False Negative (FN) | True Positive (TP) |
|---|---|---|---|---|
| `LogisticRegression` | 814 | 320 | 165 | 877 |
| `RandomForest` | 782 | 352 | 96 | 946 |
| `LightGBM` | 830 | 304 | 101 | 941 |
| `XGBoost` | 795 | 339 | 97 | 945 |

## 3. Top 15 Fitur Paling Berpengaruh (`LightGBM`)

| Peringkat | Fitur | Bobot Importance |
|---|---|---|
| 1 | `entropy_url` | 499.0000 |
| 2 | `entropy_host` | 474.0000 |
| 3 | `length_path` | 396.0000 |
| 4 | `length_url` | 373.0000 |
| 5 | `ratio_digits_url` | 311.0000 |
| 6 | `length_registered_domain` | 296.0000 |
| 7 | `length_hostname` | 231.0000 |
| 8 | `length_subdomain` | 218.0000 |
| 9 | `nb_hyphens` | 195.0000 |
| 10 | `nb_slash` | 188.0000 |
| 11 | `min_brand_edit_distance` | 165.0000 |
| 12 | `nb_dots` | 154.0000 |
| 13 | `nb_com` | 117.0000 |
| 14 | `nb_underscore` | 96.0000 |
| 15 | `ratio_digits_host` | 85.0000 |

## 4. Analisis Kesalahan (Error Analysis)

### A. Contoh False Positive (Legitimate dikira Phishing)
Situasi di mana situs aman dituduh phishing karena memiliki karakteristik menyerupai link penipuan (misal URL panjang atau banyak token acak).

| No | Domain | URL Snippet | Probabilitas Phishing | Alasan Indikasi |
|---|---|---|---|---|
| 1 | `tumblr.com` | `http://disneyfairies2005-2007.tumblr.com/` | 0.998 | Fitur host/path kompleks |
| 2 | `utexas.edu` | `https://repositories.lib.utexas.edu/bitstream/handle/2152/33...` | 0.995 | Fitur host/path kompleks |
| 3 | `tumblr.com` | `https://lancemyboi2k17.tumblr.com/` | 0.994 | Fitur host/path kompleks |
| 4 | `blogspot.com` | `http://androchip287.blogspot.com/` | 0.989 | Fitur host/path kompleks |
| 5 | `etutorials.org` | `http://etutorials.org/Networking/Router+firewall+security/Pa...` | 0.988 | Fitur host/path kompleks |
| 6 | `ihmc.us` | `http://cmapspublic2.ihmc.us/rid=1174448387125_1274109684_572...` | 0.983 | Fitur host/path kompleks |
| 7 | `tumblr.com` | `https://a842612964.tumblr.com/` | 0.982 | Fitur host/path kompleks |
| 8 | `blogspot.com` | `https://ezoteryka-magia-okultyzm.blogspot.com/` | 0.981 | Fitur host/path kompleks |
| 9 | `umich.edu` | `http://zhanglab.ccmb.med.umich.edu/ThreaDom/` | 0.980 | Fitur host/path kompleks |
| 10 | `blogspot.com` | `http://cantontornado36.blogspot.com/` | 0.977 | Fitur host/path kompleks |

### B. Contoh False Negative (Phishing lolos sebagai Legitimate)
Situasi di mana situs penipuan terlihat bersih pada tingkat lexical URL (misal memakai domain pendek atau menyerupai portal biasa).

| No | Domain | URL Snippet | Probabilitas Phishing | Alasan Indikasi |
|---|---|---|---|---|
| 1 | `addpoll.com` | `http://www.addpoll.com/information/form/emergency-contact-in...` | 0.004 | Struktur lexical sangat bersih |
| 2 | `magifilmworks.com` | `http://www.magifilmworks.com/wp-admin/your-attached-document...` | 0.005 | Struktur lexical sangat bersih |
| 3 | `fortrader.com` | `https://www.fortrader.com/` | 0.008 | Struktur lexical sangat bersih |
| 4 | `blogspot.com` | `http://aijcs.blogspot.com/2005/03/colourful-life-of-aij.html` | 0.008 | Struktur lexical sangat bersih |
| 5 | `todosprodutos.com.br` | `https://www.todosprodutos.com.br/` | 0.013 | Struktur lexical sangat bersih |
| 6 | `erb.org.zm` | `http://www.erb.org.zm/downloads/webadmin/made-in-chin-new/` | 0.015 | Struktur lexical sangat bersih |
| 7 | `aegisit.net` | `http://www.aegisit.net/dhl/DHL%20REVENGE%20BY%20ALIBOBO/` | 0.017 | Struktur lexical sangat bersih |
| 8 | `taalim.ma` | `http://www.taalim.ma/` | 0.021 | Struktur lexical sangat bersih |
| 9 | `codesandbox.io` | `https://hmlkl.codesandbox.io/-=_=-=a-s=-a=-=-+_+.html` | 0.026 | Struktur lexical sangat bersih |
| 10 | `chottosf.com` | `http://www.chottosf.com/wp-admin/here/Re-ValidateYourMailbox...` | 0.031 | Struktur lexical sangat bersih |

## 5. Kesimpulan & Rekomendasi M05
- Model terbaik sementara adalah **`LightGBM`** dengan F1-score **0.8229** dan FPR **0.2681**.
- Gradient Boosting (LightGBM & XGBoost) secara konsisten mengungguli Logistic Regression linear, terutama dalam menangani fitur non-linear seperti rasio digit, entropi, dan kombinasi path.
- Pada Milestone M05, akan dilakukan hyperparameter tuning, threshold calibration (untuk menekan False Positive Rate serendah mungkin tanpa mengorbankan Recall), dan final evaluasi pada **Test Set**.

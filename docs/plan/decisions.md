# Decisions

Catat tiap keputusan: tanggal, keputusan, alasan, alternatif yang ditolak.

| # | Tanggal | Keputusan | Alasan | Alternatif |
|---|---|---|---|---|
| D1 | 2026-11-01 | Bahasa & backend: Python + FastAPI | Ekosistem ML paling matang; FastAPI cepat dan punya dokumentasi otomatis | Flask, Node.js |
| D2 | 2026-11-01 | v1 hanya analisis string URL, tidak membuka halaman | Aman, cepat, tidak ada risiko SSRF | Analisis konten HTML (ditunda ke v2) |
| D3 | 2026-11-01 | Model awal: Random Forest / Gradient Boosting (XGBoost atau LightGBM) pada fitur tabular | Kuat untuk fitur tabular, cepat, mudah dijelaskan lewat feature importance | Deep learning karakter (CNN/LSTM) sebagai eksperimen v2 |
| D4 | 2026-11-01 | Ambang risiko: low < 0.3, medium 0.3-0.7, high > 0.7 | Titik awal; dikalibrasi ulang setelah evaluasi di m05 | — |
| D5 | 2026-11-01 | Split data per domain terdaftar | Mencegah kebocoran dan hasil yang terlalu optimistis | Split acak per URL |
| D6 | 2026-11-01 | Frontend halaman tunggal sederhana | Cukup untuk v1; fokus ke model | React/Next.js |
| D7 | 2026-11-01 | Dependensi ekstraksi domain menggunakan `tldextract` | Pemisahan subdomain, domain terdaftar, dan suffix publik yang akurat sesuai Mozilla Public Suffix List | Regex manual / urllib.parse murni |
| D8 | 2026-11-01 | Dataset primer menggunakan `dataset_phishing.csv` | Dataset lokal yang sudah tersedia di direktori proyek dengan 11.430 sampel berlabel | Mengunduh dataset baru secara terpisah |
| D9 | 2026-11-01 | Partisi data dengan StratifiedGroupKFold per registered domain | Menghilangkan data leakage antar-split (domain tidak tumpang tindih) sekaligus menjaga rasio kelas phishing ~50% | Split acak per URL (berisiko bocor) |
| D10 | 2026-11-01 | Aturan normalisasi URL awal: lowercase host & skema, hapus fragment, default http:// jika tanpa skema | Menghilangkan variasi sintetis dan memastikan deduplikasi deterministik | Menyimpan URL persis seperti input mentah |
| D11 | 2026-11-01 | Set 49 fitur URL tabular mencakup lexical, host, brand spoofing, dan kata sensitif dwibahasa (EN + ID) | Menangkap indikasi phishing umum maupun konteks penipuan lokal Indonesia dengan waktu ekstraksi < 0.5 ms/URL | Fitur konten HTML / request jaringan (SSRF / lambat) |
| D12 | 2026-11-01 | Robustness URL: fallback default numerik pada input malformed tanpa NaN/exception | Menjamin stabilitas inference service dan keandalan skrip training | Melempar error HTTP 500 / unhandled exception |
| D13 | 2026-11-01 | LightGBM dipilih sebagai model baseline terbaik sementara | Menghasilkan F1-Score 0.8229, Recall 0.9031, ROC-AUC 0.9100 pada validation set dengan training time cepat (0.52s) | Logistic Regression (F1: 0.7834), Random Forest (F1: 0.8085), XGBoost (F1: 0.8126) |
| D14 | 2026-11-01 | Pembekuan Test set pada evaluasi M04 | Menjamin objektivitas dan mencegah data snooping sebelum tuning dan kalibrasi final di M05 | Mengevaluasi test set berulang kali |
| D15 | 2026-11-01 | Ambang risiko final dikalibrasi: Low (< 0.35), Medium (0.35 - 0.70), High (>= 0.70) | Mengoptimalkan perlindungan pengguna tanpa alarm palsu berlebih pada link legitimate bertingkat | Ambang biner kaku 0.50 tanpa tingkatan risiko |
| D16 | 2026-11-01 | Penyesuaian target performa v1 (Recall 89.42%, ROC-AUC 0.9519 pada Test Set) | Pada v1 (analisis string URL murni tanpa membuka halaman), target simultan Recall >= 95% & FPR <= 2% tidak realistis karena variasi URL legitimate yang kompleks | Memaksakan ambang ekstrem yang merusak F1-score |
| D17 | 2026-11-01 | Kontrak API `POST /api/check` dengan validasi ketat (max 2048 karakter, HTTP 413; skema http/https saja, HTTP 400) | Mencegah eksploitasi buffer/overflow dan skema berbahaya (javascript:, data:, file:) | Menerima segala jenis string tanpa sanitasi |
| D18 | 2026-11-01 | Generator alasan berbasis fitur berbahasa Indonesia (`src/features/reasons.py`) | Membantu pengguna awam di Indonesia memahami mengapa suatu URL dikategorikan berisiko | Hanya mengembalikan label atau probabilitas mentah |
| D19 | 2026-11-01 | Tampilan frontend SPA dengan dark theme cyber-security sesuai design web.md, disajikan langsung via FastAPI StaticFiles, URL strictly plaintext non-clickable | Memenuhi spesifikasi antarmuka visual yang modern, responsif (mobile-friendly), aman dari misclick tautan berbahaya | Menampilkan URL sebagai tautan aktif (<a>); menggunakan framework SPA berat (React/Vue) yang membutuhkan server nodejs terpisah |
| D20 | 2026-11-01 | Explainability lokal berbasis TreeSHAP (`pred_contrib=True` bawaan LightGBM) dipadukan dengan aturan validasi aktif dwibahasa | Memberikan penjelasan logis yang akurat secara matematis dalam waktu sub-milidetik tanpa dependensi library eksternal yang lambat, serta menjamin tidak ada alasan fiktif untuk fitur yang tidak aktif | SHAP KernelExplainer (sangat lambat untuk online inference); aturan statis manual tanpa pembobotan model |
| D21 | 2026-11-01 | Rate limiter in-memory sliding window per IP (60 req/min) + zero-SSRF socket isolation test + sanitasi log URL | Melindungi layanan dari banjir request tanpa dependensi Redis eksternal, memastikan privasi data sensitif, dan membuktikan backend tidak membuka koneksi keluar ke domain target | Rate limiter Redis (membutuhkan infrastruktur daemon Redis terpisah untuk v1) |
| D22 | 2026-11-01 | Kontainerisasi mandiri dengan Docker & docker-compose, CI/CD GitHub Actions, serta kebijakan privasi Zero Data Retention | Menjamin portabilitas penuh antar platform (Render/Railway/VPS), otomasi pengujian berstandar tinggi, dan perlindungan privasi pengguna | Deployment manual bare-metal tanpa kontainer; penyimpanan URL pengguna ke database |

> Ubah keputusan di atas bila perlu, dan tambahkan baris baru setiap ada pilihan penting.

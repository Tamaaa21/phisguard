# Architecture

## Gambaran alur
```
Browser (frontend)
   │  POST /api/check { "url": "https://..." }
   ▼
FastAPI (backend)
   ├─ validasi + normalisasi URL
   ├─ ekstraksi fitur (lexical + host)   ← src/features/
   ├─ model.predict_proba()              ← src/model/ (artefak .joblib)
   └─ susun respons: label, skor, alasan
   ▼
Respons JSON → frontend menampilkan hasil
```

## Komponen
| Komponen | Teknologi (usulan) | Tanggung jawab |
|---|---|---|
| Frontend | HTML + JS sederhana (atau React/Vite) | Form input URL, tampilan hasil, disclaimer |
| Backend API | Python + FastAPI | Endpoint `/api/check`, `/api/health`, validasi, rate limit |
| Feature extractor | Python (urllib, tldextract) | Ubah URL menjadi vektor fitur numerik |
| Model | scikit-learn / XGBoost / LightGBM | Klasifikasi biner phishing vs benign |
| Pipeline training | Python script + notebook | Unduh data, bersihkan, latih, evaluasi, simpan model |
| Penyimpanan | File (`models/`, `data/`); SQLite opsional untuk log | Artefak model dan dataset |

## Struktur repo
```
phishguard/
├── CLAUDE.md
├── docs/plan/            # dokumen ini
├── data/
│   ├── raw/              # dataset asli (jangan di-commit jika besar)
│   └── processed/
├── notebooks/            # eksplorasi data
├── src/
│   ├── features/         # ekstraksi fitur URL
│   ├── training/         # skrip latih + evaluasi
│   ├── model/            # load model + predict
│   └── api/              # FastAPI app
├── models/               # artefak .joblib + metadata versi
├── web/                  # frontend
└── tests/
```

## Fitur yang diekstrak (v1, tanpa membuka halaman)
**Lexical:** panjang URL, panjang host, jumlah titik/tanda hubung/@/?/=/%/digit, jumlah subdomain, ada IP sebagai host, ada `https`, rasio digit, entropi karakter, jumlah path segment, keberadaan kata sensitif (login, verify, update, secure, akun, bank, dll).
**Host:** TLD (kategori), pemakaian URL shortener, panjang domain terdaftar, ada karakter `xn--` (punycode), kemiripan dengan merek populer (jarak edit).
**Opsional (v2):** umur domain (WHOIS), info sertifikat TLS, DNS. Perlu timeout ketat dan cache.

## Keamanan sistem
- Backend **tidak** melakukan request ke URL yang diperiksa pada v1 (hindari SSRF dan paparan konten berbahaya).
- Batasi panjang URL input, rate limit per IP, sanitasi output di frontend (jangan render URL sebagai link yang bisa diklik).
- Jangan simpan URL pengguna kecuali disetujui; jika disimpan, jelaskan di kebijakan privasi.

## Versi model
Setiap artefak model disimpan dengan metadata: tanggal latih, versi dataset, metrik uji, daftar fitur. API mengembalikan `model_version`.

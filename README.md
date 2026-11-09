# PhishGuard — Detektor Link Phishing Berbasis Machine Learning

PhishGuard adalah sistem deteksi link phishing cerdas berbasis Machine Learning (LightGBM) yang menganalisis 49 fitur *lexical*, struktur hostname, indikasi typosquatting merek, dan kata kunci sensitif dwibahasa (Indonesia & Inggris).

> 🔒 **Prinsip Keamanan Zero-SSRF:** PhishGuard **tidak pernah** membuka, melakukan ping, atau mengunduh isi halaman dari URL yang diperiksa. Seluruh inferensi bekerja secara aman dan instan (< 10 ms) langsung pada struktur string URL.

---

## 🎯 Fitur Utama

- **Analisis Instan & Aman (Zero-SSRF):** Prediksi risiko tanpa kontak jaringan ke server sasaran.
- **Deteksi Typosquatting & Merek Indonesia:** Analisis jarak edit (Levenshtein) terhadap 32 merek perbankan, e-wallet, dan e-commerce global serta lokal (BCA, Mandiri, BRI, BNI, Dana, OVO, GoPay, Shopee, Tokopedia, dll.).
- **Kamus Sensitif Dwibahasa:** Mendeteksi pola rekayasa sosial, pemancing kredensial, dan transaksi finansial dalam Bahasa Indonesia dan Inggris.
- **TreeSHAP Explainability:** Memberikan alasan diagnostik yang akurat dan transparan dalam Bahasa Indonesia berbasis kontribusi log-odds fitur.
- **3 Tingkat Risiko Terkalibrasi:**
  - 🟢 **Risiko Rendah** (`score < 0.35`): Pola URL aman dan konsisten dengan domain resmi.
  - 🟡 **Risiko Sedang** (`0.35 <= score < 0.70`): Terdapat anomali struktur atau indikator yang mencurigakan.
  - 🔴 **Risiko Tinggi** (`score >= 0.70`): Karakteristik kuat pemalsuan situs / serangan phishing.
- **Keamanan Input & Output:** Validasi ketat (maks 2048 karakter, tolak skema berbahaya `javascript:` / `file:`), perlindungan XSS, rate limiting per IP (60 req/menit), dan URL strictly plaintext (tidak dapat diklik untuk menghindari *accidental click*).

---

## 📊 Metrik Evaluasi Model (Test Set Independen)

Dievaluasi pada **1.690 sampel uji independen** dengan partisi `StratifiedGroupKFold` berdasarkan domain terdaftar (**Zero Domain Leakage**):

| Metrik Evaluasi | Nilai | Keterangan |
|---|---|---|
| **Akurasi** | **88.11%** | Proporsi klasifikasi benar secara keseluruhan |
| **Precision** | **85.85%** | Ketepatan saat menandai link sebagai phishing |
| **Recall (Sensitivitas)** | **89.42%** | Kemampuan mendeteksi link phishing sesungguhnya |
| **F1-Score** | **0.8760** | Keseimbangan harmonik antara precision dan recall |
| **False Positive Rate (FPR)** | **13.06%** | Tingkat alarm palsu pada situs aman |
| **ROC-AUC** | **0.9519** | Kemampuan pemisahan diskriminatif model |
| **Kecepatan Inferensi (p95)** | **< 10 ms** | Latensi periksa URL sangat cepat |

---

## 📁 Struktur Direktori

```text
phising-detc/
├── data/
│   ├── raw/                 # Dataset mentah (dataset_phishing.csv)
│   └── processed/           # Split train, val, test & matriks fitur (zero domain leakage)
├── docs/
│   ├── plan/                # Roadmap, keputusan arsitektur (decisions.md), spec per milestone
│   └── reports/             # Laporan evaluasi baseline (m04) dan tuning (m05)
├── models/
│   ├── latest.joblib         # Artefak model LightGBM terkalibrasi aktif
│   ├── metadata.json        # Hyperparameter, metrik test, dan konfigurasi ambang risiko
│   └── feature_names.json   # Daftar 49 urutan fitur tabular
├── src/
│   ├── api/                 # FastAPI REST API, schemas, dan rate limiter
│   ├── features/            # Ekstraktor 49 fitur, brand detector, kamus kata, & explainability
│   ├── model/               # Inference engine wrapper & TreeSHAP local contributor
│   └── training/            # Pipeline data preparation, training, tuning & kalibrasi probabilitas
├── web/                     # Antarmuka SPA frontend responsif (HTML5, modern CSS, JS)
├── tests/                   # 64 automated unit, integration, explainability & security tests
├── Dockerfile               # Container build multi-stage production
├── docker-compose.yml       # Orkestrasi Docker satu perintah
├── requirements.txt         # Dependensi Python
└── README.md
```

---

## 🚀 Panduan Menjalankan

### Cara 1: Menjalankan Next.js Fullstack (Rekomendasi — Standalone & Cepat)

Aplikasi telah berhasil dikonversi penuh ke **Next.js 15 (App Router, TypeScript, Tailwind CSS, Lucide)** dengan mesin inferensi LightGBM bawaan berbasis TypeScript murni (**Zero-Python Dependency**):

1. **Pasang dependensi Node.js:**
   ```bash
   npm install
   ```
2. **Jalankan server pengembangan:**
   ```bash
   npm run dev
   ```
   Atau untuk build produksi berkecepatan tinggi:
   ```bash
   npm run build
   npm start
   ```
3. **Buka di peramban web:**
   - 🌐 Antarmuka Web: [http://localhost:3000/](http://localhost:3000/)
   - 🩺 API Healthcheck: [http://localhost:3000/api/health](http://localhost:3000/api/health)
   - ℹ️ API Model Info: [http://localhost:3000/api/model-info](http://localhost:3000/api/model-info)
   - 🔍 API Check URL: `POST http://localhost:3000/api/check` with `{"url": "https://..."}`

> 💡 **Opsi Terhubung ke FastAPI:** Secara bawaan Next.js menjalankan inferensi model LightGBM secara mandiri di Node.js. Jika Anda ingin Route Handlers Next.js mem-forward request ke server FastAPI backend yang sedang berjalan di port 8000, cukup set `FASTAPI_BACKEND_URL=http://localhost:8000` di file `.env.local`.

---

### Cara 2: Menjalankan Backend FastAPI (Python Asli)

Jika Anda ingin menjalankan backend Python FastAPI secara terpisah:

1. **Pastikan Python 3.10+ terinstal.**
2. **Pasang dependensi:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Jalankan server aplikasi:**
   ```bash
   uvicorn src.api.main:app --reload --port 8000
   ```
4. **Buka di peramban web:**
   - 🌐 Antarmuka Web: [http://localhost:8000/](http://localhost:8000/)
   - 📖 API Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - 🩺 API Healthcheck: [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

### Cara 2: Menjalankan dengan Docker

```bash
# Build dan jalankan container
docker compose up --build -d

# Periksa status container
docker ps

# Buka aplikasi
http://localhost:8000/
```

Untuk menghentikan:
```bash
docker compose down
```

---

## 🔄 Cara Melatih Ulang Model (Retraining Pipeline)

Jika Anda memiliki data URL berlabel baru:

1. **Letakkan dataset baru di `data/raw/dataset_phishing.csv`.**
2. **Jalankan pembersihan dan partisi zero-leakage:**
   ```bash
   python src/training/prepare_data.py
   ```
   *(Menghasilkan `train.csv`, `val.csv`, dan `test.csv` di `data/processed/` tanpa tumpang tindih domain).*
3. **Ekstraksi 49 fitur URL:**
   ```bash
   python src/features/build_features.py
   ```
   *(Menghasilkan `train_features.csv`, `val_features.csv`, `test_features.csv`).*
4. **Jalankan hyperparameter tuning, kalibrasi probabilitas, dan evaluasi final:**
   ```bash
   python src/training/tune_and_calibrate.py
   ```
   *(Menghasilkan `models/latest.joblib`, `models/metadata.json`, dan laporan evaluasi).*

---

## 🧪 Menjalankan Pengujian Otomatis

Jalankan seluruh 64 pengujian (unit, feature extraction, model inference, API, TreeSHAP explainability, rate limiting, zero-SSRF security):

```bash
pytest -v
```

---

## 🔌 Dokumentasi REST API

### 1. Periksa URL (`POST /api/check`)

**Request:**
```bash
curl -X POST http://localhost:8000/api/check \
  -H "Content-Type: application/json" \
  -d '{"url": "http://bankmandiri.co.id.login-verifikasi-nasabah.xyz/auth"}'
```

**Response (HTTP 200 OK):**
```json
{
  "url": "http://bankmandiri.co.id.login-verifikasi-nasabah.xyz/auth",
  "label": "phishing",
  "score": 0.9234,
  "risk_level": "high",
  "reasons": [
    "Nama merek resmi disematkan pada subdomain untuk menyerupai situs asli.",
    "Koneksi tidak menggunakan enkripsi HTTPS (masih menggunakan protokol HTTP yang tidak aman).",
    "Mengandung kata kunci otentikasi akun atau pembaruan kredensial keamanan.",
    "Subdomain terlalu panjang atau bertingkat (32 karakter), menyimpang dari struktur resmi."
  ],
  "model_version": "1.0.0",
  "disclaimer": "Hasil ini merupakan perkiraan berbasis model machine learning pada struktur URL, bukan jaminan mutlak. Jangan memasukkan data rahasia atau kredensial pada situs yang mencurigakan."
}
```

### 2. Informasi Model (`GET /api/model-info`)

Mengembalikan metadata model aktif, waktu pelatihan, jumlah fitur, metrik test set, konfigurasi ambang batas, dan bobot fitur teratas.

---

## 🛡️ Kebijakan Privasi & Batasan Sistem

1. **Zero Data Retention:** URL yang dimasukkan pengguna hanya dianalisis di memori selama proses inferensi dan **tidak pernah disimpan secara permanen** ke basis data untuk menjaga privasi pengguna.
2. **Sanitasi Logging:** Parameter query sensitif dan informasi kredensial dalam URL disanitasi otomatis sebelum dicatat ke log aplikasi.
3. **Keterbatasan v1:** Analisis terbatas pada pola string URL. Situs sah baru atau domain kompleks terkadang dinilai sebagai *Medium Risk*. Pengguna tetap diimbau tidak pernah membagikan kode OTP atau PIN kepada pihak mana pun.

---

## 📈 Rencana Pemantauan & Retraining Berkala

- **Pemantauan Drift:** Secara berkala mengevaluasi distribusi entropi URL, frekuensi TLD baru, dan kemunculan variasi merek baru.
- **Jadwal Retraining:** Direkomendasikan retraining model secara berkala (misal: bulanan) dengan memperbarui basis data URL phishing terbaru.
- **Evolusi v2:** Integrasi fitur reputasi DNS, masa aktif domain (WHOIS age), serta validasi sertifikat TLS.

---

## 📄 Lisensi

Dikembangkan untuk edukasi, riset keamanan siber, dan perlindungan masyarakat dari penipuan digital di Indonesia.

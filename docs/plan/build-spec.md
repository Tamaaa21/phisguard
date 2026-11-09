# Build Spec — Detektor Link Phishing

## Modul
1. **Data pipeline**: unduh/gabung dataset phishing dan benign, deduplikasi, buat split train/val/test.
2. **Feature extraction**: fungsi `extract_features(url) -> dict` yang deterministik dan bisa dites.
3. **Training & evaluasi**: latih beberapa model, bandingkan, pilih satu, simpan artefak.
4. **Inference service**: muat model sekali saat start, prediksi cepat.
5. **API**: `POST /api/check`, `GET /api/health`, `GET /api/model-info`.
6. **Frontend**: halaman tunggal dengan input URL dan kartu hasil.
7. **Explainability**: tampilkan 3-5 faktor teratas yang mendorong skor.
8. **Operasional**: logging, rate limit, Docker, deploy.

## Kontrak API
### `POST /api/check`
Request:
```json
{ "url": "http://bca-verifikasi-akun.xyz/login" }
```
Respons:
```json
{
  "url": "http://bca-verifikasi-akun.xyz/login",
  "label": "phishing",
  "score": 0.97,
  "risk_level": "high",
  "reasons": [
    "Domain memakai TLD jarang (.xyz)",
    "Mengandung kata 'verifikasi' dan 'login'",
    "Tidak memakai HTTPS"
  ],
  "model_version": "2026-11-01-v1",
  "disclaimer": "Hasil ini perkiraan, bukan jaminan."
}
```
Error: `400` URL tidak valid, `413` URL terlalu panjang, `429` terlalu banyak permintaan.

`risk_level`: `low` (< 0.3), `medium` (0.3-0.7), `high` (> 0.7). Ambang diatur di `decisions.md`.

## Aturan data
- Pisahkan data uji **sebelum** feature engineering; jangan bocorkan info test ke training.
- Split berdasarkan **domain terdaftar**, bukan URL acak, supaya model tidak sekadar menghafal domain.
- Catat sumber, tanggal unduh, dan lisensi tiap dataset di `data/README.md`.
- Seimbangkan kelas atau gunakan class weight; laporkan metrik per kelas.

## Kriteria penerimaan v1
- Semua milestone m01-m10 selesai.
- Metrik uji memenuhi target di `product-overview.md`.
- Tes otomatis lulus; ada tes untuk ekstraksi fitur dan API.
- Disclaimer tampil jelas di UI.

# M05 - Tuning, Kalibrasi, & Pemilihan Model
Status: done

## Tujuan
Model final dengan probabilitas yang terkalibrasi dan ambang keputusan yang dipilih secara sadar.

## Cakupan
- Hyperparameter tuning (cross-validation yang dikelompokkan per domain)
- Kalibrasi probabilitas (Platt/isotonic)
- Pemilihan ambang risiko berdasarkan trade-off recall vs false-positive
- Evaluasi akhir **sekali** pada test set

## Tugas
- [x] GroupKFold per domain
- [x] Tuning terbatas (grid/random/Optuna)
- [x] Kurva kalibrasi dan Brier score
- [x] Tetapkan ambang low/medium/high; catat di `decisions.md`
- [x] Evaluasi test set, simpan laporan final
- [x] Simpan `models/latest.joblib` + `metadata.json`

## Kriteria selesai
- [x] Metrik test memenuhi target di `product-overview.md`, atau selisihnya dicatat jujur beserta alasannya
- [x] Metadata model berisi versi, tanggal, daftar fitur, metrik

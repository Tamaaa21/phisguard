# Extending

## Menambah fitur baru
1. Tambahkan fungsi di `src/features/` dan daftarkan di `extract_features`.
2. Tulis tes unit dengan beberapa URL contoh (phishing dan benign).
3. Latih ulang model (`python -m src.training.train`) dan bandingkan metrik dengan versi sebelumnya.
4. Catat hasilnya di `decisions.md` bila fitur diterima atau ditolak.

## Mengganti / menambah model
1. Tambahkan konfigurasi model di `src/training/`.
2. Pakai split dan metrik yang sama agar perbandingan adil.
3. Simpan artefak dengan nama berversi di `models/` dan perbarui `latest`.

## Menambah sumber data
1. Catat sumber, lisensi, dan tanggal di `data/README.md`.
2. Deduplikasi terhadap data yang ada, lalu buat ulang split per domain.
3. Evaluasi ulang pada test set yang **sama** untuk melihat dampak.

## Menambah endpoint
Tambahkan router di `src/api/`, skema Pydantic, dan tes di `tests/`. Perbarui kontrak API di `build-spec.md`.

## Retraining berkala
Jadwalkan skrip latih (cron/GitHub Actions), simpan metrik tiap versi, dan hanya promosikan model baru jika metrik tidak turun.

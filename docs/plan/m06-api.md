# M06 - Inference Service & API
Status: done

## Tujuan
Endpoint `POST /api/check` yang memuat model final dan mengembalikan hasil sesuai kontrak di `build-spec.md`.

## Tugas
- [x] Muat model sekali saat startup
- [x] Skema Pydantic untuk request/respons
- [x] Validasi URL (panjang, karakter, skema yang diizinkan)
- [x] Endpoint `/api/model-info` (versi, tanggal latih, metrik)
- [x] Penanganan error: 400, 413, 429, 500
- [x] CORS terbatas ke domain frontend

## Kriteria selesai
- [x] Contoh URL phishing dan benign menghasilkan respons sesuai kontrak
- [x] p95 latensi < 500 ms pada mesin lokal
- [x] Tes API lulus (httpx / TestClient)

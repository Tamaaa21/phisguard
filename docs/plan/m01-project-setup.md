# M01 - Setup Proyek & Lingkungan
Status: done

## Tujuan
Repo siap dikembangkan: struktur folder, virtual environment, dependensi, dan tes "hello world" berjalan.

## Cakupan
- Struktur folder sesuai `architecture.md`
- `requirements.txt`, `.gitignore`, `README.md`
- FastAPI minimal dengan `GET /api/health`
- Konfigurasi pytest

## Di luar cakupan
- Model, dataset, dan frontend

## Tugas
- [x] Buat repo + struktur folder
- [x] Siapkan venv dan instal dependensi
- [x] Tambah `.gitignore` (venv, data/raw, models besar, `__pycache__`)
- [x] Endpoint `/api/health` mengembalikan `{"status":"ok"}`
- [x] Satu tes pytest untuk health check

## Kriteria selesai
- [x] `uvicorn src.api.main:app` berjalan dan `/api/health` merespons
- [x] `pytest` lulus

# M02 - Pengumpulan & Pembersihan Dataset
Status: done

## Tujuan
Dataset URL berlabel (phishing = 1, benign = 0) yang bersih, tanpa duplikat, dengan split train/val/test per domain.

## Cakupan
- Pilih dan unduh sumber data (lihat `open-questions.md` no. 1)
- Normalisasi URL (lowercase host, hapus fragment, tangani skema)
- Deduplikasi
- Split per domain terdaftar (mis. 70/15/15)
- Dokumentasi sumber di `data/README.md`

## Di luar cakupan
- Ekstraksi fitur (M03)

## Tugas
- [x] Unduh data phishing dan benign, catat tanggal + lisensi
- [x] Skrip `src/training/prepare_data.py`
- [x] Hapus duplikat dan URL tidak valid
- [x] Cek keseimbangan kelas dan catat rasionya
- [x] Buat split per domain; simpan di `data/processed/`
- [x] Notebook eksplorasi: distribusi panjang URL, TLD, dll.

## Kriteria selesai
- [x] Tidak ada domain yang muncul di lebih dari satu split (dites otomatis)
- [x] `data/README.md` berisi sumber, tanggal, jumlah baris per kelas

## Catatan
Waspadai bias: benign dari situs populer global mungkin terlalu "bersih" dibanding phishing, sehingga model hanya belajar membedakan sumber data. Pertimbangkan menambah benign yang beragam (blog, toko kecil, situs lokal).

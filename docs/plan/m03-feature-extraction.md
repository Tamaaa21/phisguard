# M03 - Ekstraksi Fitur URL
Status: done

## Tujuan
Fungsi `extract_features(url)` yang mengubah URL menjadi dict fitur numerik, deterministik, dan cepat.

## Cakupan
- Fitur lexical dan host (lihat daftar di `architecture.md`)
- Penanganan URL aneh: tanpa skema, IP, punycode, port, userinfo
- Pembangunan matriks fitur untuk seluruh dataset

## Di luar cakupan
- Fitur yang butuh jaringan (WHOIS, DNS, TLS) dan konten halaman

## Tugas
- [x] Implementasi `src/features/`
- [x] Daftar kata sensitif (Inggris + Indonesia)
- [x] Deteksi kemiripan merek (jarak edit terhadap daftar merek populer)
- [x] Tes unit dengan >= 20 URL contoh
- [x] Simpan matriks fitur di `data/processed/`

## Kriteria selesai
- [x] Ekstraksi < 5 ms per URL (rata-rata)
- [x] Tidak ada NaN/exception untuk URL malformed; nilai default terdokumentasi
- [x] Tes lulus

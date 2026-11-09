# M09 - Pengujian, Keamanan, & Rate Limit
Status: done

## Tujuan
Sistem andal dan aman dari penyalahgunaan.

## Tugas
- [x] Tes unit fitur, tes API, tes regresi metrik model
- [x] Rate limit per IP
- [x] Batas ukuran dan panjang input; tolak skema berbahaya (`javascript:`, `file:`)
- [x] Pastikan backend tidak pernah melakukan request keluar ke URL input
- [x] Sanitasi output di frontend (cegah XSS dari string URL)
- [x] Uji URL ekstrem: sangat panjang, unicode/punycode, banyak parameter
- [x] Uji ketahanan: URL benign dengan pola mirip phishing (cek false positive), phishing yang dibuat tampak bersih (cek false negative)
- [x] Logging tanpa menyimpan data sensitif

## Kriteria selesai
- [x] Semua tes lulus di CI
- [x] Daftar keterbatasan model terdokumentasi di halaman "Tentang"

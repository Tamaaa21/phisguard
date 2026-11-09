# Product Overview — PhishGuard (nama sementara)

## Ringkasan
Website tempat pengguna menempelkan sebuah URL, lalu sistem memprediksi apakah URL itu **phishing** atau **aman** menggunakan model machine learning. Hasil ditampilkan beserta skor keyakinan dan alasan singkat.

## Masalah
Banyak orang awam di Indonesia menerima link mencurigakan lewat WhatsApp, SMS, dan email (palsu bank, kurir, marketplace, undian). Mereka sulit membedakan link asli dan palsu.

## Pengguna
- Pengguna umum yang ingin cek link sebelum diklik.
- Mahasiswa/peneliti yang ingin melihat cara kerja model (sifat edukasi).

## Tujuan
1. Pengguna dapat memeriksa satu URL dan mendapat hasil dalam < 2 detik.
2. Akurasi model terukur dan dilaporkan jujur (precision, recall, F1, false-positive rate).
3. Hasil bisa dijelaskan (fitur apa yang membuat URL dicurigai).

## Bukan tujuan (v1)
- Tidak membuka/mengunduh isi halaman web target (risiko keamanan dan lebih lambat).
- Tidak ada ekstensi browser, aplikasi mobile, atau akun pengguna.
- Tidak menggantikan Google Safe Browsing; ini alat bantu, bukan jaminan 100%.

## Metrik keberhasilan
- Recall phishing >= 95% dan false-positive rate <= 2% pada data uji terpisah (target awal, bisa disesuaikan di `decisions.md`).
- Waktu respons API p95 < 500 ms.

## Risiko utama
- Dataset basi: pola phishing berubah cepat, model cepat usang.
- Bias dataset: URL benign dari situs global mungkin tidak mewakili situs Indonesia.
- Pengguna terlalu percaya hasil "aman". Wajib ada disclaimer.

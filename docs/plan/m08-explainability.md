# M08 - Explainability
Status: done

## Tujuan
Menjelaskan kepada pengguna mengapa sebuah URL dinilai mencurigakan, dalam bahasa awam.

## Tugas
- [x] Hitung kontribusi fitur per prediksi (SHAP atau aturan berbasis feature importance)
- [x] Petakan fitur teknis ke kalimat Indonesia ("Domain memakai TLD jarang", "Memakai alamat IP, bukan nama domain")
- [x] Tampilkan maksimal 3-5 alasan teratas
- [x] Tes: alasan konsisten dengan fitur yang benar-benar aktif pada URL

## Kriteria selesai
- [x] Setiap respons `high`/`medium` memuat >= 1 alasan yang masuk akal
- [x] Tidak ada alasan yang menyesatkan pada contoh uji

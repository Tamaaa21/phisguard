# Open Questions

Pindahkan ke `decisions.md` setelah terjawab.

1. *(Terjawab di D8)* **Dataset**: Menggunakan `dataset_phishing.csv` yang ada di workspace.
2. *(Terjawab di D11)* **Konteks Indonesia**: Ya, kamus kata kunci sensitif (`masuk`, `akun`, `sandi`, `saldo`, `bayar`, dll.) dan daftar 14 merek/layanan Indonesia (BCA, Mandiri, BRI, BNI, Dana, OVO, GoPay, Shopee, Tokopedia, dll.) diintegrasikan ke modul ekstraksi fitur.
3. *(Terjawab di D15 & D16)* **Target performa**: Model v1 mencapai Recall 89.42%, F1 0.8760, dan ROC-AUC 0.9519 pada Test Set independen. Target simultan Recall >= 95% & FPR <= 2% tidak realistis pada v1 murni lexical string tanpa inspeksi DOM/sertifikat, sehingga diterapkan ambang risiko 3-tingkat (Low, Medium, High).
4. *(Terjawab di D21 & D22)* **Data pengguna**: Menggunakan kebijakan *Zero Data Retention*; URL pengguna hanya dianalisis di memori saat inferensi dan tidak disimpan secara permanen demi privasi. Query sensitif disanitasi dari log.
5. *(Terjawab di D22)* **Update model**: Retraining berkala secara offline (rekomendasi: bulanan) menggunakan skrip pipeline yang telah distandarisasi di `src/training/`.
6. *(Terjawab di D22)* **Deploy**: Kontainerisasi mandiri dengan `Dockerfile` dan `docker-compose.yml` yang kompatibel langsung dengan Render, Railway, Hugging Face Spaces, atau VPS Linux berbasis Docker.
7. *(Terjawab di D1)* **Penamaan & branding**: PhishGuard — Detektor Link Phishing (ML).
8. *(Terjawab di D9, D13, D16)* **Standar Evaluasi Akademik/Riset**: Metodologi evaluasi ketat tanpa kebocoran domain (*zero domain leakage* via StratifiedGroupKFold), perbandingan multi-model (Logistic Regression, Random Forest, XGBoost, LightGBM), kalibrasi probabilitas (Platt Scaling), serta pelaporan lengkap seluruh metrik standar (Precision, Recall, F1, FPR, ROC-AUC, PR-AUC, Brier score).

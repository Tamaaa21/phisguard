# Dokumentasi Dataset PhishGuard

Dokumen ini mencatat informasi asal-usul, pembersihan, dan partisi dataset yang digunakan pada proyek PhishGuard.

---

## 1. Sumber Data & Lisensi

- **File Sumber:** `data/raw/dataset_phishing.csv` (disediakan di repositori proyek).
- **Asal Dataset:** Dataset benchmark deteksi phishing akademis publik (koleksi gabungan PhishTank, OpenPhish, dan situs terdaftar legitimate).
- **Lisensi:** Open Access / Creative Commons (CC BY 4.0 / Academic research).
- **Tanggal Pemrosesan:** 2026-11-01.

---

## 2. Pembersihan & Normalisasi

Proses pembersihan dijalankan melalui skrip [`src/training/prepare_data.py`](../src/training/prepare_data.py):
1. **Normalisasi URL:**
   - Menghilangkan spasi awal/akhir.
   - Menambahkan skema default `http://` jika URL belum memiliki skema.
   - Mengubah skema dan host/domain menjadi huruf kecil (lowercase).
   - Menghilangkan URL fragment (`#...`).
2. **Penghapusan Duplikat:**
   - Ditemukan dan dihapus 14 URL duplikat.
   - Tidak ada label yang berkonflik.
3. **Penyaringan URL Valid:**
   - Memastikan host/domain dapat diekstrak dan tidak kosong.
   - 0 URL tidak valid (seluruh 11.416 URL yang tersisa valid).

---

## 3. Statistik Dataset & Keseimbangan Kelas

| Tahap | Legitimate (0) | Phishing (1) | Total Baris | Rasio Phishing |
|---|---|---|---|---|
| **Raw Dataset** | 5.715 | 5.715 | 11.430 | 50.00% |
| **Cleaned & Deduplicated** | 5.715 | 5.701 | 11.416 | 49.94% |

---

## 4. Partisi Data per Registered Domain (Zero Domain Leakage)

Untuk mencegah kebocoran data (data leakage) dan evaluasi yang terlalu optimis, data dibagi berdasarkan **Domain Terdaftar** (`registered_domain` via `tldextract`), bukan acak per URL. Semua URL dari domain yang sama dijamin berada pada split yang sama.

| Split | File | Jumlah Baris | Persentase | Legitimate | Phishing | Rasio Phishing | Domain Unik |
|---|---|---|---|---|---|---|---|
| **Train** | [`data/processed/train.csv`](processed/train.csv) | 7.550 | 66.14% | 3.685 | 3.865 | 51.19% | 4.466 |
| **Validation** | [`data/processed/val.csv`](processed/val.csv) | 2.176 | 19.06% | 1.134 | 1.042 | 47.89% | 1.085 |
| **Test** | [`data/processed/test.csv`](processed/test.csv) | 1.690 | 14.80% | 896 | 794 | 46.98% | 1.083 |
| **Total** | | **11.416** | **100%** | **5.715** | **5.701** | **49.94%** | **6.634** |

### Verifikasi Kebocoran Domain (Automated Leakage Test)
- **Overlap Train ∩ Val:** 0 domain
- **Overlap Train ∩ Test:** 0 domain
- **Overlap Val ∩ Test:** 0 domain
- **Status:** **Lulus (Zero Leakage)**, diverifikasi otomatis oleh suite pengujian `pytest tests/test_data_split.py`.


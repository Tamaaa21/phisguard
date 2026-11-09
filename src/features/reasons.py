"""Generate human-readable explanations (reasons) in Indonesian for URL check results.

Combines TreeSHAP local feature contributions with domain heuristic verification
so that every explanation is both mathematically grounded and strictly active on the target URL.
"""

from __future__ import annotations

from typing import Any


def generate_reasons(
    url: str,
    features: dict[str, float | int],
    score: float,
    risk_level: str,
    contributions: dict[str, float] | None = None,
) -> list[str]:
    """
    Generate 2-5 clear, Indonesian-language explanations for model assessment.

    Args:
        url: The evaluated URL string.
        features: Extracted 49 numerical features.
        score: Calibrated phishing probability (0.0 to 1.0).
        risk_level: One of 'low', 'medium', or 'high'.
        contributions: Optional dictionary of feature contributions (e.g. TreeSHAP log-odds).

    Returns:
        List of 2 to 5 explanatory bullet points in Indonesian.
    """
    contributions = contributions or {}
    level = risk_level.lower()

    # If assessed as LOW risk, return positive security indicators
    if level == "low":
        legit_reasons: list[str] = []

        if features.get("has_https", 0) == 1:
            legit_reasons.append("Menggunakan protokol enkripsi aman HTTPS.")

        if features.get("brand_in_subdomain", 0) == 0 and features.get("is_typosquatting", 0) == 0:
            legit_reasons.append("Struktur domain dan nama host teratur tanpa indikasi manipulasi merek resmi.")

        if features.get("has_ip", 0) == 0:
            legit_reasons.append("Menggunakan nama domain yang valid, bukan alamat IP langsung.")

        if features.get("has_sensitive_word", 0) == 0:
            legit_reasons.append("Tidak ditemukan kata kunci pemancing kredensial, perbankan, atau rekayasa sosial.")

        if features.get("entropy_url", 0.0) < 3.5:
            legit_reasons.append("Tingkat keacakan karakter normal dan konsisten dengan URL situs resmi.")

        return legit_reasons[:3] if legit_reasons else [
            "Struktur lexical URL dan domain konsisten dengan profil situs sah yang aman."
        ]

    # For HIGH or MEDIUM risk: evaluate active risk signals
    # Format: (primary_feature_key, condition_bool, base_priority, explanation_text)
    candidates: list[tuple[str, bool, float, str]] = [
        (
            "has_ip",
            features.get("has_ip", 0) == 1,
            2.5,
            "Memakai alamat IP langsung sebagai host, bukan nama domain resmi.",
        ),
        (
            "brand_in_subdomain",
            features.get("brand_in_subdomain", 0) == 1,
            2.3,
            "Nama merek resmi disematkan pada subdomain untuk menyerupai situs asli.",
        ),
        (
            "is_typosquatting",
            features.get("is_typosquatting", 0) == 1,
            2.2,
            "Nama domain memiliki kemiripan ejaan dengan merek resmi (indikasi typosquatting / pelesetan nama).",
        ),
        (
            "brand_in_path",
            features.get("brand_in_path", 0) == 1,
            1.8,
            "Nama merek terkemuka disisipkan pada jalur (path) URL untuk mengelabui korban.",
        ),
        (
            "has_punycode",
            features.get("has_punycode", 0) == 1,
            2.0,
            "Domain menggunakan karakter Punycode (awalan xn--) yang berpotensi menyamarkan huruf (homograph).",
        ),
        (
            "is_shortener",
            features.get("is_shortener", 0) == 1,
            1.7,
            "Menggunakan layanan pemendek tautan (URL Shortener) yang menyamarkan alamat tujuan akhir situs.",
        ),
        (
            "has_https",
            features.get("has_https", 0) == 0,
            1.2,
            "Koneksi tidak menggunakan enkripsi HTTPS (masih menggunakan protokol HTTP yang tidak aman).",
        ),
        (
            "nb_auth_words",
            features.get("nb_auth_words", 0) > 0 and features.get("nb_finance_words", 0) > 0,
            2.0,
            "Mengandung kombinasi kata sensitif otentikasi (login/verifikasi) dan perbankan/keuangan.",
        ),
        (
            "nb_finance_words",
            features.get("nb_finance_words", 0) > 0 and features.get("nb_auth_words", 0) == 0,
            1.6,
            "Mengandung kata kunci sensitif sektor perbankan atau transaksi keuangan.",
        ),
        (
            "nb_auth_words",
            features.get("nb_auth_words", 0) > 0 and features.get("nb_finance_words", 0) == 0,
            1.6,
            "Mengandung kata kunci otentikasi akun atau pembaruan kredensial keamanan.",
        ),
        (
            "nb_urgency_words",
            features.get("nb_urgency_words", 0) > 0,
            1.5,
            "Mengandung kata-kata desakan/urgensi yang lazim pada skema rekayasa sosial (social engineering).",
        ),
        (
            "tld_in_subdomain",
            features.get("tld_in_subdomain", 0) == 1 or features.get("tld_in_path", 0) == 1,
            1.8,
            "Ekstensi domain (seperti .com/.xyz) disisipkan di dalam subdomain atau path untuk mengaburkan domain asli.",
        ),
        (
            "length_subdomain",
            features.get("length_subdomain", 0) >= 15 or features.get("nb_subdomains", 0) >= 2,
            1.4,
            f"Subdomain terlalu panjang atau bertingkat ({int(features.get('length_subdomain', 0))} karakter), menyimpang dari struktur resmi.",
        ),
        (
            "nb_dots",
            features.get("nb_dots", 0) >= 4,
            1.3,
            f"Terdapat banyak tanda titik ({int(features.get('nb_dots', 0))} titik), umum digunakan untuk menyembunyikan nama domain sebenarnya.",
        ),
        (
            "nb_hyphens",
            features.get("nb_hyphens", 0) >= 3,
            1.2,
            f"Banyak tanda hubung (-) pada URL ({int(features.get('nb_hyphens', 0))} tanda), lazim pada domain tiruan.",
        ),
        (
            "entropy_url",
            features.get("entropy_url", 0.0) >= 3.8,
            1.3,
            f"Tingkat keacakan karakter URL (entropi {features.get('entropy_url', 0.0):.2f}) tinggi, indikasi token atau string acak.",
        ),
        (
            "ratio_digits_url",
            features.get("ratio_digits_url", 0.0) >= 0.18,
            1.1,
            f"Proporsi angka/digit pada URL relatif tinggi ({features.get('ratio_digits_url', 0.0)*100:.1f}%), mengindikasikan ID sintetis.",
        ),
        (
            "length_url",
            features.get("length_url", 0) >= 80,
            1.0,
            f"Panjang URL tidak wajar ({int(features.get('length_url', 0))} karakter).",
        ),
        (
            "nb_at",
            features.get("nb_at", 0) >= 1,
            1.9,
            "Mengandung karakter '@' yang dapat menyamarkan tujuan URL sebenarnya di beberapa browser.",
        ),
        (
            "nb_dslash",
            features.get("nb_dslash", 0) >= 1,
            1.5,
            "Terdapat tanda '//' ganda di luar skema protokol (potensi pengalihan / open redirect).",
        ),
        (
            "http_in_path",
            features.get("http_in_path", 0) == 1,
            1.4,
            "Teks 'http' ditemukan di dalam path URL (indikasi manipulasi rute tautan).",
        ),
        (
            "is_malformed",
            features.get("is_malformed", 0) == 1,
            2.0,
            "Format struktur URL tidak mengikuti kaidah penulisan standar yang sah.",
        ),
    ]

    # Score each active candidate using SHAP contribution + base rule priority
    scored_reasons: list[tuple[float, str]] = []
    for feat_name, condition, base_priority, reason_text in candidates:
        if condition:
            # Add positive TreeSHAP contribution if available
            shap_weight = max(0.0, contributions.get(feat_name, 0.0))
            combined_score = base_priority + (shap_weight * 1.5)
            scored_reasons.append((combined_score, reason_text))

    # Sort descending by importance score
    scored_reasons.sort(key=lambda x: x[0], reverse=True)

    # De-duplicate reason texts while maintaining sorted order
    seen: set[str] = set()
    final_reasons: list[str] = []
    for _, text in scored_reasons:
        if text not in seen:
            seen.add(text)
            final_reasons.append(text)

    # Ensure at least 1 sensible reason for high/medium risk
    if not final_reasons:
        if score >= 0.5:
            final_reasons.append(
                "Karakteristik lexical dan struktur domain memiliki kemiripan tinggi dengan pola phishing teridentifikasi."
            )
        else:
            final_reasons.append(
                "Struktur hostname dan parameter URL menunjukkan anomali yang perlu diwaspadai."
            )

    # Return top 3 to 5 reasons
    return final_reasons[:5]

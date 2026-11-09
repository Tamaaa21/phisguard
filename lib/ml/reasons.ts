/**
 * Generate human-readable explanations (reasons) in Indonesian for URL check results.
 */

export function generateReasons(
  url: string,
  features: Record<string, number>,
  score: number,
  riskLevel: "low" | "medium" | "high",
  contributions: Record<string, number> = {}
): string[] {
  const level = riskLevel.toLowerCase();

  // If assessed as LOW risk, return positive security indicators
  if (level === "low") {
    const legitReasons: string[] = [];

    if ((features["has_https"] ?? 0) === 1) {
      legitReasons.push("Menggunakan protokol enkripsi aman HTTPS.");
    }

    if (
      (features["brand_in_subdomain"] ?? 0) === 0 &&
      (features["is_typosquatting"] ?? 0) === 0
    ) {
      legitReasons.push(
        "Struktur domain dan nama host teratur tanpa indikasi manipulasi merek resmi."
      );
    }

    if ((features["has_ip"] ?? 0) === 0) {
      legitReasons.push(
        "Menggunakan nama domain yang valid, bukan alamat IP langsung."
      );
    }

    if ((features["has_sensitive_word"] ?? 0) === 0) {
      legitReasons.push(
        "Tidak ditemukan kata kunci pemancing kredensial, perbankan, atau rekayasa sosial."
      );
    }

    if ((features["entropy_url"] ?? 0.0) < 3.5) {
      legitReasons.push(
        "Tingkat keacakan karakter normal dan konsisten dengan URL situs resmi."
      );
    }

    return legitReasons.length > 0
      ? legitReasons.slice(0, 3)
      : [
          "Struktur lexical URL dan domain konsisten dengan profil situs sah yang aman.",
        ];
  }

  // Candidates for HIGH or MEDIUM risk
  interface ReasonCandidate {
    featName: string;
    condition: boolean;
    basePriority: number;
    text: string;
  }

  const candidates: ReasonCandidate[] = [
    {
      featName: "has_ip",
      condition: (features["has_ip"] ?? 0) === 1,
      basePriority: 2.5,
      text: "Memakai alamat IP langsung sebagai host, bukan nama domain resmi.",
    },
    {
      featName: "brand_in_subdomain",
      condition: (features["brand_in_subdomain"] ?? 0) === 1,
      basePriority: 2.3,
      text: "Nama merek resmi disematkan pada subdomain untuk menyerupai situs asli.",
    },
    {
      featName: "is_typosquatting",
      condition: (features["is_typosquatting"] ?? 0) === 1,
      basePriority: 2.2,
      text: "Nama domain memiliki kemiripan ejaan dengan merek resmi (indikasi typosquatting / pelesetan nama).",
    },
    {
      featName: "brand_in_path",
      condition: (features["brand_in_path"] ?? 0) === 1,
      basePriority: 1.8,
      text: "Nama merek terkemuka disisipkan pada jalur (path) URL untuk mengelabui korban.",
    },
    {
      featName: "has_punycode",
      condition: (features["has_punycode"] ?? 0) === 1,
      basePriority: 2.0,
      text: "Domain menggunakan karakter Punycode (awalan xn--) yang berpotensi menyamarkan huruf (homograph).",
    },
    {
      featName: "is_shortener",
      condition: (features["is_shortener"] ?? 0) === 1,
      basePriority: 1.7,
      text: "Menggunakan layanan pemendek tautan (URL Shortener) yang menyamarkan alamat tujuan akhir situs.",
    },
    {
      featName: "has_https",
      condition: (features["has_https"] ?? 0) === 0,
      basePriority: 1.2,
      text: "Koneksi tidak menggunakan enkripsi HTTPS (masih menggunakan protokol HTTP yang tidak aman).",
    },
    {
      featName: "nb_auth_words",
      condition:
        (features["nb_auth_words"] ?? 0) > 0 &&
        (features["nb_finance_words"] ?? 0) > 0,
      basePriority: 2.0,
      text: "Mengandung kombinasi kata sensitif otentikasi (login/verifikasi) dan perbankan/keuangan.",
    },
    {
      featName: "nb_finance_words",
      condition:
        (features["nb_finance_words"] ?? 0) > 0 &&
        (features["nb_auth_words"] ?? 0) === 0,
      basePriority: 1.6,
      text: "Mengandung kata kunci sensitif sektor perbankan atau transaksi keuangan.",
    },
    {
      featName: "nb_auth_words",
      condition:
        (features["nb_auth_words"] ?? 0) > 0 &&
        (features["nb_finance_words"] ?? 0) === 0,
      basePriority: 1.6,
      text: "Mengandung kata kunci otentikasi akun atau pembaruan kredensial keamanan.",
    },
    {
      featName: "nb_urgency_words",
      condition: (features["nb_urgency_words"] ?? 0) > 0,
      basePriority: 1.5,
      text: "Mengandung kata-kata desakan/urgensi yang lazim pada skema rekayasa sosial (social engineering).",
    },
    {
      featName: "tld_in_subdomain",
      condition:
        (features["tld_in_subdomain"] ?? 0) === 1 ||
        (features["tld_in_path"] ?? 0) === 1,
      basePriority: 1.8,
      text: "Ekstensi domain (seperti .com/.xyz) disisipkan di dalam subdomain atau path untuk mengaburkan domain asli.",
    },
    {
      featName: "length_subdomain",
      condition:
        (features["length_subdomain"] ?? 0) >= 15 ||
        (features["nb_subdomains"] ?? 0) >= 2,
      basePriority: 1.4,
      text: `Subdomain terlalu panjang atau bertingkat (${Math.round(
        features["length_subdomain"] ?? 0
      )} karakter), menyimpang dari struktur resmi.`,
    },
    {
      featName: "nb_dots",
      condition: (features["nb_dots"] ?? 0) >= 4,
      basePriority: 1.3,
      text: `Terdapat banyak tanda titik (${Math.round(
        features["nb_dots"] ?? 0
      )} titik), umum digunakan untuk menyembunyikan nama domain sebenarnya.`,
    },
    {
      featName: "nb_hyphens",
      condition: (features["nb_hyphens"] ?? 0) >= 3,
      basePriority: 1.2,
      text: `Banyak tanda hubung (-) pada URL (${Math.round(
        features["nb_hyphens"] ?? 0
      )} tanda), lazim pada domain tiruan.`,
    },
    {
      featName: "entropy_url",
      condition: (features["entropy_url"] ?? 0.0) >= 3.8,
      basePriority: 1.3,
      text: `Tingkat keacakan karakter URL (entropi ${(
        features["entropy_url"] ?? 0.0
      ).toFixed(2)}) tinggi, indikasi token atau string acak.`,
    },
    {
      featName: "ratio_digits_url",
      condition: (features["ratio_digits_url"] ?? 0.0) >= 0.18,
      basePriority: 1.1,
      text: `Proporsi angka/digit pada URL relatif tinggi (${(
        (features["ratio_digits_url"] ?? 0.0) * 100
      ).toFixed(1)}%), mengindikasikan ID sintetis.`,
    },
    {
      featName: "length_url",
      condition: (features["length_url"] ?? 0) >= 80,
      basePriority: 1.0,
      text: `Panjang URL tidak wajar (${Math.round(
        features["length_url"] ?? 0
      )} karakter).`,
    },
    {
      featName: "nb_at",
      condition: (features["nb_at"] ?? 0) >= 1,
      basePriority: 1.9,
      text: "Mengandung karakter '@' yang dapat menyamarkan tujuan URL sebenarnya di beberapa browser.",
    },
    {
      featName: "nb_dslash",
      condition: (features["nb_dslash"] ?? 0) >= 1,
      basePriority: 1.5,
      text: "Terdapat tanda '//' ganda di luar skema protokol (potensi pengalihan / open redirect).",
    },
    {
      featName: "http_in_path",
      condition: (features["http_in_path"] ?? 0) === 1,
      basePriority: 1.4,
      text: "Teks 'http' ditemukan di dalam path URL (indikasi manipulasi rute tautan).",
    },
    {
      featName: "is_malformed",
      condition: (features["is_malformed"] ?? 0) === 1,
      basePriority: 2.0,
      text: "Format struktur URL tidak mengikuti kaidah penulisan standar yang sah.",
    },
  ];

  const scored: Array<{ score: number; text: string }> = [];
  for (const c of candidates) {
    if (c.condition) {
      const contrib = Math.max(0, contributions[c.featName] || 0);
      const combinedScore = c.basePriority + contrib * 1.5;
      scored.push({ score: combinedScore, text: c.text });
    }
  }

  scored.sort((a, b) => b.score - a.score);

  const seen = new Set<string>();
  const finalReasons: string[] = [];
  for (const item of scored) {
    if (!seen.has(item.text)) {
      seen.add(item.text);
      finalReasons.push(item.text);
    }
  }

  if (finalReasons.length === 0) {
    if (score >= 0.5) {
      finalReasons.push(
        "Karakteristik lexical dan struktur domain memiliki kemiripan tinggi dengan pola phishing teridentifikasi."
      );
    } else {
      finalReasons.push(
        "Struktur hostname dan parameter URL menunjukkan anomali yang perlu diwaspadai."
      );
    }
  }

  return finalReasons.slice(0, 5);
}

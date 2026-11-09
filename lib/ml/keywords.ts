/**
 * Sensitive keyword dictionaries and detection logic for PhishGuard.
 */

export const AUTH_WORDS: Set<string> = new Set([
  "login", "signin", "sign-in", "log-in", "verify", "verification",
  "account", "secure", "security", "auth", "authenticate", "password",
  "credential", "recover", "recovery", "unlock", "confirm", "validation",
  "masuk", "daftar", "akun", "keamanan", "verifikasi", "sandi", "pulihkan",
]);

export const FINANCE_WORDS: Set<string> = new Set([
  "bank", "banking", "paypal", "pay", "payment", "card", "credit", "debit",
  "wallet", "crypto", "bitcoin", "bill", "invoice", "transfer",
  "bca", "mandiri", "bri", "bni", "cimb", "dana", "ovo", "gopay",
  "shopeepay", "linkaja", "saldo", "rekening", "tagihan", "bayar", "tabungan",
]);

export const URGENCY_WORDS: Set<string> = new Set([
  "update", "alert", "notice", "warning", "suspend", "suspended", "action",
  "required", "urgent", "limit", "limited", "expire", "expired", "block",
  "blocked", "pembaruan", "peringatan", "ditangguhkan", "diblokir", "kadaluarsa",
]);

const WORD_REGEX = /[a-zA-Z0-9_-]+/g;

export function countSensitiveWords(urlLower: string): {
  nb_sensitive_words: number;
  has_sensitive_word: number;
  nb_auth_words: number;
  nb_finance_words: number;
  nb_urgency_words: number;
} {
  const matches = urlLower.match(WORD_REGEX) || [];
  const tokens = new Set(matches);

  let authHits = 0;
  for (const w of AUTH_WORDS) {
    if (tokens.has(w) || (w.length > 4 && urlLower.includes(w))) {
      authHits++;
    }
  }

  let financeHits = 0;
  for (const w of FINANCE_WORDS) {
    if (tokens.has(w) || (w.length > 4 && urlLower.includes(w))) {
      financeHits++;
    }
  }

  let urgencyHits = 0;
  for (const w of URGENCY_WORDS) {
    if (tokens.has(w) || (w.length > 4 && urlLower.includes(w))) {
      urgencyHits++;
    }
  }

  const total = authHits + financeHits + urgencyHits;

  return {
    nb_sensitive_words: total,
    has_sensitive_word: total > 0 ? 1 : 0,
    nb_auth_words: authHits,
    nb_finance_words: financeHits,
    nb_urgency_words: urgencyHits,
  };
}

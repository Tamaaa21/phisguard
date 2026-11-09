"""Sensitive keyword dictionaries and detection logic for PhishGuard."""

from __future__ import annotations

import re

AUTH_WORDS: set[str] = {
    "login", "signin", "sign-in", "log-in", "verify", "verification",
    "account", "secure", "security", "auth", "authenticate", "password",
    "credential", "recover", "recovery", "unlock", "confirm", "validation",
    "masuk", "daftar", "akun", "keamanan", "verifikasi", "sandi", "pulihkan",
}

FINANCE_WORDS: set[str] = {
    "bank", "banking", "paypal", "pay", "payment", "card", "credit", "debit",
    "wallet", "crypto", "bitcoin", "bill", "invoice", "transfer",
    "bca", "mandiri", "bri", "bni", "cimb", "dana", "ovo", "gopay",
    "shopeepay", "linkaja", "saldo", "rekening", "tagihan", "bayar", "tabungan",
}

URGENCY_WORDS: set[str] = {
    "update", "alert", "notice", "warning", "suspend", "suspended", "action",
    "required", "urgent", "limit", "limited", "expire", "expired", "block",
    "blocked", "pembaruan", "peringatan", "ditangguhkan", "diblokir", "kadaluarsa",
}

ALL_SENSITIVE_WORDS: set[str] = AUTH_WORDS | FINANCE_WORDS | URGENCY_WORDS

# Compiled regex for fast token search
_WORD_REGEX = re.compile(r"[a-zA-Z0-9_-]+")


def count_sensitive_words(url_lower: str) -> dict[str, int]:
    """Count occurrences of sensitive keywords across categories."""
    tokens = set(_WORD_REGEX.findall(url_lower))

    auth_hits = sum(1 for w in AUTH_WORDS if w in tokens or (len(w) > 4 and w in url_lower))
    finance_hits = sum(1 for w in FINANCE_WORDS if w in tokens or (len(w) > 4 and w in url_lower))
    urgency_hits = sum(1 for w in URGENCY_WORDS if w in tokens or (len(w) > 4 and w in url_lower))

    total = auth_hits + finance_hits + urgency_hits

    return {
        "nb_sensitive_words": total,
        "has_sensitive_word": 1 if total > 0 else 0,
        "nb_auth_words": auth_hits,
        "nb_finance_words": finance_hits,
        "nb_urgency_words": urgency_hits,
    }


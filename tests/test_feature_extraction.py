"""Unit tests for URL feature extraction."""

from __future__ import annotations

import math
import time
import pytest

from src.features.extractor import extract_features, get_default_features, get_feature_names
from src.features.brand_detector import fast_levenshtein
from src.features.sensitive_words import count_sensitive_words

# 25 Diverse URLs representing various legitimate, phishing, and edge-case patterns
SAMPLE_URLS: list[dict[str, str | int]] = [
    # 1-5: Legitimate standard URLs
    {"url": "https://www.google.com/search?q=machine+learning", "is_ip": 0, "has_https": 1},
    {"url": "https://en.wikipedia.org/wiki/Phishing", "is_ip": 0, "has_https": 1},
    {"url": "https://github.com/tiangolo/fastapi", "is_ip": 0, "has_https": 1},
    {"url": "https://docs.python.org/3/library/urllib.parse.html", "is_ip": 0, "has_https": 1},
    {"url": "https://bankmandiri.co.id/personal", "is_ip": 0, "has_https": 1},

    # 6-10: IP address hosts (common in phishing/scams)
    {"url": "http://192.168.1.1/admin/login.php", "is_ip": 1, "has_https": 0},
    {"url": "http://218.45.1.2/bca/update-rekening", "is_ip": 1, "has_https": 0},
    {"url": "http://104.244.42.1/session/verify", "is_ip": 1, "has_https": 0},
    {"url": "http://127.0.0.1:8080/test", "is_ip": 1, "has_https": 0},
    {"url": "http://0x7f000001/phish", "is_ip": 1, "has_https": 0},

    # 11-15: Targeted brand in subdomain (spoofing)
    {"url": "http://paypal.com.account-verification.xyz/login", "is_ip": 0, "brand_in_sub": 1},
    {"url": "http://appleid.apple.com.secure-update.cc/verify", "is_ip": 0, "brand_in_sub": 1},
    {"url": "http://bca.klikbca.ebanking-secure.id/masuk", "is_ip": 0, "brand_in_sub": 1},
    {"url": "http://netflix.account-billing.info/renew", "is_ip": 0, "brand_in_sub": 1},
    {"url": "http://bri.brimo.klaim-promo-undian.xyz/login", "is_ip": 0, "brand_in_sub": 1},

    # 16-18: Shortened URLs & Punycode
    {"url": "http://bit.ly/3xYqz9A", "is_shortener": 1},
    {"url": "https://s.id/saldo-dana-gratis", "is_shortener": 1},
    {"url": "https://xn--e1afmkfd.xn--p1ai/path/auth", "has_punycode": 1},

    # 19-21: URLs with ports and userinfo
    {"url": "http://admin:pass123@malicious-host.org:8080/portal", "has_userinfo": 1, "has_port": 1},
    {"url": "https://login-service.net:8443/auth", "has_port": 1},
    {"url": "http://dana-id.klaim-saldo.xyz/bayar?token=9f8a7b6c5d4e", "brand_in_sub": 1},

    # 22-25: Edge cases & malformed URLs
    {"url": "   http://whitespace-trimmed.com/   ", "is_ip": 0},
    {"url": "malformed_string_without_scheme_or_dots", "is_malformed": 1},
    {"url": "", "is_malformed": 1},
    {"url": "http://///", "is_malformed": 1},
]


def test_feature_names_consistency():
    feat_names = get_feature_names()
    default_feats = get_default_features()
    assert len(feat_names) == len(default_feats)
    assert set(feat_names) == set(default_feats.keys())
    assert len(feat_names) >= 45


@pytest.mark.parametrize("item", SAMPLE_URLS)
def test_extract_features_no_nan_no_exception(item):
    url = item["url"]
    feats = extract_features(url)

    assert isinstance(feats, dict)
    assert set(feats.keys()) == set(get_feature_names())

    # Ensure no NaN or infinite values
    for k, v in feats.items():
        assert isinstance(v, (int, float)), f"Feature {k} has unexpected type {type(v)}"
        assert not math.isnan(v), f"Feature {k} is NaN for URL: {url}"
        assert not math.isinf(v), f"Feature {k} is Inf for URL: {url}"

    # Specific property assertions
    if "is_ip" in item:
        assert feats["has_ip"] == item["is_ip"]
    if "has_https" in item:
        assert feats["has_https"] == item["has_https"]
    if "brand_in_sub" in item:
        assert feats["brand_in_subdomain"] == item["brand_in_sub"]
    if "is_shortener" in item:
        assert feats["is_shortener"] == item["is_shortener"]
    if "has_punycode" in item:
        assert feats["has_punycode"] == item["has_punycode"]
    if "has_userinfo" in item:
        assert feats["has_userinfo"] == item["has_userinfo"]
    if "has_port" in item:
        assert feats["has_port"] == item["has_port"]
    if "is_malformed" in item:
        assert feats["is_malformed"] == item["is_malformed"]


def test_extraction_speed_under_5ms():
    urls = [str(item["url"]) for item in SAMPLE_URLS[:20]]
    # Warmup
    for u in urls:
        extract_features(u)

    # Measure 5 runs of 20 URLs = 100 extractions
    t0 = time.perf_counter()
    for _ in range(5):
        for u in urls:
            extract_features(u)
    total_time = time.perf_counter() - t0
    avg_ms = (total_time / 100) * 1000

    assert avg_ms < 5.0, f"Extraction too slow: {avg_ms:.2f} ms per URL (expected < 5.0 ms)"


def test_sensitive_words_detection():
    res = count_sensitive_words("http://bank-mandiri.com/masuk-akun-sandi-verifikasi")
    assert res["nb_sensitive_words"] > 0
    assert res["has_sensitive_word"] == 1
    assert res["nb_auth_words"] > 0
    assert res["nb_finance_words"] > 0


def test_fast_levenshtein():
    assert fast_levenshtein("paypal", "paypal") == 0
    assert fast_levenshtein("paypal", "paypa1") == 1
    assert fast_levenshtein("google", "g00gle") == 2
    assert fast_levenshtein("bca", "bri") == 2


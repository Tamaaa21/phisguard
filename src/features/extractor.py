"""URL Feature Extractor for PhishGuard (lexical, host, structural, brand, sensitive)."""

from __future__ import annotations

from collections import Counter
import ipaddress
import math
import re
from urllib.parse import urlparse

import tldextract

from src.features.brand_detector import analyze_brand_presence
from src.features.sensitive_words import count_sensitive_words

# Pre-compiled regexes
_IPV4_REGEX = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
_HEX_IP_REGEX = re.compile(r"^0x[0-9a-fA-F]+(?:\.0x[0-9a-fA-F]+){3}$")

KNOWN_SHORTENERS: set[str] = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "buff.ly", "ow.ly",
    "rebrand.ly", "s.id", "cutt.ly", "tiny.cc", "clck.ru", "rotf.lol", "v.gd",
    "qr.net", "shorturl.at", "adf.ly", "bc.vc", "shorte.st",
}

COMMON_TLDS: set[str] = {
    "com", "org", "net", "edu", "gov", "mil", "io", "co", "id", "xyz", "top",
    "online", "site", "info", "ru", "cn", "club", "vip", "app",
}

_EXTRACTOR = tldextract.TLDExtract(cache_dir="data/processed/.tld_cache")


def calculate_entropy(text: str) -> float:
    """Compute Shannon entropy of a string."""
    if not text:
        return 0.0
    length = len(text)
    counts = Counter(text)
    return -sum((cnt / length) * math.log2(cnt / length) for cnt in counts.values())


def is_ip_address(host: str) -> bool:
    """Check if host is an IPv4 (dotted, hex, integer) or IPv6 address."""
    if not host:
        return False
    clean_host = host.split(":")[0].strip("[]")
    try:
        if clean_host.startswith("0x") or clean_host.startswith("0X"):
            val = int(clean_host, 16)
            if 0 <= val <= 0xFFFFFFFF:
                return True
        elif clean_host.isdigit():
            val = int(clean_host)
            if 0 <= val <= 0xFFFFFFFF:
                return True
        ipaddress.ip_address(clean_host)
        return True
    except (ValueError, OverflowError):
        return False


def get_default_features() -> dict[str, float | int]:
    """Default feature vector returned for malformed or empty URLs."""
    return {
        "length_url": 0,
        "length_hostname": 0,
        "length_path": 0,
        "nb_dots": 0,
        "nb_hyphens": 0,
        "nb_at": 0,
        "nb_qm": 0,
        "nb_and": 0,
        "nb_or": 0,
        "nb_eq": 0,
        "nb_underscore": 0,
        "nb_tilde": 0,
        "nb_percent": 0,
        "nb_slash": 0,
        "nb_colon": 0,
        "nb_semicolon": 0,
        "nb_dollar": 0,
        "nb_space": 0,
        "nb_www": 0,
        "nb_com": 0,
        "nb_dslash": 0,
        "http_in_path": 0,
        "https_token": 0,
        "ratio_digits_url": 0.0,
        "ratio_digits_host": 0.0,
        "entropy_url": 0.0,
        "entropy_host": 0.0,
        "has_ip": 0,
        "has_https": 0,
        "has_port": 0,
        "has_userinfo": 0,
        "nb_subdomains": 0,
        "length_subdomain": 0,
        "nb_path_segments": 0,
        "has_punycode": 0,
        "is_shortener": 0,
        "length_registered_domain": 0,
        "tld_in_subdomain": 0,
        "tld_in_path": 0,
        "nb_sensitive_words": 0,
        "has_sensitive_word": 0,
        "nb_auth_words": 0,
        "nb_finance_words": 0,
        "nb_urgency_words": 0,
        "min_brand_edit_distance": 10,
        "is_typosquatting": 0,
        "brand_in_subdomain": 0,
        "brand_in_path": 0,
        "is_malformed": 1,
    }


def extract_features(raw_url: str) -> dict[str, float | int]:
    """
    Extract a dictionary of numerical features from a single URL string.
    Guaranteed to never raise an exception and never return NaN.
    """
    if not isinstance(raw_url, str):
        return get_default_features()

    url = raw_url.strip()
    if not url:
        return get_default_features()

    # Prepend http:// if scheme missing for parsing
    parse_url = url
    if "://" not in parse_url:
        if parse_url.startswith("//"):
            parse_url = "http:" + parse_url
        else:
            parse_url = "http://" + parse_url

    try:
        parsed = urlparse(parse_url)
    except Exception:
        return get_default_features()

    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path
    query = parsed.query

    if not netloc:
        return get_default_features()

    # Parse host & port & userinfo
    has_userinfo = 1 if "@" in netloc else 0
    host = netloc
    if "@" in host:
        host = host.split("@")[-1]

    has_port = 0
    if ":" in host and not host.startswith("["):
        host_parts = host.split(":")
        host = host_parts[0]
        has_port = 1

    # Valid hostname must have at least one dot or be a recognized IP or localhost
    if "." not in host and not is_ip_address(host) and host != "localhost":
        return get_default_features()

    # TLD extraction
    ext = _EXTRACTOR(host)
    if ext.ipv4:
        registered_domain = ext.ipv4
        subdomain = ""
        suffix = ""
    else:
        subdomain = ext.subdomain
        suffix = ext.suffix
        registered_domain = f"{ext.domain}.{suffix}".lower() if ext.domain and suffix else ext.domain.lower()

    # Structural & character counts
    len_url = len(url)
    len_host = len(host)
    len_path = len(path)

    digits_url = sum(1 for c in url if c.isdigit())
    digits_host = sum(1 for c in host if c.isdigit())

    # Path segments
    segments = [s for s in path.split("/") if s]
    nb_path_segments = len(segments)

    # Subdomain count
    nb_subdomains = len(subdomain.split(".")) if subdomain else 0

    # Shortener check
    is_shortener = 1 if registered_domain in KNOWN_SHORTENERS else 0

    # Punycode check
    has_punycode = 1 if "xn--" in host else 0

    # TLD in subdomain or path
    sub_parts = set(subdomain.split(".")) if subdomain else set()
    tld_in_subdomain = 1 if any(t in sub_parts for t in COMMON_TLDS) else 0

    path_lower = path.lower()
    tld_in_path = 1 if any(f".{t}" in path_lower for t in COMMON_TLDS) else 0

    # Sensitive words analysis
    sensitive_feats = count_sensitive_words(url.lower())

    # Brand presence analysis
    brand_feats = analyze_brand_presence(registered_domain, subdomain, path)

    # Dslash count after initial scheme://
    after_scheme = url.split("://", 1)[-1] if "://" in url else url
    nb_dslash = after_scheme.count("//")

    features = {
        "length_url": len_url,
        "length_hostname": len_host,
        "length_path": len_path,
        "nb_dots": url.count("."),
        "nb_hyphens": url.count("-"),
        "nb_at": url.count("@"),
        "nb_qm": url.count("?"),
        "nb_and": url.count("&"),
        "nb_or": url.count("|"),
        "nb_eq": url.count("="),
        "nb_underscore": url.count("_"),
        "nb_tilde": url.count("~"),
        "nb_percent": url.count("%"),
        "nb_slash": url.count("/"),
        "nb_colon": url.count(":"),
        "nb_semicolon": url.count(";"),
        "nb_dollar": url.count("$"),
        "nb_space": url.count(" ") + url.lower().count("%20"),
        "nb_www": url.lower().count("www"),
        "nb_com": url.lower().count("com"),
        "nb_dslash": nb_dslash,
        "http_in_path": 1 if "http" in path_lower else 0,
        "https_token": 1 if "https" in host else 0,
        "ratio_digits_url": round(digits_url / max(1, len_url), 4),
        "ratio_digits_host": round(digits_host / max(1, len_host), 4),
        "entropy_url": round(calculate_entropy(url), 4),
        "entropy_host": round(calculate_entropy(host), 4),
        "has_ip": 1 if is_ip_address(host) else 0,
        "has_https": 1 if scheme == "https" else 0,
        "has_port": has_port,
        "has_userinfo": has_userinfo,
        "nb_subdomains": nb_subdomains,
        "length_subdomain": len(subdomain),
        "nb_path_segments": nb_path_segments,
        "has_punycode": has_punycode,
        "is_shortener": is_shortener,
        "length_registered_domain": len(registered_domain),
        "tld_in_subdomain": tld_in_subdomain,
        "tld_in_path": tld_in_path,
        **sensitive_feats,
        **brand_feats,
        "is_malformed": 0,
    }

    return features


def get_feature_names() -> list[str]:
    """Return ordered list of all feature names."""
    return list(get_default_features().keys())

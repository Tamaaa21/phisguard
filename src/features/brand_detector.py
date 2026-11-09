"""Brand similarity and typosquatting detection for URL host and path."""

from __future__ import annotations

import re

POPULAR_BRANDS: list[str] = [
    # Global Tech & Social
    "google", "apple", "microsoft", "amazon", "facebook", "instagram",
    "whatsapp", "netflix", "paypal", "telegram", "twitter", "yahoo", "linkedin",
    "dropbox", "adobe", "spotify", "tiktok", "steam",
    # Indonesian Banking & FinTech
    "bca", "klikbca", "mandiri", "livin", "bri", "brimo", "bni", "cimb", "danamon",
    "dana", "ovo", "gopay", "shopeepay", "linkaja", "jenius", "jago",
    # Indonesian E-commerce & Logistics
    "tokopedia", "shopee", "bukalapak", "blibli", "lazada", "jne", "sicepat",
]

_TOKEN_SPLIT = re.compile(r"[.\-_]+")


def fast_levenshtein(s1: str, s2: str) -> int:
    """Compute Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return fast_levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def analyze_brand_presence(
    registered_domain: str,
    subdomain: str,
    path: str,
) -> dict[str, int | float]:
    """Analyze brand targeting, typosquatting, and brand presence in subdomain/path."""
    reg_domain_name = registered_domain.split(".")[0].lower() if registered_domain else ""
    subdomain_lower = subdomain.lower() if subdomain else ""
    path_lower = path.lower() if path else ""

    # Split domain and subdomain into tokens
    domain_tokens = [t for t in _TOKEN_SPLIT.split(reg_domain_name) if len(t) >= 3]

    min_edit_dist = 99
    is_typosquatting = 0

    for brand in POPULAR_BRANDS:
        # Check domain token distance
        for token in domain_tokens:
            if abs(len(token) - len(brand)) <= 2:
                dist = fast_levenshtein(token, brand)
                if dist < min_edit_dist:
                    min_edit_dist = dist
                # If distance is 1 or 2 and token is not exact brand
                if 0 < dist <= 2 and len(brand) >= 4:
                    is_typosquatting = 1

    # Check if a popular brand appears in subdomain while not being the registered domain
    brand_in_subdomain = 0
    if subdomain_lower:
        for brand in POPULAR_BRANDS:
            if brand in subdomain_lower and brand != reg_domain_name:
                brand_in_subdomain = 1
                break

    # Check if brand appears in path
    brand_in_path = 0
    if path_lower:
        for brand in POPULAR_BRANDS:
            if f"/{brand}" in path_lower or f"{brand}-" in path_lower or f"={brand}" in path_lower:
                brand_in_path = 1
                break

    # Cap min_edit_dist
    if min_edit_dist == 99:
        min_edit_dist = 10

    return {
        "min_brand_edit_distance": min_edit_dist,
        "is_typosquatting": is_typosquatting,
        "brand_in_subdomain": brand_in_subdomain,
        "brand_in_path": brand_in_path,
    }


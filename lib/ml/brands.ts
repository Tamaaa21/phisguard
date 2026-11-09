/**
 * Brand similarity, typosquatting, and brand presence detection.
 */

export const POPULAR_BRANDS: string[] = [
  // Global Tech & Social
  "google", "apple", "microsoft", "amazon", "facebook", "instagram",
  "whatsapp", "netflix", "paypal", "telegram", "twitter", "yahoo", "linkedin",
  "dropbox", "adobe", "spotify", "tiktok", "steam",
  // Indonesian Banking & FinTech
  "bca", "klikbca", "mandiri", "livin", "bri", "brimo", "bni", "cimb", "danamon",
  "dana", "ovo", "gopay", "shopeepay", "linkaja", "jenius", "jago",
  // Indonesian E-commerce & Logistics
  "tokopedia", "shopee", "bukalapak", "blibli", "lazada", "jne", "sicepat",
];

const TOKEN_SPLIT = /[.\-_]+/;

/**
 * Levenshtein distance between two strings.
 */
export function fastLevenshtein(s1: string, s2: string): number {
  if (s1.length < s2.length) {
    return fastLevenshtein(s2, s1);
  }
  if (s2.length === 0) {
    return s1.length;
  }

  let previousRow: number[] = Array.from({ length: s2.length + 1 }, (_, i) => i);

  for (let i = 0; i < s1.length; i++) {
    const c1 = s1[i];
    const currentRow: number[] = [i + 1];

    for (let j = 0; j < s2.length; j++) {
      const c2 = s2[j];
      const insertions = previousRow[j + 1] + 1;
      const deletions = currentRow[j] + 1;
      const substitutions = previousRow[j] + (c1 !== c2 ? 1 : 0);
      currentRow.push(Math.min(insertions, deletions, substitutions));
    }

    previousRow = currentRow;
  }

  return previousRow[previousRow.length - 1];
}

export function analyzeBrandPresence(
  registeredDomain: string,
  subdomain: string,
  path: string
): {
  min_brand_edit_distance: number;
  is_typosquatting: number;
  brand_in_subdomain: number;
  brand_in_path: number;
} {
  const regDomainName = registeredDomain ? registeredDomain.split(".")[0].toLowerCase() : "";
  const subdomainLower = subdomain ? subdomain.toLowerCase() : "";
  const pathLower = path ? path.toLowerCase() : "";

  // Split domain into tokens
  const domainTokens = regDomainName
    ? regDomainName.split(TOKEN_SPLIT).filter((t) => t.length >= 3)
    : [];

  let minEditDist = 99;
  let isTyposquatting = 0;

  for (const brand of POPULAR_BRANDS) {
    for (const token of domainTokens) {
      if (Math.abs(token.length - brand.length) <= 2) {
        const dist = fastLevenshtein(token, brand);
        if (dist < minEditDist) {
          minEditDist = dist;
        }
        if (dist > 0 && dist <= 2 && brand.length >= 4) {
          isTyposquatting = 1;
        }
      }
    }
  }

  // Check if popular brand appears in subdomain while not being the registered domain
  let brandInSubdomain = 0;
  if (subdomainLower) {
    for (const brand of POPULAR_BRANDS) {
      if (subdomainLower.includes(brand) && brand !== regDomainName) {
        brandInSubdomain = 1;
        break;
      }
    }
  }

  // Check if brand appears in path
  let brandInPath = 0;
  if (pathLower) {
    for (const brand of POPULAR_BRANDS) {
      if (
        pathLower.includes(`/${brand}`) ||
        pathLower.includes(`${brand}-`) ||
        pathLower.includes(`=${brand}`)
      ) {
        brandInPath = 1;
        break;
      }
    }
  }

  if (minEditDist === 99) {
    minEditDist = 10;
  }

  return {
    min_brand_edit_distance: minEditDist,
    is_typosquatting: isTyposquatting,
    brand_in_subdomain: brandInSubdomain,
    brand_in_path: brandInPath,
  };
}

import { parse } from "tldts";
import { analyzeBrandPresence } from "./brands";
import { countSensitiveWords } from "./keywords";
import { calculateEntropy } from "./entropy";

export const KNOWN_SHORTENERS: Set<string> = new Set([
  "bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "buff.ly", "ow.ly",
  "rebrand.ly", "s.id", "cutt.ly", "tiny.cc", "clck.ru", "rotf.lol", "v.gd",
  "qr.net", "shorturl.at", "adf.ly", "bc.vc", "shorte.st",
]);

export const COMMON_TLDS: Set<string> = new Set([
  "com", "org", "net", "edu", "gov", "mil", "io", "co", "id", "xyz", "top",
  "online", "site", "info", "ru", "cn", "club", "vip", "app",
]);

const IPV4_REGEX = /^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/;

export function isIpAddress(host: string): boolean {
  if (!host) return false;
  const cleanHost = host.split(":")[0].replace(/[\[\]]/g, "");

  if (IPV4_REGEX.test(cleanHost)) {
    const parts = cleanHost.split(".").map(Number);
    if (parts.every((p) => p >= 0 && p <= 255)) {
      return true;
    }
  }

  // Hex or Integer IP
  if (cleanHost.toLowerCase().startsWith("0x")) {
    const val = parseInt(cleanHost, 16);
    if (!isNaN(val) && val >= 0 && val <= 0xffffffff) {
      return true;
    }
  } else if (/^\d+$/.test(cleanHost)) {
    const val = parseInt(cleanHost, 10);
    if (!isNaN(val) && val >= 0 && val <= 0xffffffff) {
      return true;
    }
  }

  // IPv6 check
  if (cleanHost.includes(":")) {
    return true;
  }

  return false;
}

export function getDefaultFeatures(): Record<string, number> {
  return {
    length_url: 0,
    length_hostname: 0,
    length_path: 0,
    nb_dots: 0,
    nb_hyphens: 0,
    nb_at: 0,
    nb_qm: 0,
    nb_and: 0,
    nb_or: 0,
    nb_eq: 0,
    nb_underscore: 0,
    nb_tilde: 0,
    nb_percent: 0,
    nb_slash: 0,
    nb_colon: 0,
    nb_semicolon: 0,
    nb_dollar: 0,
    nb_space: 0,
    nb_www: 0,
    nb_com: 0,
    nb_dslash: 0,
    http_in_path: 0,
    https_token: 0,
    ratio_digits_url: 0.0,
    ratio_digits_host: 0.0,
    entropy_url: 0.0,
    entropy_host: 0.0,
    has_ip: 0,
    has_https: 0,
    has_port: 0,
    has_userinfo: 0,
    nb_subdomains: 0,
    length_subdomain: 0,
    nb_path_segments: 0,
    has_punycode: 0,
    is_shortener: 0,
    length_registered_domain: 0,
    tld_in_subdomain: 0,
    tld_in_path: 0,
    nb_sensitive_words: 0,
    has_sensitive_word: 0,
    nb_auth_words: 0,
    nb_finance_words: 0,
    nb_urgency_words: 0,
    min_brand_edit_distance: 10,
    is_typosquatting: 0,
    brand_in_subdomain: 0,
    brand_in_path: 0,
    is_malformed: 1,
  };
}

function countChar(str: string, char: string): number {
  let count = 0;
  for (let i = 0; i < str.length; i++) {
    if (str[i] === char) count++;
  }
  return count;
}

function countSubstr(str: string, substr: string): number {
  if (!substr) return 0;
  let count = 0;
  let pos = 0;
  while ((pos = str.indexOf(substr, pos)) !== -1) {
    count++;
    pos += substr.length;
  }
  return count;
}

export function extractFeatures(rawUrl: string): Record<string, number> {
  if (typeof rawUrl !== "string") {
    return getDefaultFeatures();
  }

  const url = rawUrl.trim();
  if (!url) {
    return getDefaultFeatures();
  }

  let parseUrl = url;
  if (!parseUrl.includes("://")) {
    if (parseUrl.startsWith("//")) {
      parseUrl = "http:" + parseUrl;
    } else {
      parseUrl = "http://" + parseUrl;
    }
  }

  let parsed: URL;
  try {
    parsed = new URL(parseUrl);
  } catch {
    return getDefaultFeatures();
  }

  const scheme = parsed.protocol.replace(":", "").toLowerCase();
  let netloc = parsed.host.toLowerCase();
  const path = parsed.pathname || "";

  if (!netloc) {
    return getDefaultFeatures();
  }

  const hasUserinfo = parseUrl.includes("@") && parseUrl.indexOf("@") < parseUrl.indexOf("/", parseUrl.indexOf("://") + 3) ? 1 : 0;
  let host = netloc;
  if (host.includes("@")) {
    host = host.split("@").pop() || host;
  }

  let hasPort = 0;
  if (host.includes(":") && !host.startsWith("[")) {
    const parts = host.split(":");
    host = parts[0];
    hasPort = 1;
  }

  const isIp = isIpAddress(host);
  if (!host.includes(".") && !isIp && host !== "localhost") {
    return getDefaultFeatures();
  }

  // TLD Extraction
  const parsedTld = parse(host);
  let registeredDomain = "";
  let subdomain = "";

  if (isIp || parsedTld.isIp) {
    registeredDomain = host;
    subdomain = "";
  } else {
    subdomain = parsedTld.subdomain || "";
    registeredDomain = parsedTld.domain ? parsedTld.domain.toLowerCase() : host.toLowerCase();
  }

  // Character counts
  const lenUrl = url.length;
  const lenHost = host.length;
  const lenPath = path.length;

  let digitsUrl = 0;
  for (let i = 0; i < url.length; i++) {
    if (url[i] >= "0" && url[i] <= "9") digitsUrl++;
  }

  let digitsHost = 0;
  for (let i = 0; i < host.length; i++) {
    if (host[i] >= "0" && host[i] <= "9") digitsHost++;
  }

  const segments = path.split("/").filter(Boolean);
  const nbPathSegments = segments.length;
  const nbSubdomains = subdomain ? subdomain.split(".").length : 0;

  const isShortener = KNOWN_SHORTENERS.has(registeredDomain) ? 1 : 0;
  const hasPunycode = host.includes("xn--") ? 1 : 0;

  // TLD in subdomain or path
  const subParts = new Set(subdomain ? subdomain.split(".") : []);
  let tldInSubdomain = 0;
  for (const t of COMMON_TLDS) {
    if (subParts.has(t)) {
      tldInSubdomain = 1;
      break;
    }
  }

  const pathLower = path.toLowerCase();
  let tldInPath = 0;
  for (const t of COMMON_TLDS) {
    if (pathLower.includes(`.${t}`)) {
      tldInPath = 1;
      break;
    }
  }

  const urlLower = url.toLowerCase();
  const sensitiveFeats = countSensitiveWords(urlLower);
  const brandFeats = analyzeBrandPresence(registeredDomain, subdomain, path);

  const afterScheme = url.includes("://") ? url.split("://", 2)[1] : url;
  const nbDslash = countSubstr(afterScheme, "//");

  const nbSpace = countChar(url, " ") + countSubstr(urlLower, "%20");
  const nbWww = countSubstr(urlLower, "www");
  const nbCom = countSubstr(urlLower, "com");

  return {
    length_url: lenUrl,
    length_hostname: lenHost,
    length_path: lenPath,
    nb_dots: countChar(url, "."),
    nb_hyphens: countChar(url, "-"),
    nb_at: countChar(url, "@"),
    nb_qm: countChar(url, "?"),
    nb_and: countChar(url, "&"),
    nb_or: countChar(url, "|"),
    nb_eq: countChar(url, "="),
    nb_underscore: countChar(url, "_"),
    nb_tilde: countChar(url, "~"),
    nb_percent: countChar(url, "%"),
    nb_slash: countChar(url, "/"),
    nb_colon: countChar(url, ":"),
    nb_semicolon: countChar(url, ";"),
    nb_dollar: countChar(url, "$"),
    nb_space: nbSpace,
    nb_www: nbWww,
    nb_com: nbCom,
    nb_dslash: nbDslash,
    http_in_path: pathLower.includes("http") ? 1 : 0,
    https_token: host.includes("https") ? 1 : 0,
    ratio_digits_url: Number((digitsUrl / Math.max(1, lenUrl)).toFixed(4)),
    ratio_digits_host: Number((digitsHost / Math.max(1, lenHost)).toFixed(4)),
    entropy_url: calculateEntropy(url),
    entropy_host: calculateEntropy(host),
    has_ip: isIp ? 1 : 0,
    has_https: scheme === "https" ? 1 : 0,
    has_port: hasPort,
    has_userinfo: hasUserinfo,
    nb_subdomains: nbSubdomains,
    length_subdomain: subdomain.length,
    nb_path_segments: nbPathSegments,
    has_punycode: hasPunycode,
    is_shortener: isShortener,
    length_registered_domain: registeredDomain.length,
    tld_in_subdomain: tldInSubdomain,
    tld_in_path: tldInPath,
    ...sensitiveFeats,
    ...brandFeats,
    is_malformed: 0,
  };
}

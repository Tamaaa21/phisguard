/**
 * Shannon Entropy calculation for string randomness detection.
 */
export function calculateEntropy(text: string): number {
  if (!text) return 0.0;
  const length = text.length;
  const counts: Record<string, number> = {};

  for (let i = 0; i < length; i++) {
    const ch = text[i];
    counts[ch] = (counts[ch] || 0) + 1;
  }

  let entropy = 0.0;
  for (const char in counts) {
    const p = counts[char] / length;
    entropy -= p * Math.log2(p);
  }

  return Number(entropy.toFixed(4));
}

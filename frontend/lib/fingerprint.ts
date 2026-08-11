/**
 * A lightweight, non-cryptographic fingerprint of the browser/device,
 * captured once when an assessment attempt starts (see backend Phase 11
 * notes: "fingerprint captured once at start, not continuously
 * re-validated, to avoid false positives from legitimate network
 * changes"). This is defense-in-depth, not a security boundary — a
 * motivated cheater can spoof it. It just makes casual session-sharing
 * detectable.
 */
export function fingerprintHash(): string {
  if (typeof window === "undefined") return "server";

  const raw = [
    navigator.userAgent,
    navigator.language,
    `${screen.width}x${screen.height}`,
    Intl.DateTimeFormat().resolvedOptions().timeZone,
    String(navigator.hardwareConcurrency ?? ""),
  ].join("|");

  let hash = 0;
  for (let i = 0; i < raw.length; i++) {
    hash = (hash << 5) - hash + raw.charCodeAt(i);
    hash |= 0;
  }
  return hash.toString(16);
}

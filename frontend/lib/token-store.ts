/**
 * Access tokens live in memory only — never in localStorage/sessionStorage,
 * which are readable by any injected script (XSS risk). The refresh token
 * is a separate httpOnly cookie the browser sends automatically; JS never
 * touches it. On a hard page reload, `accessToken` resets to null and the
 * app calls /auth/refresh once on boot to obtain a fresh one silently.
 */
let accessToken: string | null = null;

export function getAccessToken(): string | null {
  return accessToken;
}

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

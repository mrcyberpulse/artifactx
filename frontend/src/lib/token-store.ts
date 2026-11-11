// Access token lives in memory only, never localStorage/sessionStorage, so it cannot be
// read by an XSS payload that persists across reloads. It is lost on full page reload by
// design; AuthProvider re-establishes it via the HttpOnly refresh cookie on mount.
let accessToken: string | null = null;
type Listener = (token: string | null) => void;
const listeners = new Set<Listener>();

export function getAccessToken(): string | null {
  return accessToken;
}

export function setAccessToken(token: string | null): void {
  accessToken = token;
  listeners.forEach((listener) => listener(token));
}

export function subscribeAccessToken(listener: Listener): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

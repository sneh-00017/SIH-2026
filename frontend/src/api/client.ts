const browserHost = typeof window !== "undefined" ? window.location.hostname : "127.0.0.1";
const browserProtocol = typeof window !== "undefined" ? window.location.protocol : "http:";
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? `${browserProtocol}//${browserHost}:5000`;

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status} ${response.statusText}`);
  }
  return (await response.json()) as T;
}

export { API_BASE_URL };

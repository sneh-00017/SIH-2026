import { API_BASE_URL } from "./client";

export async function checkBackendHealth(): Promise<string> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = (await response.json()) as { message?: string; status?: string };
    return `✅ Backend connected: ${data.message ?? "OK"} (status: ${data.status ?? "unknown"})`;
  } catch (error) {
    console.error(error);
    return "❌ Backend not connected. Make sure Flask is running on port 5000.";
  }
}
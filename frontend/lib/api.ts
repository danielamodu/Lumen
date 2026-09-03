const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const DEMO_KEY = "lmn_demo0000000000000000000000000000";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function apiFetch<T = any>(
  endpoint: string, 
  body: object = {}
): Promise<T> {
  const response = await fetch(`${API_URL}${endpoint}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Lumen-Key": DEMO_KEY,
    },
    body: JSON.stringify(body),
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  
  return response.json();
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function apiGet<T = any>(endpoint: string): Promise<T> {
  const response = await fetch(`${API_URL}${endpoint}`, {
    method: "GET", 
    headers: {
      "X-Lumen-Key": DEMO_KEY,
    },
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  
  return response.json();
}

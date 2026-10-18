import { apiErrorMessage } from "./apiError";
const API_URL =
  import.meta.env.VITE_API_URL ??
  "http://127.0.0.1:8000/api/v1";

export async function apiRequest<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(
    `${API_URL}${endpoint}`,
    {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    }
  );

  if (!response.ok) {
    let message =
      `Erro HTTP ${response.status}`;

    try {
      const body = await response.json();

      if (body.detail) {
        message = apiErrorMessage(body.detail, message);
      }
    } catch {
      // Mantém mensagem HTTP padrão.
    }

    throw new Error(message);
  }

  if (response.status === 204) return undefined as T;
  return response.json();
}

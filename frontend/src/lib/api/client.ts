import type { ApiError } from "./stores/auth";

const API_BASE = import.meta.env.VITE_API_URL || "";

class APIClient {
  private async request<T>(method: string, path: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE}/api/v1${path}`, {
      method,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error: ApiError = await response.json();

      if (response.status === 401) {
        const refreshed = await this.refreshToken();
        if (refreshed) {
          return this.request<T>(method, path, options);
        }
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
        throw new Error("Session expired. Please log in again.");
      }

      if (response.status === 403) {
        throw new Error("You do not have permission to perform this action.");
      }

      throw new Error(error.detail?.message || "An unexpected error occurred");
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return response.json();
  }

  private async refreshToken(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE}/api/v1/auth/refresh`, {
        method: "POST",
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  async get<T>(path: string): Promise<T> {
    return this.request<T>("GET", path);
  }

  async post<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>("POST", path, {
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async put<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>("PUT", path, {
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async delete<T>(path: string): Promise<T> {
    return this.request<T>("DELETE", path);
  }
}

export const api = new APIClient();

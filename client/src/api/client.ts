import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL,
  withCredentials: true, // keep if your auth uses cookies
});

export function normalizeError(err: unknown): string {
  if (axios.isAxiosError(err)) {
    return (
      err.response?.data?.detail || err.response?.data?.message || err.message
    );
  }
  return "Unknown error";
}

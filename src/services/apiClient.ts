import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
export const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK_API !== "false";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});

apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("civicmind_auth_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Helper for simulated delay in mock responses
export const mockDelay = <T>(data: T, ms = 200): Promise<T> => {
  return new Promise((resolve) => setTimeout(() => resolve(data), ms));
};

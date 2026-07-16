import axios from "axios";

function extractErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;

    if (typeof detail === "string") {
      return detail;
    }
    if (Array.isArray(detail)) {
      return detail
        .map((d) => (typeof d === "string" ? d : (d.msg ?? JSON.stringify(d))))
        .join("; ");
    }
    if (detail && typeof detail === "object") {
      return detail.message ?? JSON.stringify(detail);
    }
    return detail.message ?? JSON.stringify(detail);
  }
  return "Unexpected Error";
}

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000",
  timeout: 30000,
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    return Promise.reject(new Error(extractErrorMessage(error)));
  },
);

export default apiClient;

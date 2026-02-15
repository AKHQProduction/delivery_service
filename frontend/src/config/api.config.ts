import axios from "axios";
import { detectPlatform } from "../platforms/detect";
import { createWebPlatform } from "../platforms/web/WebPlatform";
import { createTelegramPlatform } from "../platforms/telegram/TelegramPlatform";

const baseURL = import.meta.env.VITE_API_URL;

const platformType = detectPlatform();
const platform =
  platformType === "telegram" ? createTelegramPlatform() : createWebPlatform();

const api = axios.create({
  baseURL: baseURL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

// Request interceptor: delegate auth headers to platform adapter
api.interceptors.request.use((config) => {
  const headers = platform.auth.getHeaders();
  Object.assign(config.headers, headers);
  return config;
});

// Response interceptor for error handling
let errorHandler: ((message: string, details?: string) => void) | null = null;

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      const data = error.response.data;

      //TODO:
      //MOVE THIS TO A SEPARATE FILE WITH ALL EXEPTIONS
      if (error.response.status === 409 && data?.code === "duplicate_phones") {
        return Promise.reject(error);
      }

      // Session expired — delegate to platform adapter
      if (error.response.status === 401) {
        platform.auth.onUnauthorized();
        return Promise.reject(error);
      }
      // Extract error message from backend response
      // Adjust these fields based on your backend's error response structure
      const errorMessage =
        data?.error || // Common field
        data?.message || // Common field
        data?.msg || // Common field
        data?.detail || // FastAPI/Django style
        data?.error_message || // Custom field
        `Error ${error.response.status}`;

      // Extract additional details if available
      const errorDetails =
        data?.details ||
        data?.description ||
        data?.error_description ||
        (typeof data === "string" ? data : undefined);

      // Call the error handler if it's set
      if (errorHandler) {
        errorHandler(errorMessage, errorDetails);
      }

      console.error("API Error:", {
        status: error.response.status,
        message: errorMessage,
        details: errorDetails,
        fullError: error.response.data,
      });
    } else if (error.request) {
      // Request made but no response received
      if (errorHandler) {
        errorHandler(
          "Network Error",
          "Unable to connect to the server. Check your internet connection.",
        );
      }
    } else {
      // Something else happened
      if (errorHandler) {
        errorHandler("Error", error.message);
      }
    }

    return Promise.reject(error);
  },
);

// Function to set the error handler
export const setApiErrorHandler = (handler: (message: string, details?: string) => void) => {
  errorHandler = handler;
};

export default api;

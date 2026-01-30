import axios from "axios";
import initDataTG from "../services/tgInitData";

const baseURL = import.meta.env.VITE_API_URL;
const userID = JSON.parse(localStorage.getItem("userID") || "{}");

const api = axios.create({
  baseURL: baseURL,
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${initDataTG?.initData || userID}`,
  },
});

// Request interceptor
api.interceptors.request.use((config) => {
  if (initDataTG?.initData) {
    config.headers.Authorization = `Bearer ${initDataTG.initData}`;
  }
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
      
      // Extract error message from backend response
      // Adjust these fields based on your backend's error response structure
      const errorMessage = 
        data?.error ||           // Common field
        data?.message ||         // Common field
        data?.msg ||             // Common field
        data?.detail ||          // FastAPI/Django style
        data?.error_message ||   // Custom field
        `Error ${error.response.status}`;
      
      // Extract additional details if available
      const errorDetails = 
        data?.details ||
        data?.description ||
        data?.error_description ||
        (typeof data === 'string' ? data : undefined);

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
          "Unable to connect to the server. Check your internet connection."
        );
      }
    } else {
      // Something else happened
      if (errorHandler) {
        errorHandler("Error", error.message);
      }
    }

    return Promise.reject(error);
  }
);

// Function to set the error handler
export const setApiErrorHandler = (handler: (message: string, details?: string) => void) => {
  errorHandler = handler;
};

export default api;
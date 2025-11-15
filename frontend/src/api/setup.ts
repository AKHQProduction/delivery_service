import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL;
const userID = JSON.parse(localStorage.getItem("userID") || "{}");

const api = axios.create({
  baseURL: baseURL,
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${userID}`,
  },
});

api.interceptors.request.use((config) => {
  const userID = JSON.parse(localStorage.getItem("userID") || "{}");
  if (userID) {
    config.headers.Authorization = `Bearer ${userID}`;
  }
  return config;
});

export default api;

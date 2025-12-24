import axios from "axios";
import initDataTG from "../services/tgInitData";

const baseURL = import.meta.env.VITE_API_URL;
const userID = JSON.parse(localStorage.getItem("userID") || "{}");

const api = axios.create({
  baseURL: baseURL,
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${
      initDataTG ? JSON.stringify(initDataTG.initDataUnsafe) : userID
    }`,
  },
});

api.interceptors.request.use((config) => {
  if (initDataTG) {
    config.headers.Authorization = `Bearer ${
      initDataTG ? JSON.stringify(initDataTG.initDataUnsafe) : userID
    }`;
  }
  return config;
});

export default api;

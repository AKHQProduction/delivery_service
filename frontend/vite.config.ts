import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
      allowedHosts: true,
      watch: {
        usePolling: true,
      },
      host: true,
      strictPort: true,
      port: 5173,
      hmr: {
        overlay: false,
        protocol: "wss",
        clientPort: 443,
      },
    },
});

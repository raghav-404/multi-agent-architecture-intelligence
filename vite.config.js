import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const apiRoutes = ["/me", "/login", "/register", "/logout", "/analyze", "/refine", "/impact", "/scenario", "/history", "/pdf"];
const proxy = Object.fromEntries(apiRoutes.map(path => [path, "http://127.0.0.1:8000"]));

export default defineConfig({
  root: "frontend",
  base: "/static/",
  plugins: [react()],
  server: { port: 5173, proxy },
  build: {
    outDir: "../static",
    emptyOutDir: true,
    assetsDir: "assets"
  }
});

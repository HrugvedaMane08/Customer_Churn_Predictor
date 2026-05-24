import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  output: "standalone",
  typescript: {
    ignoreBuildErrors: true,
  },
  async rewrites() {
    const isDev = process.env.NODE_ENV === "development";
    const defaultBackend = isDev ? "http://127.0.0.1:8000" : "https://customer-churn-predictor-3p9a.onrender.com";
    const backendUrl = process.env.BACKEND_API_URL || defaultBackend;
    // Sanitize backend URL by removing any trailing /api/v1 or slashes added by mistake
    const cleanBackendUrl = backendUrl.replace(/\/api\/v1\/?$/, "").replace(/\/$/, "");
    return [
      {
        source: "/api/v1/:path*",
        destination: `${cleanBackendUrl}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;

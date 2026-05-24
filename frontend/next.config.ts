import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  output: "standalone",
  typescript: {
    ignoreBuildErrors: true,
  },
  async rewrites() {
    const backendUrl = process.env.BACKEND_API_URL || "http://127.0.0.1:8000";
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

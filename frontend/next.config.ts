import type { NextConfig } from "next";

const siteHost = (process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000")
  .replace(/^https?:\/\//, "")
  .replace(/\/$/, "");

const productionHosts = ["ekontaktor.ru", "www.ekontaktor.ru"];

/** Browser-visible backend URL (admin login page) */
const backendPublic = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1").replace(
  /\/api\/v1\/?$/,
  "",
);

const nextConfig: NextConfig = {
  skipTrailingSlashRedirect: true,
  async redirects() {
    return [
      {
        source: "/manage",
        destination: `${backendPublic}/manage/`,
        permanent: false,
        basePath: false,
      },
      {
        source: "/manage/:path*",
        destination: `${backendPublic}/manage/:path*`,
        permanent: false,
        basePath: false,
      },
    ];
  },
  images: {
    formats: ["image/avif", "image/webp"],
    remotePatterns: [
      { protocol: "http", hostname: "localhost", port: "8000" },
      { protocol: "http", hostname: "127.0.0.1", port: "8000" },
      { protocol: "http", hostname: "backend", port: "8000" },
      { protocol: "https", hostname: siteHost.split(":")[0] },
      ...productionHosts.map((hostname) => ({ protocol: "https" as const, hostname })),
    ],
  },
};

export default nextConfig;

/** @type {import('next').NextConfig} */
const nextConfig = {
  generateBuildId: async () => String(Date.now()),
  async rewrites() {
    return [
      {
        source: "/app",
        destination: "/live",
      },
    ];
  },
};

export default nextConfig;

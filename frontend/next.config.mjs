/** @type {import('next').NextConfig} */
const nextConfig = {
  generateBuildId: async () => String(Date.now()),
};

export default nextConfig;

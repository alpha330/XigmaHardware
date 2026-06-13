/** @type {import('next').NextConfig} */
const nextConfig = {
    images: {
      remotePatterns: [
        {
          protocol: 'https',
          hostname: '**.xigmahardware.com', // دامنه بک‌اند
        },
        {
          protocol: 'http',
          hostname: 'localhost',
        },
      ],
    },
    compiler: {
      emotion: true, // فعال‌سازی Emotion
    },
    allowedDevOrigins: ['127.0.0.1'],
    env: {
      API_BASE_URL: process.env.API_BASE_URL || 'http://localhost:8000/api/v1',
    },
  };

  export default nextConfig;
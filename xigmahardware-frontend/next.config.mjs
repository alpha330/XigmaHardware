/** @type {import('next').NextConfig} */
const nextConfig = {
  /* config options here */
  compiler: {
    emotion: true,  // فعال کردن Emotion
  },
  allowedDevOrigins: ['127.0.0.1'],
};

export default nextConfig;

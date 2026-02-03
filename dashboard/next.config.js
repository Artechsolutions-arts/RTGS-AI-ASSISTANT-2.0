/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_N8N_BASE_URL: process.env.NEXT_PUBLIC_N8N_BASE_URL || 'http://localhost:5678/webhook',
    NEXT_PUBLIC_GOOGLE_MAPS_API_KEY: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || '',
  },
}

module.exports = nextConfig

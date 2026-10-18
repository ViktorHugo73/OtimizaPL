import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Used only by standalone Vite development; Vercel owns deployed routing.
      '/api': { target: process.env.LOCAL_API_URL ?? 'http://127.0.0.1:8000', changeOrigin: true },
    },
  },
})

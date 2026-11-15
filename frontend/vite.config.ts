import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// In development, /api is proxied to the FastAPI server, so the frontend needs no CORS setup.
// In production, set VITE_API_URL to the deployed backend (see .env.example).
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { '/api': 'http://127.0.0.1:8000' },
  },
})

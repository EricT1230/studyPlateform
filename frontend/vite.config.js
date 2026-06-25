import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // listen on 0.0.0.0 so the dev server is reachable from outside the container
    // Docker Desktop on Windows/macOS does not forward inotify events across
    // bind mounts, so file-watch HMR needs polling. Enabled only in the dev
    // container (VITE_USE_POLLING=1) to avoid burning CPU on native dev.
    watch: process.env.VITE_USE_POLLING ? { usePolling: true } : undefined,
  },
})

import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

// API target: use environment variable or default to localhost
const API_TARGET = process.env.API_TARGET || 'http://127.0.0.1:8000';

export default defineConfig({
  plugins: [svelte()],
  server: {
    host: '0.0.0.0',  // Allow external access
    port: 5173,
    proxy: {
      '/api': {
        target: API_TARGET,
        changeOrigin: true,
      },
      '/collector': {
        target: API_TARGET,
        changeOrigin: true,
      },
      '/recipes': {
        target: API_TARGET,
        changeOrigin: true,
      },
      '/health': {
        target: API_TARGET,
        changeOrigin: true,
      },
    },
  },
});

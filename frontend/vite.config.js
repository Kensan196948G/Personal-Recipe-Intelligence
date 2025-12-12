import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  plugins: [svelte()],
  server: {
    host: '0.0.0.0',  // Allow external access
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://192.168.0.187:8000',
        changeOrigin: true,
      },
      '/collector': {
        target: 'http://192.168.0.187:8000',
        changeOrigin: true,
      },
      '/recipes': {
        target: 'http://192.168.0.187:8000',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://192.168.0.187:8000',
        changeOrigin: true,
      },
    },
  },
});

import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  plugins: [svelte()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://192.168.0.29:8000',
        changeOrigin: true,
      },
      '/collector': {
        target: 'http://192.168.0.29:8000',
        changeOrigin: true,
      },
      '/recipes': {
        target: 'http://192.168.0.29:8000',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://192.168.0.29:8000',
        changeOrigin: true,
      },
    },
  },
});

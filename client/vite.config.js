import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  // Set API_URL in client/.env.local when the API isn't on port 5000.
  const api = loadEnv(mode, process.cwd(), '').API_URL || 'http://localhost:5000';
  return {
    plugins: [react()],
    server: {
      proxy: {
        '/api': api,
        '/media': api,
      },
    },
  };
});

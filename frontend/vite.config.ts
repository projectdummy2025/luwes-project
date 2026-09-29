import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

// Vite configuration for React TypeScript frontend communicating with backend
export default defineConfig(({ mode }) => {
  // Load root environment variables from central .env file
  const rootEnv = loadEnv(mode, resolve(import.meta.dirname, '..'), '');
  const frontendHost = rootEnv.FRONTEND_HOST || '0.0.0.0';
  const frontendPort = parseInt(rootEnv.FRONTEND_PORT || '8085', 10);
  const backendHost = rootEnv.BACKEND_HOST || '127.0.0.1';
  const backendPort = rootEnv.BACKEND_PORT || '8035';

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
      },
    },
    server: {
      host: frontendHost,
      port: frontendPort,
      proxy: {
        '/api': {
          target: `http://${backendHost}:${backendPort}`,
          changeOrigin: true,
        },
      },
    },
  };
});

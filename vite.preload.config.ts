import { defineConfig } from 'vite';
import { resolve } from 'path';

console.info('dir', __dirname);

// https://vitejs.dev/config
export default defineConfig({
  base: './',
  resolve: {
    alias: {
      '@images': resolve(__dirname, './src/assets/images'),
      '@': resolve(__dirname, './src'),
      '@actions': resolve(__dirname, './actions'),
    },
  },
});

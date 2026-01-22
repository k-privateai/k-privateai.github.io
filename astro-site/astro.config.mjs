// @ts-check
import { defineConfig } from 'astro/config';

import react from '@astrojs/react';
import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  site: 'https://k-privateai.github.io',
  integrations: [react()],
  build: {
    format: 'directory', // /foo/ -> /foo/index.html
  },
  trailingSlash: 'always', // enforce /foo/
  markdown: {
    shikiConfig: {
      theme: 'github-dark',
    },
  },
  vite: {
    plugins: [tailwindcss()]
  }
});
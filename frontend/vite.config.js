import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/relatorios': 'http://localhost:5000',
      '/video':      'http://localhost:5000',
      '/baias':      'http://localhost:5000',
      '/animais':    'http://localhost:5000',
      '/usuarios':   'http://localhost:5000',
      '/alertas':    'http://localhost:5000',
      '/analisar': {
        target: 'http://localhost:5000',
        timeout: 300000,
        proxyTimeout: 300000,
      },
    },
  },
})

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  // 设置基础路径为 /watch-agent/
  base: '/watch-agent/',
  
  plugins: [
    react({
      // 使用Fast Refresh，提供更好的HMR体验
      fastRefresh: true,
    })
  ],
  server: {
    port: 10031,
    host: '0.0.0.0',
    
    // 简化 HMR 配置，避免端口冲突
    hmr: {
      overlay: true,
    },
    
    // 文件监听配置
    watch: {
      ignored: [
        '**/node_modules/**',
        '**/dist/**',
        '**/.git/**',
        '**/storage/**',
        '**/logs/**',
      ],
      usePolling: true,
      interval: 1000,
    },
    
    proxy: {
      '/api': {
        target: 'http://10.11.17.19:10030',
        changeOrigin: true,
      },
    },
  },
  
  // 优化配置
  optimizeDeps: {
    // 预构建依赖，提高加载速度
    include: [
      'react',
      'react-dom',
      'zustand',
      'axios',
      'lucide-react',
    ],
  },
  
  // 构建配置
  build: {
    // 增加警告阈值
    chunkSizeWarningLimit: 1000,
  },
})


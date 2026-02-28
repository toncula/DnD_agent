import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import tailwindcss from '@tailwindcss/vite'; // 这里必须引用 Tailwind v4 的插件
import path from 'path';

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(), // 激活 Tailwind 处理
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    host: '0.0.0.0',
    watch: {
      // 继续保持对数据目录的忽略，防止后端保存触发全页刷新
      ignored: ['**/data/**', '**/chroma_db_data/**', '**/__pycache__/**'],
    },
  },
});

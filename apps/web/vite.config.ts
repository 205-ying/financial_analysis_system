import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import UnoCSS from 'unocss/vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    UnoCSS(),
    AutoImport({
      imports: [
        'vue',
        'vue-router',
        'pinia',
        '@vueuse/core'
      ],
      presets: ['element-plus'],
      resolvers: [ElementPlusResolver()],
      dts: true,
      eslintrc: {
        enabled: true
      }
    }),
    Components({
      resolvers: [ElementPlusResolver({ importStyle: false })], // 禁用自动导入样式
      dts: true
    })
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `
          @use "@/styles/variables/colors" as *;
          @use "@/styles/variables/typography" as *;
          @use "@/styles/variables/spacing" as *;
          @use "@/styles/variables/shadows" as *;
          @use "@/styles/variables/borders" as *;
          @use "@/styles/variables/animations" as *;
        `,
        silenceDeprecations: ['legacy-js-api'] // 抑制弃用警告
      }
    }
  },
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    target: 'es2020',
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    chunkSizeWarningLimit: 1000, // 增大警告限制
    rollupOptions: {
      output: {
        manualChunks: {
          // Element Plus - 保持单独一个 chunk
          'element-plus': ['element-plus'],
          // Element Plus Icons
          'element-icons': ['@element-plus/icons-vue'],
          // Vue 核心库
          'vue-vendor': ['vue', 'vue-router', 'pinia', '@vueuse/core'],
          // ECharts 核心库
          'echarts-core': ['echarts/core'],
          // ECharts 图表类型
          'echarts-charts': ['echarts/charts'],
          // ECharts 组件
          'echarts-components': ['echarts/components'],
          // ECharts 渲染器
          'echarts-renderer': ['echarts/renderers'],
          // DayJS 日期处理
          'dayjs': ['dayjs'],
          // Element Plus 样式按需引入 (通过 unplugin-vue-components)
        },
        // 优化长文件名
        entryFileNames: 'assets/[name].[hash].js',
        chunkFileNames: 'assets/[name].[hash].js',
        assetFileNames: 'assets/[name].[ext]'
      }
    }
  }
})
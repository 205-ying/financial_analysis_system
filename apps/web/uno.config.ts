import { defineConfig, presetAttributify, presetUno } from 'unocss'

export default defineConfig({
  presets: [
    presetUno(),
    presetAttributify()
  ],
  theme: {
    colors: {
      primary: '#4338CA', // 主色 Indigo
      indigo: {
        500: '#6366f1',
        600: '#4f46e5',
        700: '#4338CA',
      },
      bg: '#F8FAFC',
      surface: '#FFFFFF'
    }
  },
  shortcuts: {
    'text-indigo': 'text-indigo-700',
    'bg-main': 'bg-bg',
    'bg-surface': 'bg-surface'
  }
})

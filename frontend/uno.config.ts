import { defineConfig, presetAttributify, presetUno, presetIcons } from 'unocss'

export default defineConfig({
  presets: [
    presetUno(),
    presetAttributify(),
    presetIcons({
      scale: 1.2,
      warn: true
    })
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

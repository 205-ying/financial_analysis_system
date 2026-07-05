/**
 * ECharts Hook
 */
import { ref, onMounted, onBeforeUnmount, Ref } from 'vue'
import * as echarts from 'echarts/core'
import { getCurrentEChartsTheme } from '@/config/echarts-theme'
import {
  BarChart,
  LineChart,
  PieChart,
  GaugeChart,
  type BarSeriesOption,
  type LineSeriesOption,
  type PieSeriesOption,
  type GaugeSeriesOption
} from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  DataZoomComponent,
  GraphicComponent,
  MarkPointComponent,
  type TitleComponentOption,
  type TooltipComponentOption,
  type GridComponentOption,
  type LegendComponentOption,
  type DataZoomComponentOption,
  type GraphicComponentOption
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { ComposeOption } from 'echarts/core'

// 注册必须的组件
echarts.use([
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  DataZoomComponent,
  GraphicComponent,
  MarkPointComponent,
  BarChart,
  LineChart,
  PieChart,
  GaugeChart,
  CanvasRenderer
])

export type ECOption = ComposeOption<
  | BarSeriesOption
  | LineSeriesOption
  | PieSeriesOption
  | GaugeSeriesOption
  | TitleComponentOption
  | TooltipComponentOption
  | GridComponentOption
  | LegendComponentOption
  | DataZoomComponentOption
  | GraphicComponentOption
>

/**
 * 使用 ECharts
 */
export function useECharts(chartRef: Ref<HTMLElement | null>) {
  let chartInstance: echarts.ECharts | null = null
  const loading = ref(false)

  /**
   * 初始化图表
   */
  const initChart = () => {
    if (!chartRef.value) return

    const theme = getCurrentEChartsTheme()
    chartInstance = echarts.init(chartRef.value, theme)

    // 监听窗口大小变化
    window.addEventListener('resize', handleResize)
  }

  /**
   * 设置图表配置 (自动注入财务驾驶舱默认配置)
   */
  const setOption = (option: ECOption, notMerge = false) => {
    if (!chartInstance) {
      initChart()
    }

    const FINANCE_COLORS = ['#C81E1E', '#D19A36', '#2F8F5B', '#D98F20', '#405D65', '#8B5E34']

    // 经营报表全局基础配置
    const baseOption: ECOption = {
      color: FINANCE_COLORS,
      grid: {
        top: 60,
        right: 20,
        bottom: 20,
        left: 20,
        containLabel: true,
        show: false,
      },
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(255, 253, 249, 0.96)',
        borderColor: '#E4DED5',
        borderWidth: 1,
        padding: [12, 16],
        textStyle: {
          color: '#332D28',
          fontSize: 13,
          fontFamily: '"Aptos", "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif',
        },
        extraCssText: 'box-shadow: 0 10px 28px rgba(51, 45, 40, 0.12); border-radius: 6px;',
        axisPointer: {
          type: 'line',
          lineStyle: {
            color: '#D2C9BD',
            width: 1,
            type: 'dashed'
          }
        },
      },
      xAxis: {
        type: 'category',
        axisLine: {
          show: true,
          lineStyle: { color: '#E4DED5', width: 1 }
        },
        axisTick: { show: false },
        axisLabel: {
          color: '#756D64',
          margin: 16,
          fontFamily: '"Aptos", "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif'
        },
        splitLine: { show: false }
      },
      yAxis: {
        type: 'value',
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: {
          color: '#756D64',
          margin: 16,
          fontFamily: '"Aptos", "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif'
        },
        splitLine: {
          show: true,
          lineStyle: {
            color: '#E4DED5',
            type: 'dashed',
            opacity: 0.72
          }
        }
      }
    }

    // 自动为折线图注入平滑与渐变属性
    const injectedOption = { ...option }
    
    if (Array.isArray(injectedOption.series)) {
      injectedOption.series = injectedOption.series.map((s: any, index: number) => {
        if (s.type === 'line') {
          return {
            ...s,
            smooth: s.smooth !== undefined ? s.smooth : true,
            showSymbol: s.showSymbol !== undefined ? s.showSymbol : false, // 默认隐藏节点，hover时才显示
            lineStyle: {
              width: 3,
              ...s.lineStyle
            },
            areaStyle: s.areaStyle || {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: (s.itemStyle?.color || FINANCE_COLORS[index % FINANCE_COLORS.length]) + '33' },
                { offset: 1, color: (s.itemStyle?.color || FINANCE_COLORS[index % FINANCE_COLORS.length]) + '00' }
              ])
            }
          }
        }
        return s
      }) as any
    }

    // 利用 setOption 的特性自动浅层/深层覆盖混合
    chartInstance?.setOption(baseOption, false)
    chartInstance?.setOption(injectedOption, notMerge)
  }

  /**
   * 显示加载动画
   */
  const showLoading = () => {
    loading.value = true
    chartInstance?.showLoading('default', {
      text: '加载中...',
      color: 'var(--color-primary)',
      textColor: 'var(--color-text-primary)',
      maskColor: 'rgba(var(--color-bg-primary), 0.8)',
      zlevel: 0
    })
  }

  /**
   * 隐藏加载动画
   */
  const hideLoading = () => {
    loading.value = false
    chartInstance?.hideLoading()
  }

  /**
   * 调整图表大小
   */
  const handleResize = () => {
    chartInstance?.resize()
  }

  /**
   * 销毁图表
   */
  const dispose = () => {
    window.removeEventListener('resize', handleResize)
    chartInstance?.dispose()
    chartInstance = null
  }

  onMounted(() => {
    initChart()
  })

  onBeforeUnmount(() => {
    dispose()
  })

  return {
    chartInstance,
    loading,
    setOption,
    showLoading,
    hideLoading,
    handleResize,
    dispose
  }
}

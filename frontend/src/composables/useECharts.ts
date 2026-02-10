/**
 * ECharts Hook
 */
import { ref, onMounted, onBeforeUnmount, Ref } from 'vue'
import * as echarts from 'echarts/core'
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
  type TitleComponentOption,
  type TooltipComponentOption,
  type GridComponentOption,
  type LegendComponentOption,
  type DataZoomComponentOption
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

    chartInstance = echarts.init(chartRef.value)

    // 监听窗口大小变化
    window.addEventListener('resize', handleResize)
  }

  /**
   * 设置图表配置
   */
  const setOption = (option: ECOption, notMerge = false) => {
    if (!chartInstance) {
      initChart()
    }
    chartInstance?.setOption(option, notMerge)
  }

  /**
   * 显示加载动画
   */
  const showLoading = () => {
    loading.value = true
    chartInstance?.showLoading('default', {
      text: '加载中...',
      color: '#409eff',
      textColor: '#000',
      maskColor: 'rgba(255, 255, 255, 0.8)',
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

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
   * 设置图表配置 (自动注入 V2 净化版默认配置)
   */
  const setOption = (option: ECOption, notMerge = false) => {
    if (!chartInstance) {
      initChart()
    }

    // 莫兰迪低饱和色系
    const V2_COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#14b8a6', '#f59e0b', '#84cc16'];

    // 净化版全局基础配置
    const baseOption: ECOption = {
      color: V2_COLORS,
      grid: {
        top: 60,
        right: 20,
        bottom: 20,
        left: 20,
        containLabel: true,
        show: false, // 彻底关闭物理边框
      },
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(255, 255, 255, 0.7)',
        borderColor: 'rgba(255, 255, 255, 0.4)',
        borderWidth: 1,
        padding: [12, 16],
        textStyle: {
          color: '#0F172A',
          fontSize: 13,
          fontFamily: 'Inter, sans-serif',
        },
        extraCssText: 'box-shadow: 0 8px 32px rgba(67, 56, 202, 0.08); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border-radius: 8px;',
        axisPointer: {
          type: 'line',
          lineStyle: {
            color: '#CBD5E1',
            width: 1,
            type: 'dashed'
          }
        },
      },
      xAxis: {
        type: 'category',
        axisLine: {
          show: true,
          lineStyle: { color: '#E2E8F0', width: 1 } // 极淡的轴线
        },
        axisTick: { show: false }, // 去掉刻度
        axisLabel: {
          color: '#64748B',
          margin: 16,
          fontFamily: 'Inter, sans-serif'
        },
        splitLine: { show: false } // 去掉垂直网格线
      },
      yAxis: {
        type: 'value',
        axisLine: { show: false }, // Y轴线隐藏
        axisTick: { show: false }, // 去除刻度
        axisLabel: {
          color: '#64748B',
          margin: 16,
          fontFamily: 'Inter, sans-serif'
        },
        splitLine: {
          show: true,
          lineStyle: {
            color: '#CBD5E1',
            type: 'dashed',
            opacity: 0.3 // 非常微弱的水平虚线
          }
        }
      }
    };

    // 自动为折线图注入平滑与渐变属性
    const injectedOption = { ...option };
    
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
                { offset: 0, color: (s.itemStyle?.color || V2_COLORS[index % V2_COLORS.length]) + '4D' }, // 30% 透明度 (HEX 4D)
                { offset: 1, color: (s.itemStyle?.color || V2_COLORS[index % V2_COLORS.length]) + '00' }  // 0% 透明度 (HEX 00)
              ])
            }
          };
        }
        return s;
      }) as any;
    }

    // 利用 setOption 的特性自动浅层/深层覆盖混合
    chartInstance?.setOption(baseOption, false);
    chartInstance?.setOption(injectedOption, notMerge);
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

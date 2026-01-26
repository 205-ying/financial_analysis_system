/**
 * 饼图/环形图组件
 * 用于占比展示（费用结构、成本结构等）
 */
<template>
  <div :id="chartId" :style="{ width: '100%', height: height }"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'

interface PieDataItem {
  name: string
  value: number
}

interface Props {
  chartId?: string
  height?: string
  data: PieDataItem[]
  title?: string
  isDonut?: boolean           // 是否为环形图
  showLabel?: boolean         // 是否显示标签
}

const props = withDefaults(defineProps<Props>(), {
  chartId: () => `pie-chart-${Math.random().toString(36).slice(2)}`,
  height: '400px',
  isDonut: false,
  showLabel: true
})

let chartInstance: ECharts | null = null

const initChart = () => {
  const dom = document.getElementById(props.chartId)
  if (!dom) return

  chartInstance = echarts.init(dom)

  const option: echarts.EChartsOption = {
    title: props.title ? {
      text: props.title,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    } : undefined,
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      type: 'scroll',
      pageIconSize: 12,
      itemGap: 10
    },
    series: [
      {
        name: '占比',
        type: 'pie',
        radius: props.isDonut ? ['40%', '70%'] : '70%',
        center: ['35%', '50%'],
        data: props.data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        label: {
          show: props.showLabel,
          formatter: '{b}: {d}%'
        },
        labelLine: {
          show: props.showLabel
        }
      }
    ]
  }

  chartInstance.setOption(option)
}

// 响应式调整
const handleResize = () => {
  chartInstance?.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})

// 监听数据变化重新渲染
watch(
  () => [props.data, props.isDonut],
  () => {
    if (chartInstance) {
      chartInstance.dispose()
      initChart()
    }
  },
  { deep: true }
)
</script>

<style scoped>
/* 图表容器样式 */
</style>

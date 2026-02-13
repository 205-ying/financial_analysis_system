/**
 * 柱状图组件
 * 用于对比展示（门店对比、月度对比等）
 */
<template>
  <div :id="chartId" :style="{ width: '100%', height: height }"></div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'

interface Props {
  chartId?: string
  height?: string
  xAxisData: string[]         // X轴数据（门店名、月份等）
  series: {
    name: string
    data: number[]
    color?: string
  }[]
  title?: string
  yAxisName?: string
  horizontal?: boolean         // 是否横向柱状图
}

const props = withDefaults(defineProps<Props>(), {
  chartId: () => `bar-chart-${Math.random().toString(36).slice(2)}`,
  height: '400px',
  horizontal: false,
  title: '',
  yAxisName: ''
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
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: props.series.map(s => s.name),
      top: props.title ? 40 : 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: props.title ? 80 : 50,
      containLabel: true
    },
    xAxis: props.horizontal ? {
      type: 'value',
      axisLabel: {
        formatter: (value: number) => {
          if (value >= 10000) {
            return (value / 10000).toFixed(1) + 'w'
          }
          return value.toFixed(0)
        }
      }
    } : {
      type: 'category',
      data: props.xAxisData,
      axisLabel: {
        rotate: props.xAxisData.length > 10 ? 45 : 0,
        interval: 0
      }
    },
    yAxis: props.horizontal ? {
      type: 'category',
      data: props.xAxisData,
      inverse: true
    } : {
      type: 'value',
      name: props.yAxisName,
      axisLabel: {
        formatter: (value: number) => {
          if (value >= 10000) {
            return (value / 10000).toFixed(1) + 'w'
          }
          return value.toFixed(0)
        }
      }
    },
    series: props.series.map(s => ({
      name: s.name,
      type: 'bar',
      data: s.data,
      itemStyle: {
        color: s.color || undefined
      },
      emphasis: {
        focus: 'series'
      },
      barMaxWidth: 60
    }))
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
  () => [props.xAxisData, props.series, props.horizontal],
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

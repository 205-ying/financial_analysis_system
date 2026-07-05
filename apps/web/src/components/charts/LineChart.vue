/**
 * 折线图组件
 * 用于趋势展示（营收趋势、利润趋势等）
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
  xAxisData: string[]         // X轴数据（日期等）
  series: {
    name: string
    data: number[]
    color?: string
  }[]
  title?: string
  yAxisName?: string
}

const props = withDefaults(defineProps<Props>(), {
  chartId: () => `line-chart-${Math.random().toString(36).slice(2)}`,
  height: '400px',
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
        type: 'cross'
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
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: props.xAxisData,
      axisLabel: {
        rotate: props.xAxisData.length > 15 ? 45 : 0
      }
    },
    yAxis: {
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
      type: 'line',
      smooth: true,
      data: s.data,
      itemStyle: {
        color: s.color
      },
      lineStyle: {
        width: 2
      },
      emphasis: {
        focus: 'series'
      }
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
  () => [props.xAxisData, props.series],
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

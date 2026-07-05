/**
 * ECharts 主题配置
 * 使用财务分析系统设计颜色
 */

import * as echarts from 'echarts/core'
import { COLORS, CHART_PALETTE } from '@/utils/colors'

// 财务分析系统ECharts主题
export const ECHARTS_THEME_FINANCIAL = {
  // 颜色配置
  color: CHART_PALETTE.CATEGORY,

  // 背景色
  backgroundColor: 'transparent',

  // 文本样式
  textStyle: {
    color: COLORS.TEXT_PRIMARY,
    fontFamily: '"Aptos", "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif',
    fontSize: 12,
  },

  // 标题
  title: {
    textStyle: {
      color: COLORS.TEXT_PRIMARY,
      fontWeight: 'bold',
      fontSize: 16,
    },
    subtextStyle: {
      color: COLORS.TEXT_SECONDARY,
      fontSize: 14,
    },
    padding: [10, 0, 10, 0],
  },

  // 图例
  legend: {
    textStyle: {
      color: COLORS.TEXT_SECONDARY,
      fontSize: 12,
    },
    pageTextStyle: {
      color: COLORS.TEXT_TERTIARY,
    },
    pageIconColor: COLORS.PRIMARY,
    pageIconInactiveColor: COLORS.GRAY_400,
  },

  // 提示框
  tooltip: {
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderColor: COLORS.GRAY_200,
    borderWidth: 1,
    textStyle: {
      color: COLORS.TEXT_PRIMARY,
      fontSize: 12,
    },
    axisPointer: {
      lineStyle: {
        color: COLORS.PRIMARY,
        width: 1,
        type: 'dashed',
      },
      crossStyle: {
        color: COLORS.PRIMARY,
        width: 1,
      },
      shadowStyle: {
        color: 'rgba(150, 150, 150, 0.1)',
      },
    },
  },

  // 网格
  grid: {
    borderColor: COLORS.GRAY_200,
    backgroundColor: 'transparent',
  },

  // 坐标轴
  axisLine: {
    lineStyle: {
      color: COLORS.GRAY_300,
      width: 1,
    },
  },
  axisTick: {
    lineStyle: {
      color: COLORS.GRAY_300,
      width: 1,
    },
  },
  axisLabel: {
    textStyle: {
      color: COLORS.TEXT_SECONDARY,
      fontSize: 11,
    },
  },
  splitLine: {
    lineStyle: {
      color: COLORS.GRAY_100,
      width: 1,
      type: 'dashed',
    },
  },

  // 区域缩放
  dataZoom: {
    backgroundColor: 'rgba(255, 255, 255, 0.8)',
    dataBackgroundColor: COLORS.GRAY_100,
    fillerColor: 'rgba(200, 30, 30, 0.1)',
    handleColor: COLORS.PRIMARY,
    handleSize: '100%',
    textStyle: {
      color: COLORS.TEXT_SECONDARY,
    },
  },

  // 视觉映射
  visualMap: {
    textStyle: {
      color: COLORS.TEXT_SECONDARY,
    },
  },

  // 时间轴
  timeline: {
    lineStyle: {
      color: COLORS.GRAY_300,
    },
    itemStyle: {
      color: COLORS.GRAY_400,
    },
    label: {
      color: COLORS.TEXT_SECONDARY,
    },
    controlStyle: {
      color: COLORS.GRAY_400,
      borderColor: COLORS.GRAY_400,
    },
  },

  // 标记点
  markPoint: {
    label: {
      color: COLORS.TEXT_INVERSE,
    },
  },

  // 标记线
  markLine: {
    label: {
      color: COLORS.TEXT_SECONDARY,
    },
    lineStyle: {
      color: COLORS.PRIMARY,
      type: 'dashed',
    },
  },

  // 标记区域
  markArea: {
    label: {
      color: COLORS.TEXT_SECONDARY,
    },
  },

  // 系列通用样式
  series: {
    // 折线图
    line: {
      symbolSize: 6,
      lineStyle: {
        width: 2,
      },
      itemStyle: {
        borderWidth: 1,
      },
      areaStyle: {
        opacity: 0.1,
      },
    },

    // 柱状图
    bar: {
      barWidth: '60%',
      itemStyle: {
        barBorderRadius: [2, 2, 0, 0],
      },
    },

    // 饼图
    pie: {
      itemStyle: {
        borderWidth: 1,
        borderColor: COLORS.WHITE,
      },
      label: {
        color: COLORS.TEXT_PRIMARY,
      },
      labelLine: {
        lineStyle: {
          color: COLORS.GRAY_300,
        },
      },
    },

    // 散点图
    scatter: {
      symbolSize: 8,
    },

    // 仪表盘
    gauge: {
      axisLine: {
        lineStyle: {
          width: 15,
        },
      },
      axisTick: {
        length: 8,
        lineStyle: {
          color: COLORS.WHITE,
          width: 2,
        },
      },
      splitLine: {
        length: 15,
        lineStyle: {
          color: COLORS.WHITE,
          width: 2,
        },
      },
      pointer: {
        width: 5,
      },
      title: {
        color: COLORS.TEXT_SECONDARY,
      },
      detail: {
        color: COLORS.TEXT_PRIMARY,
      },
    },
  },

  // 财务特定配置
  financial: {
    // 营收趋势图
    revenueTrend: {
      series: [
        {
          name: '营收',
          color: CHART_PALETTE.FINANCIAL.REVENUE,
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(47, 143, 91, 0.3)' },
                { offset: 1, color: 'rgba(47, 143, 91, 0.05)' },
              ],
            },
          },
        },
        {
          name: '成本',
          color: CHART_PALETTE.FINANCIAL.COST,
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(217, 143, 32, 0.3)' },
                { offset: 1, color: 'rgba(217, 143, 32, 0.05)' },
              ],
            },
          },
        },
        {
          name: '利润',
          color: CHART_PALETTE.FINANCIAL.PROFIT,
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(200, 30, 30, 0.3)' },
                { offset: 1, color: 'rgba(200, 30, 30, 0.05)' },
              ],
            },
          },
        },
      ],
    },

    // 费用结构图
    expenseStructure: {
      color: CHART_PALETTE.CATEGORY,
    },

    // 门店排名
    storeRanking: {
      color: [
        'rgba(200, 30, 30, 0.1)',
        'rgba(200, 30, 30, 0.2)',
        'rgba(200, 30, 30, 0.3)',
        'rgba(200, 30, 30, 0.4)',
        'rgba(200, 30, 30, 0.5)',
      ],
    },

    // 利润率仪表盘
    profitMarginGauge: {
      axisLine: {
        lineStyle: {
          color: [
            [0.2, COLORS.DANGER],      // 0-8% 红色
            [0.375, COLORS.WARNING],   // 8-15% 黄色
            [1, COLORS.SUCCESS],       // 15-40% 绿色
          ],
        },
      },
    },
  },
}

// 暗色主题
export const ECHARTS_THEME_FINANCIAL_DARK = {
  ...ECHARTS_THEME_FINANCIAL,

  // 覆盖亮色主题的配置
  textStyle: {
    ...ECHARTS_THEME_FINANCIAL.textStyle,
    color: COLORS.GRAY_100,
  },

  title: {
    ...ECHARTS_THEME_FINANCIAL.title,
    textStyle: {
      ...ECHARTS_THEME_FINANCIAL.title.textStyle,
      color: COLORS.GRAY_100,
    },
    subtextStyle: {
      ...ECHARTS_THEME_FINANCIAL.title.subtextStyle,
      color: COLORS.GRAY_200,
    },
  },

  legend: {
    ...ECHARTS_THEME_FINANCIAL.legend,
    textStyle: {
      ...ECHARTS_THEME_FINANCIAL.legend.textStyle,
      color: COLORS.GRAY_200,
    },
  },

  tooltip: {
    ...ECHARTS_THEME_FINANCIAL.tooltip,
    backgroundColor: 'rgba(31, 41, 55, 0.95)',
    borderColor: COLORS.GRAY_700,
    textStyle: {
      ...ECHARTS_THEME_FINANCIAL.tooltip.textStyle,
      color: COLORS.GRAY_100,
    },
  },

  grid: {
    ...ECHARTS_THEME_FINANCIAL.grid,
    borderColor: COLORS.GRAY_700,
  },

  axisLine: {
    ...ECHARTS_THEME_FINANCIAL.axisLine,
    lineStyle: {
      ...ECHARTS_THEME_FINANCIAL.axisLine.lineStyle,
      color: COLORS.GRAY_600,
    },
  },

  axisTick: {
    ...ECHARTS_THEME_FINANCIAL.axisTick,
    lineStyle: {
      ...ECHARTS_THEME_FINANCIAL.axisTick.lineStyle,
      color: COLORS.GRAY_600,
    },
  },

  axisLabel: {
    ...ECHARTS_THEME_FINANCIAL.axisLabel,
    textStyle: {
      ...ECHARTS_THEME_FINANCIAL.axisLabel.textStyle,
      color: COLORS.GRAY_300,
    },
  },

  splitLine: {
    ...ECHARTS_THEME_FINANCIAL.splitLine,
    lineStyle: {
      ...ECHARTS_THEME_FINANCIAL.splitLine.lineStyle,
      color: COLORS.GRAY_800,
    },
  },
}

/**
 * 注册ECharts主题
 */
export function registerEChartsThemes() {
  // 注册亮色主题
  echarts.registerTheme('financial-light', ECHARTS_THEME_FINANCIAL)

  // 注册暗色主题
  echarts.registerTheme('financial-dark', ECHARTS_THEME_FINANCIAL_DARK)
}

/**
 * 获取当前主题
 */
export function getCurrentEChartsTheme(): string {
  if (typeof window === 'undefined') return 'financial-light'

  const isDark = document.documentElement.getAttribute('data-theme') === 'dark' ||
    document.documentElement.classList.contains('dark-mode')

  return isDark ? 'financial-dark' : 'financial-light'
}

/**
 * 初始化图表时应用主题
 */
export function initChartWithTheme(chart: any): void {
  // 当前主题已通过 initChart 应用
  chart.setOption({
    backgroundColor: 'transparent',
  }, false, true)
}

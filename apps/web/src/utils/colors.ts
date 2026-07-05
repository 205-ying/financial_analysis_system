/**
 * 颜色工具函数和常量
 * 从设计系统导出颜色值供JavaScript使用
 */

// 财务分析系统颜色常量 - 与 src/styles/variables/_colors.scss 保持一致
export const COLORS = {
  // 主色调
  PRIMARY: '#C81E1E',
  PRIMARY_LIGHT: '#DC2F2F',
  PRIMARY_LIGHTER: '#EF6A62',
  PRIMARY_LIGHTEST: '#FFF1EE',
  PRIMARY_DARK: '#A91419',
  PRIMARY_DARKER: '#741014',

  // 辅助色
  SECONDARY: '#D19A36',
  SECONDARY_LIGHT: '#E0B45D',
  SECONDARY_LIGHTER: '#F1D28F',
  SECONDARY_LIGHTEST: '#FFF7E6',
  SECONDARY_DARK: '#A66F17',
  SECONDARY_DARKER: '#765012',

  // 语义颜色
  SUCCESS: '#2F8F5B',
  SUCCESS_LIGHT: '#43A86F',
  SUCCESS_LIGHTER: '#9ED7B7',
  SUCCESS_LIGHTEST: '#E8F6EE',
  SUCCESS_DARK: '#1F7247',
  SUCCESS_DARKER: '#155334',

  WARNING: '#D98F20',
  WARNING_LIGHT: '#E7A640',
  WARNING_LIGHTER: '#F4CB7D',
  WARNING_LIGHTEST: '#FFF3DD',
  WARNING_DARK: '#A96711',
  WARNING_DARKER: '#75490E',

  DANGER: '#EF4444',
  DANGER_LIGHT: '#F87171',
  DANGER_LIGHTER: '#FCA5A5',
  DANGER_LIGHTEST: '#FEE2E2',
  DANGER_DARK: '#DC2626',
  DANGER_DARKER: '#B91C1C',

  INFO: '#405D65',
  INFO_LIGHT: '#5E7A82',
  INFO_LIGHTER: '#A8BBC0',
  INFO_LIGHTEST: '#EEF4F5',
  INFO_DARK: '#29434A',
  INFO_DARKER: '#16292F',

  // 中性色阶
  WHITE: '#FFFFFF',
  GRAY_50: '#FAF8F4',
  GRAY_100: '#F1EEE8',
  GRAY_200: '#E4DED5',
  GRAY_300: '#D2C9BD',
  GRAY_400: '#A99F94',
  GRAY_500: '#756D64',
  GRAY_600: '#554D46',
  GRAY_700: '#332D28',
  GRAY_800: '#171F20',
  GRAY_900: '#071114',
  BLACK: '#000000',

  // 文本颜色
  TEXT_PRIMARY: '#071114',
  TEXT_SECONDARY: '#695F55',
  TEXT_TERTIARY: '#756D64',
  TEXT_PLACEHOLDER: '#A99F94',
  TEXT_DISABLED: '#D2C9BD',
  TEXT_INVERSE: '#FFFFFF',

  // 图表色板
  CHART_CATEGORY_1: '#C81E1E',    // 主色
  CHART_CATEGORY_2: '#D19A36',    // 辅助色
  CHART_CATEGORY_3: '#2F8F5B',    // 成功色
  CHART_CATEGORY_4: '#D98F20',    // 警告色
  CHART_CATEGORY_5: '#EF4444',    // 危险色
  CHART_CATEGORY_6: '#405D65',    // 信息色
  CHART_CATEGORY_7: '#7A8289',    // 灰蓝
  CHART_CATEGORY_8: '#8B5E34',    // 棕金

  // 语义色板
  CHART_SEMANTIC_BAD: '#EF4444',
  CHART_SEMANTIC_WARNING: '#D98F20',
  CHART_SEMANTIC_GOOD: '#2F8F5B',

  // 渐变
  CHART_GRADIENT_START: '#C81E1E',
  CHART_GRADIENT_MID: '#D19A36',
  CHART_GRADIENT_END: '#2F8F5B',
} as const

// 图表调色板
export const CHART_PALETTE = {
  // 分类色板 - 用于饼图、柱状图等
  CATEGORY: [
    COLORS.CHART_CATEGORY_1,
    COLORS.CHART_CATEGORY_2,
    COLORS.CHART_CATEGORY_3,
    COLORS.CHART_CATEGORY_4,
    COLORS.CHART_CATEGORY_5,
    COLORS.CHART_CATEGORY_6,
    COLORS.CHART_CATEGORY_7,
    COLORS.CHART_CATEGORY_8,
  ],

  // 语义色板 - 用于仪表盘、进度条等
  SEMANTIC: {
    BAD: COLORS.CHART_SEMANTIC_BAD,
    WARNING: COLORS.CHART_SEMANTIC_WARNING,
    GOOD: COLORS.CHART_SEMANTIC_GOOD,
  },

  // 渐变 - 用于趋势图等
  GRADIENT: {
    START: COLORS.CHART_GRADIENT_START,
    MID: COLORS.CHART_GRADIENT_MID,
    END: COLORS.CHART_GRADIENT_END,
  },

  // 常用序列
  SEQUENTIAL: [
    COLORS.CHART_GRADIENT_START,
    COLORS.CHART_GRADIENT_MID,
    COLORS.CHART_GRADIENT_END,
  ],

  // 财务主题序列
  FINANCIAL: {
    REVENUE: COLORS.SUCCESS,      // 营收 - 绿色
    COST: COLORS.WARNING,         // 成本 - 黄色
    PROFIT: COLORS.PRIMARY,       // 利润 - 红色
    EXPENSE: COLORS.DANGER,       // 费用 - 红色
    MARGIN: COLORS.INFO,          // 利润率 - 墨绿色
  },
} as const

// 标签类型映射
export const TAG_COLORS = {
  success: COLORS.SUCCESS,
  info: COLORS.INFO,
  warning: COLORS.WARNING,
  danger: COLORS.DANGER,
  primary: COLORS.PRIMARY,
  secondary: COLORS.SECONDARY,
} as const

// 状态颜色映射
export const STATUS_COLORS = {
  success: COLORS.SUCCESS,
  failure: COLORS.WARNING,
  error: COLORS.DANGER,
  pending: COLORS.GRAY_400,
  processing: COLORS.INFO,
  completed: COLORS.SUCCESS,
} as const

/**
 * 从CSS变量获取颜色值
 * @param variable CSS变量名（不包含--前缀）
 * @param fallback 回退颜色值
 */
export function getCssColor(variable: string, fallback: string = COLORS.GRAY_400): string {
  if (typeof window === 'undefined') return fallback

  const value = getComputedStyle(document.documentElement)
    .getPropertyValue(`--color-${variable}`)
    .trim()

  return value || fallback
}

/**
 * 获取图表颜色（支持CSS变量和直接颜色值）
 */
export function getChartColor(index: number): string {
  if (index < CHART_PALETTE.CATEGORY.length) {
    return CHART_PALETTE.CATEGORY[index]
  }
  // 如果超出范围，循环使用
  return CHART_PALETTE.CATEGORY[index % CHART_PALETTE.CATEGORY.length]
}

/**
 * 生成渐变颜色
 */
export function generateGradient(
  start: string = COLORS.CHART_GRADIENT_START,
  end: string = COLORS.CHART_GRADIENT_END,
  steps: number = 5
): string[] {
  const colors: string[] = []

  for (let i = 0; i < steps; i++) {
    const ratio = i / (steps - 1)
    // 简单的线性插值（实际项目可能需要更复杂的颜色插值）
    colors.push(i === 0 ? start : i === steps - 1 ? end : `${start}${Math.floor(ratio * 100)}`)
  }

  return colors
}

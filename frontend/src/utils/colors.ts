/**
 * 颜色工具函数和常量
 * 从设计系统导出颜色值供JavaScript使用
 */

// 财务分析系统颜色常量 - 与 src/styles/variables/_colors.scss 保持一致
export const COLORS = {
  // 主色调
  PRIMARY: '#1E3A8A',
  PRIMARY_LIGHT: '#3B82F6',
  PRIMARY_LIGHTER: '#60A5FA',
  PRIMARY_LIGHTEST: '#DBEAFE',
  PRIMARY_DARK: '#1E40AF',
  PRIMARY_DARKER: '#1E3A8A',

  // 辅助色
  SECONDARY: '#D4AF37',
  SECONDARY_LIGHT: '#FBBF24',
  SECONDARY_LIGHTER: '#FCD34D',
  SECONDARY_LIGHTEST: '#FEF3C7',
  SECONDARY_DARK: '#B45309',
  SECONDARY_DARKER: '#92400E',

  // 语义颜色
  SUCCESS: '#10B981',
  SUCCESS_LIGHT: '#34D399',
  SUCCESS_LIGHTER: '#A7F3D0',
  SUCCESS_LIGHTEST: '#D1FAE5',
  SUCCESS_DARK: '#059669',
  SUCCESS_DARKER: '#047857',

  WARNING: '#F59E0B',
  WARNING_LIGHT: '#FBBF24',
  WARNING_LIGHTER: '#FCD34D',
  WARNING_LIGHTEST: '#FEF3C7',
  WARNING_DARK: '#D97706',
  WARNING_DARKER: '#B45309',

  DANGER: '#EF4444',
  DANGER_LIGHT: '#F87171',
  DANGER_LIGHTER: '#FCA5A5',
  DANGER_LIGHTEST: '#FEE2E2',
  DANGER_DARK: '#DC2626',
  DANGER_DARKER: '#B91C1C',

  INFO: '#3B82F6',
  INFO_LIGHT: '#60A5FA',
  INFO_LIGHTER: '#93C5FD',
  INFO_LIGHTEST: '#DBEAFE',
  INFO_DARK: '#2563EB',
  INFO_DARKER: '#1D4ED8',

  // 中性色阶
  WHITE: '#FFFFFF',
  GRAY_50: '#F9FAFB',
  GRAY_100: '#F3F4F6',
  GRAY_200: '#E5E7EB',
  GRAY_300: '#D1D5DB',
  GRAY_400: '#9CA3AF',
  GRAY_500: '#6B7280',
  GRAY_600: '#4B5563',
  GRAY_700: '#374151',
  GRAY_800: '#1F2937',
  GRAY_900: '#111827',
  BLACK: '#000000',

  // 文本颜色
  TEXT_PRIMARY: '#111827',
  TEXT_SECONDARY: '#374151',
  TEXT_TERTIARY: '#6B7280',
  TEXT_PLACEHOLDER: '#9CA3AF',
  TEXT_DISABLED: '#D1D5DB',
  TEXT_INVERSE: '#FFFFFF',

  // 图表色板
  CHART_CATEGORY_1: '#1E3A8A',    // 主色
  CHART_CATEGORY_2: '#D4AF37',    // 辅助色
  CHART_CATEGORY_3: '#10B981',    // 成功色
  CHART_CATEGORY_4: '#F59E0B',    // 警告色
  CHART_CATEGORY_5: '#EF4444',    // 危险色
  CHART_CATEGORY_6: '#3B82F6',    // 信息色
  CHART_CATEGORY_7: '#8B5CF6',    // 紫色
  CHART_CATEGORY_8: '#EC4899',    // 粉色

  // 语义色板
  CHART_SEMANTIC_BAD: '#EF4444',
  CHART_SEMANTIC_WARNING: '#F59E0B',
  CHART_SEMANTIC_GOOD: '#10B981',

  // 渐变
  CHART_GRADIENT_START: '#1E3A8A',
  CHART_GRADIENT_MID: '#3B82F6',
  CHART_GRADIENT_END: '#10B981',
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
    PROFIT: COLORS.PRIMARY,       // 利润 - 蓝色
    EXPENSE: COLORS.DANGER,       // 费用 - 红色
    MARGIN: COLORS.INFO,          // 利润率 - 浅蓝色
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
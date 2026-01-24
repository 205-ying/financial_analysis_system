/**
 * 格式化工具函数
 */

/**
 * 格式化金额
 * @param amount 金额
 * @param precision 精度，默认2位小数
 */
export function formatCurrency(amount: number | string, precision = 2): string {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount
  if (isNaN(num)) return '0.00'
  return num.toFixed(precision)
}

/**
 * 格式化百分比
 * @param value 数值
 * @param precision 精度，默认2位小数
 */
export function formatPercent(value: number | string, precision = 2): string {
  const num = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(num)) return '0.00%'
  return `${num.toFixed(precision)}%`
}

/**
 * 格式化数字（千分位）
 * @param num 数字
 */
export function formatNumber(num: number | string): string {
  const value = typeof num === 'string' ? parseFloat(num) : num
  if (isNaN(value)) return '0'
  return value.toLocaleString('zh-CN')
}

/**
 * 格式化日期
 * @param date 日期
 * @param format 格式，默认 'YYYY-MM-DD'
 */
export function formatDate(
  date: Date | string | number,
  format = 'YYYY-MM-DD'
): string {
  const d = new Date(date)
  if (isNaN(d.getTime())) return ''

  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')

  return format
    .replace('YYYY', String(year))
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 格式化日期时间
 * @param date 日期
 */
export function formatDateTime(date: Date | string | number): string {
  return formatDate(date, 'YYYY-MM-DD HH:mm:ss')
}

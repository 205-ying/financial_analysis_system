/**
 * 验证工具函数
 */

/**
 * 验证邮箱格式
 */
export function isEmail(email: string): boolean {
  const reg = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  return reg.test(email)
}

/**
 * 验证手机号格式（中国大陆）
 */
export function isPhone(phone: string): boolean {
  const reg = /^1[3-9]\d{9}$/
  return reg.test(phone)
}

/**
 * 验证URL格式
 */
export function isURL(url: string): boolean {
  const reg = /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/
  return reg.test(url)
}

/**
 * 验证身份证号
 */
export function isIDCard(idCard: string): boolean {
  const reg = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/
  return reg.test(idCard)
}

/**
 * 验证用户名（字母开头，允许字母数字下划线）
 */
export function isUsername(username: string): boolean {
  const reg = /^[a-zA-Z][a-zA-Z0-9_]{3,15}$/
  return reg.test(username)
}

/**
 * 验证密码强度（至少8位，包含大小写字母和数字）
 */
export function isStrongPassword(password: string): boolean {
  const reg = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/
  return reg.test(password)
}

/**
 * 验证是否为正整数
 */
export function isPositiveInteger(value: string | number): boolean {
  const num = typeof value === 'string' ? parseInt(value) : value
  return Number.isInteger(num) && num > 0
}

/**
 * 验证是否为正数（包括小数）
 */
export function isPositiveNumber(value: string | number): boolean {
  const num = typeof value === 'string' ? parseFloat(value) : value
  return !isNaN(num) && num > 0
}

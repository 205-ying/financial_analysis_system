/**
 * 环境配置
 */

interface EnvConfig {
  apiBaseUrl: string
  isDevelopment: boolean
  isProduction: boolean
  mode: string
}

const env = import.meta.env

export const envConfig: EnvConfig = {
  apiBaseUrl: env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  isDevelopment: env.MODE === 'development',
  isProduction: env.MODE === 'production',
  mode: env.MODE || 'development'
}

export default envConfig

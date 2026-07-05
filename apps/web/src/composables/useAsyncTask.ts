import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'

type MessageFactory<TResult, TArgs extends unknown[]> =
  | string
  | ((result: TResult, args: TArgs) => string)

type ErrorMessageFactory<TArgs extends unknown[]> =
  | string
  | ((error: unknown, args: TArgs) => string)

export interface AsyncTaskOptions<TResult, TArgs extends unknown[]> {
  successMessage?: MessageFactory<TResult, TArgs>
  errorMessage?: ErrorMessageFactory<TArgs>
  silentError?: boolean
  onSuccess?: (result: TResult, args: TArgs) => void
  onError?: (error: unknown, args: TArgs) => void
}

const fallbackErrorMessage = (error: unknown, fallback = '操作失败') => {
  if (error instanceof Error && error.message) return error.message
  return fallback
}

export function useAsyncTask<TResult, TArgs extends unknown[] = []>(
  task: (...args: TArgs) => Promise<TResult>,
  options: AsyncTaskOptions<TResult, TArgs> = {}
) {
  const loading = ref(false)
  const error = ref<unknown>(null)
  const lastRunAt = ref<Date | null>(null)

  const hasError = computed(() => error.value !== null)

  const execute = async (...args: TArgs) => {
    loading.value = true
    error.value = null

    try {
      const result = await task(...args)
      lastRunAt.value = new Date()

      if (options.successMessage) {
        const message =
          typeof options.successMessage === 'function'
            ? options.successMessage(result, args)
            : options.successMessage
        ElMessage.success(message)
      }

      options.onSuccess?.(result, args)
      return result
    } catch (err) {
      error.value = err
      options.onError?.(err, args)

      if (!options.silentError) {
        const message = options.errorMessage
          ? typeof options.errorMessage === 'function'
            ? options.errorMessage(err, args)
            : options.errorMessage
          : fallbackErrorMessage(err)
        ElMessage.error(message)
      }

      throw err
    } finally {
      loading.value = false
    }
  }

  const reset = () => {
    error.value = null
    lastRunAt.value = null
  }

  return {
    loading,
    error,
    hasError,
    lastRunAt,
    execute,
    reset,
  }
}

export default useAsyncTask

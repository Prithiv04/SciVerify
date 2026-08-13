import axios from 'axios'
import { env } from '@/lib/env'
import type { VerificationApiErrorBody } from '@/types/backend-verification'

function formatApiError(error: unknown): string {
  if (!axios.isAxiosError<VerificationApiErrorBody>(error)) {
    return error instanceof Error
      ? error.message
      : 'An unexpected error occurred'
  }

  if (!error.response) {
    return 'Unable to connect to the SciVerify backend. Please make sure the backend server is running.'
  }

  const detail = error.response.data?.detail

  if (typeof detail === 'string' && detail.trim()) {
    return detail
  }

  if (Array.isArray(detail) && detail.length > 0) {
    return detail
      .map((item) => item.msg)
      .filter(Boolean)
      .join(', ')
  }

  return error.message || 'An unexpected error occurred'
}

export const apiClient = axios.create({
  baseURL: env.apiBaseUrl || undefined,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(new Error(formatApiError(error))),
)

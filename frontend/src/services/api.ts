import axios from 'axios'
import { env } from '@/lib/env'

export const apiClient = axios.create({
  baseURL: env.apiBaseUrl || undefined,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.message ??
      error.message ??
      'An unexpected error occurred'

    return Promise.reject(new Error(message))
  },
)

import type { VerdictKey } from '@/constants/verdicts'

export type { VerdictKey }

export type AgentStatus = 'idle' | 'running' | 'completed' | 'error'

export type TimelineStepStatus = 'pending' | 'active' | 'completed' | 'error'

export interface ApiError {
  message: string
  status?: number
}

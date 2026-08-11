export type Verdict = 'true' | 'false' | 'mixed' | 'unverified'

export interface ApiError {
  message: string
  status?: number
}

import type { VerdictKey } from '@/constants/verdicts'

export type SourceType = 'doi' | 'url' | 'citation' | 'reference'

export interface AgentAnalysis {
  role: string
  summary: string
  finding: string
  status: 'completed' | 'running' | 'idle'
}

export interface EvidenceItem {
  id: string
  title: string
  source: string
  year?: number
  excerpt: string
  relevance: number
  evidenceType: string
  identifier?: string
  verdict?: VerdictKey
}

export interface SuggestedCorrection {
  originalClaim: string
  suggestedWording: string
}

export interface VerificationResult {
  id: string
  claim: string
  citation: string
  sourceType: SourceType
  verdict: VerdictKey
  confidence: number
  summary: string
  reasoning: string
  prosecutor: AgentAnalysis
  defender: AgentAnalysis
  adjudicator: AgentAnalysis
  evidence: EvidenceItem[]
  suggestedCorrection: SuggestedCorrection
  createdAt: string
}

export type VerificationRecord = VerificationResult

export interface VerificationFormInput {
  claim: string
  citation: string
  sourceType: SourceType
}

export interface DashboardStats {
  total: number
  supports: number
  overstated: number
  contradicts: number
  insufficient: number
  fabricated: number
}

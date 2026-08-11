import type { VerdictKey } from '@/constants/verdicts'

export type SourceType = 'doi' | 'url' | 'citation' | 'reference'

export type CitationStatus = 'verified' | 'fabricated' | 'unverified'

export type EvidenceStrength = 'HIGH' | 'MEDIUM' | 'LOW'

export interface AgentAnalysis {
  role: string
  summary: string
  finding: string
  status: 'completed' | 'running' | 'idle'
}

export interface EvidenceItem {
  id: string
  title: string
  authors?: string
  source: string
  year?: number
  excerpt: string
  whyItMatters?: string
  relevance: number
  strength?: EvidenceStrength
  evidenceType: string
  identifier?: string
  sourceUrl?: string
  verdict?: VerdictKey
}

export interface EvidenceFactor {
  text: string
  supported: boolean
}

export interface SuggestedCorrection {
  originalClaim: string
  problem: string
  suggestedWording: string
}

export interface VerificationResult {
  id: string
  claim: string
  citation: string
  sourceType: SourceType
  context?: string
  citationStatus: CitationStatus
  verdict: VerdictKey
  confidence: number
  summary: string
  reasoning: string
  evidenceFactors: EvidenceFactor[]
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
  context?: string
}

export interface DashboardStats {
  total: number
  supports: number
  overstated: number
  contradicts: number
  insufficient: number
  fabricated: number
}

export interface VerificationProgressUpdate {
  stageId: string
  stageIndex: number
  message?: string
}

export type VerificationStageGroup = 'pipeline' | 'agent'

export interface VerificationStage {
  id: string
  title: string
  group: VerificationStageGroup
  agent?: 'prosecutor' | 'defender' | 'adjudicator'
  activeMessage?: string
}

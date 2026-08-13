import type { VerdictKey } from '@/constants/verdicts'
import type {
  AgentAnalysis,
  EvidenceFactor,
  EvidenceItem,
  EvidenceStrength,
  SuggestedCorrection,
  VerificationFormInput,
  VerificationResult,
} from '@/types/verification'
import type {
  BackendAgentAnalysis,
  BackendAdjudicatorAnalysis,
  BackendEvidenceItem,
  BackendPaperSummary,
  BackendVerificationResponse,
} from '@/types/backend-verification'

function emptyAgent(role: string): AgentAnalysis {
  return {
    role,
    summary: 'Analysis unavailable.',
    finding: 'No agent output was returned for this verification.',
    status: 'completed',
  }
}

function emptyCorrection(claim: string): SuggestedCorrection {
  return {
    originalClaim: claim,
    problem: 'No correction was suggested.',
    suggestedWording: claim,
  }
}

function toConfidencePercent(value: number | null | undefined): number {
  if (value == null || Number.isNaN(value)) return 0
  if (value <= 1) return Math.round(value * 100)
  return Math.round(value)
}

function mapAgent(
  agent: BackendAgentAnalysis | null | undefined,
  role: string,
): AgentAnalysis {
  if (!agent) return emptyAgent(role)

  const keyPoints = agent.key_points?.filter(Boolean) ?? []
  const finding =
    keyPoints.length > 0
      ? keyPoints.join(' ')
      : agent.stance || 'Analysis completed.'

  return {
    role,
    summary: agent.analysis,
    finding,
    status: 'completed',
  }
}

function mapAdjudicator(
  agent: BackendAdjudicatorAnalysis | null | undefined,
): AgentAnalysis {
  if (!agent) return emptyAgent('Adjudicator')

  return {
    role: 'Adjudicator',
    summary: agent.analysis,
    finding: agent.reasoning,
    status: 'completed',
  }
}

function evidenceStrength(relevance: number): EvidenceStrength {
  if (relevance >= 0.7) return 'HIGH'
  if (relevance >= 0.4) return 'MEDIUM'
  return 'LOW'
}

function mapEvidenceItem(
  item: BackendEvidenceItem,
  paper: BackendPaperSummary,
  verdict?: VerdictKey,
): EvidenceItem {
  return {
    id: item.chunk_id,
    title: `${item.section} · chunk ${item.chunk_index + 1}`,
    source: paper.title ?? paper.doi,
    excerpt: item.text,
    whyItMatters:
      item.claim_numbers?.length || item.evidence_numbers?.length
        ? `Claim numbers: ${item.claim_numbers?.join(', ') || 'none'}. Evidence numbers: ${item.evidence_numbers?.join(', ') || 'none'}.`
        : undefined,
    relevance: Math.round(item.relevance_score * 100),
    strength: evidenceStrength(item.relevance_score),
    evidenceType: item.section,
    identifier: paper.doi,
    sourceUrl: item.source_url ?? undefined,
    verdict,
  }
}

function buildEvidenceFactors(response: BackendVerificationResponse): EvidenceFactor[] {
  const factors: EvidenceFactor[] = []

  for (const point of response.prosecutor?.key_points ?? []) {
    factors.push({ text: point, supported: false })
  }
  for (const point of response.defender?.key_points ?? []) {
    factors.push({ text: point, supported: true })
  }

  return factors
}

function mapSuggestedCorrection(
  response: BackendVerificationResponse,
  claim: string,
): SuggestedCorrection {
  const suggested =
    response.suggested_correction ??
    response.adjudicator?.suggested_correction ??
    null

  if (!suggested) {
    return emptyCorrection(claim)
  }

  return {
    originalClaim: claim,
    problem: response.reasoning ?? response.summary ?? 'The claim needs revision.',
    suggestedWording: suggested,
  }
}

function resolveCitationStatus(
  response: BackendVerificationResponse,
): VerificationResult['citationStatus'] {
  if (response.verdict === 'FABRICATED') return 'fabricated'
  if (response.paper?.doi) return 'verified'
  return 'unverified'
}

export function mapBackendVerificationToResult(
  response: BackendVerificationResponse,
  input: VerificationFormInput,
): VerificationResult {
  const verdict = response.verdict ?? 'INSUFFICIENT'
  const confidence = toConfidencePercent(response.confidence)
  const summary =
    response.summary ??
    response.adjudicator?.analysis ??
    'Verification completed.'
  const reasoning =
    response.reasoning ??
    response.adjudicator?.reasoning ??
    response.detail ??
    summary

  return {
    id: crypto.randomUUID(),
    claim: response.claim,
    citation: input.citation,
    sourceType: input.sourceType,
    context: input.context,
    citationStatus: resolveCitationStatus(response),
    verdict,
    confidence,
    summary,
    reasoning,
    evidenceFactors: buildEvidenceFactors(response),
    prosecutor: mapAgent(response.prosecutor, 'Prosecutor'),
    defender: mapAgent(response.defender, 'Defender'),
    adjudicator: mapAdjudicator(response.adjudicator),
    evidence: (response.evidence ?? []).map((item) =>
      mapEvidenceItem(item, response.paper, verdict),
    ),
    suggestedCorrection: mapSuggestedCorrection(response, response.claim),
    createdAt: new Date().toISOString(),
  }
}

export function mapInsufficientEvidenceResult(
  response: BackendVerificationResponse,
  input: VerificationFormInput,
): VerificationResult {
  return {
    id: crypto.randomUUID(),
    claim: response.claim,
    citation: input.citation,
    sourceType: input.sourceType,
    context: input.context,
    citationStatus: response.paper?.doi ? 'verified' : 'unverified',
    verdict: 'INSUFFICIENT',
    confidence: 0,
    summary:
      response.summary ??
      'There was not enough evidence to determine whether the claim is supported.',
    reasoning:
      response.reasoning ??
      response.detail ??
      'Evidence retrieval did not produce usable chunks for verification.',
    evidenceFactors: [],
    prosecutor: emptyAgent('Prosecutor'),
    defender: emptyAgent('Defender'),
    adjudicator: emptyAgent('Adjudicator'),
    evidence: (response.evidence ?? []).map((item) =>
      mapEvidenceItem(item, response.paper, 'INSUFFICIENT'),
    ),
    suggestedCorrection: emptyCorrection(response.claim),
    createdAt: new Date().toISOString(),
  }
}

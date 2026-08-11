import type {
  DashboardStats,
  VerificationFormInput,
  VerificationResult,
} from '@/types/verification'

const daysAgo = (days: number) =>
  new Date(Date.now() - days * 86_400_000).toISOString()

export const MOCK_VERIFICATION_HISTORY: VerificationResult[] = [
  {
    id: 'mock-001',
    claim:
      'The proposed intervention reduces the primary biomarker by 40% in clinical cohorts.',
    citation: '10.1000/demo.2024.001 — Demo Clinical Outcomes Study',
    sourceType: 'doi',
    verdict: 'OVERSTATED',
    confidence: 76,
    summary:
      'The cited source supports a reduction in the measured outcome, but the reported magnitude in the claim is stronger than the evidence presented.',
    reasoning:
      'The cited evidence supports the direction of the claim but does not support the reported magnitude.',
    prosecutor: {
      role: 'Prosecutor',
      summary: 'Challenges the claim and searches for weaknesses.',
      finding:
        'The source reports a smaller effect size than the claim suggests.',
      status: 'completed',
    },
    defender: {
      role: 'Defender',
      summary: 'Builds the strongest evidence-based supporting case.',
      finding:
        'The cited study does demonstrate a statistically significant improvement under the tested conditions.',
      status: 'completed',
    },
    adjudicator: {
      role: 'Adjudicator',
      summary: 'Weighs both arguments against the available evidence.',
      finding:
        'The direction of the effect is supported, but the magnitude is overstated.',
      status: 'completed',
    },
    evidence: [
      {
        id: 'ev-001',
        title: 'Demo Clinical Outcomes Study',
        source: 'Demo Journal of Applied Research',
        year: 2024,
        excerpt:
          'The intervention group showed a statistically significant reduction in the primary biomarker compared with placebo controls.',
        relevance: 94,
        evidenceType: 'Primary outcome',
        identifier: '10.1000/demo.2024.001',
        verdict: 'SUPPORTS',
      },
    ],
    suggestedCorrection: {
      originalClaim:
        'The proposed intervention reduces the primary biomarker by 40% in clinical cohorts.',
      suggestedWording:
        'The intervention was associated with a statistically significant reduction in the primary biomarker under the tested conditions.',
    },
    createdAt: daysAgo(1),
  },
  {
    id: 'mock-002',
    claim:
      'Meta-analysis confirms the therapy improves long-term survival across all subgroups.',
    citation: 'https://example.org/demo/meta-analysis-review',
    sourceType: 'url',
    verdict: 'CONTRADICTS',
    confidence: 82,
    summary:
      'The cited review does not support survival improvements across all subgroups as stated.',
    reasoning:
      'Subgroup analyses in the cited review show null or inconsistent survival effects in several cohorts.',
    prosecutor: {
      role: 'Prosecutor',
      summary: 'Challenges the claim and searches for weaknesses.',
      finding:
        'Multiple subgroups in the cited review do not show significant survival benefit.',
      status: 'completed',
    },
    defender: {
      role: 'Defender',
      summary: 'Builds the strongest evidence-based supporting case.',
      finding:
        'Pooled estimates show a modest survival trend in the overall population.',
      status: 'completed',
    },
    adjudicator: {
      role: 'Adjudicator',
      summary: 'Weighs both arguments against the available evidence.',
      finding:
        'The universal subgroup claim is not supported by the cited evidence.',
      status: 'completed',
    },
    evidence: [
      {
        id: 'ev-002',
        title: 'Demo Meta-Analysis Review',
        source: 'Demo Evidence Synthesis Reports',
        year: 2023,
        excerpt:
          'Pooled hazard ratios varied substantially across predefined subgroups, with several confidence intervals crossing unity.',
        relevance: 88,
        evidenceType: 'Meta-analysis',
        verdict: 'CONTRADICTS',
      },
    ],
    suggestedCorrection: {
      originalClaim:
        'Meta-analysis confirms the therapy improves long-term survival across all subgroups.',
      suggestedWording:
        'The cited meta-analysis reports mixed survival effects across subgroups, with pooled estimates that should be interpreted cautiously.',
    },
    createdAt: daysAgo(3),
  },
  {
    id: 'mock-003',
    claim:
      'The compound demonstrates complete tumor regression in preclinical models.',
    citation: 'Smith et al., Demo Oncology Letters, 2022',
    sourceType: 'citation',
    verdict: 'SUPPORTS',
    confidence: 91,
    summary:
      'The cited preclinical study reports complete regression in a defined model subset.',
    reasoning:
      'The claim aligns with reported complete regression outcomes in the referenced model conditions.',
    prosecutor: {
      role: 'Prosecutor',
      summary: 'Challenges the claim and searches for weaknesses.',
      finding:
        'Complete regression was observed only in a specific model configuration.',
      status: 'completed',
    },
    defender: {
      role: 'Defender',
      summary: 'Builds the strongest evidence-based supporting case.',
      finding:
        'The study explicitly documents complete regression under the tested preclinical conditions.',
      status: 'completed',
    },
    adjudicator: {
      role: 'Adjudicator',
      summary: 'Weighs both arguments against the available evidence.',
      finding:
        'The claim is supported when scoped to the conditions described in the source.',
      status: 'completed',
    },
    evidence: [
      {
        id: 'ev-003',
        title: 'Preclinical Tumor Regression Study (Demo)',
        source: 'Demo Oncology Letters',
        year: 2022,
        excerpt:
          'Complete tumor regression was observed in the treated cohort under the specified xenograft conditions.',
        relevance: 92,
        evidenceType: 'Preclinical',
        verdict: 'SUPPORTS',
      },
    ],
    suggestedCorrection: {
      originalClaim:
        'The compound demonstrates complete tumor regression in preclinical models.',
      suggestedWording:
        'The compound demonstrated complete tumor regression in the specific preclinical model conditions described in the cited study.',
    },
    createdAt: daysAgo(5),
  },
  {
    id: 'mock-004',
    claim:
      'The dataset proves universal efficacy with no observed adverse events.',
    citation: 'Demo unpublished manuscript reference text',
    sourceType: 'reference',
    verdict: 'INSUFFICIENT',
    confidence: 58,
    summary:
      'Insufficient reliable evidence is available to evaluate universal efficacy or safety claims.',
    reasoning:
      'The provided reference lacks peer-reviewed outcomes data required for this evaluation.',
    prosecutor: {
      role: 'Prosecutor',
      summary: 'Challenges the claim and searches for weaknesses.',
      finding:
        'No verified outcomes data supports universal efficacy or zero adverse events.',
      status: 'completed',
    },
    defender: {
      role: 'Defender',
      summary: 'Builds the strongest evidence-based supporting case.',
      finding:
        'The reference may contain preliminary observations, but they are not independently verified.',
      status: 'completed',
    },
    adjudicator: {
      role: 'Adjudicator',
      summary: 'Weighs both arguments against the available evidence.',
      finding:
        'Available material is insufficient for a definitive verdict on efficacy or safety.',
      status: 'completed',
    },
    evidence: [],
    suggestedCorrection: {
      originalClaim:
        'The dataset proves universal efficacy with no observed adverse events.',
      suggestedWording:
        'Further peer-reviewed evidence is required before efficacy or safety claims can be stated.',
    },
    createdAt: daysAgo(8),
  },
  {
    id: 'mock-005',
    claim:
      'Randomized trial data show a 20% accuracy improvement on real-world datasets.',
    citation: '10.1000/demo.2023.045',
    sourceType: 'doi',
    verdict: 'OVERSTATED',
    confidence: 74,
    summary:
      'The cited trial supports improvement, but the 20% figure exceeds what the source reports.',
    reasoning:
      'Reported gains are positive but materially lower than the stated percentage.',
    prosecutor: {
      role: 'Prosecutor',
      summary: 'Challenges the claim and searches for weaknesses.',
      finding: 'Reported accuracy gains are closer to 11–14% in the source.',
      status: 'completed',
    },
    defender: {
      role: 'Defender',
      summary: 'Builds the strongest evidence-based supporting case.',
      finding:
        'The trial reports statistically significant accuracy improvements on benchmark tasks.',
      status: 'completed',
    },
    adjudicator: {
      role: 'Adjudicator',
      summary: 'Weighs both arguments against the available evidence.',
      finding:
        'Improvement is supported, but the exact 20% figure is not substantiated.',
      status: 'completed',
    },
    evidence: [
      {
        id: 'ev-005',
        title: 'Demo Benchmark Trial',
        source: 'Demo Methods Journal',
        year: 2023,
        excerpt:
          'The proposed method improved benchmark accuracy by approximately 12% relative to the baseline system.',
        relevance: 90,
        evidenceType: 'Trial outcome',
        identifier: '10.1000/demo.2023.045',
        verdict: 'OVERSTATED',
      },
    ],
    suggestedCorrection: {
      originalClaim:
        'Randomized trial data show a 20% accuracy improvement on real-world datasets.',
      suggestedWording:
        'The cited trial reports a statistically significant accuracy improvement, though the magnitude is lower than 20%.',
    },
    createdAt: daysAgo(12),
  },
]

export function computeDashboardStats(
  records: VerificationResult[],
): DashboardStats {
  return {
    total: records.length,
    supports: records.filter((r) => r.verdict === 'SUPPORTS').length,
    overstated: records.filter((r) => r.verdict === 'OVERSTATED').length,
    contradicts: records.filter((r) => r.verdict === 'CONTRADICTS').length,
    insufficient: records.filter((r) => r.verdict === 'INSUFFICIENT').length,
    fabricated: records.filter((r) => r.verdict === 'FABRICATED').length,
  }
}

export function buildMockVerificationResult(
  input: VerificationFormInput,
): VerificationResult {
  const template = MOCK_VERIFICATION_HISTORY[0]

  return {
    ...template,
    id: `mock-${crypto.randomUUID()}`,
    claim: input.claim,
    citation: input.citation,
    sourceType: input.sourceType,
    suggestedCorrection: {
      originalClaim: input.claim,
      suggestedWording: template.suggestedCorrection.suggestedWording,
    },
    createdAt: new Date().toISOString(),
  }
}

export const VERIFICATION_LOADING_STEPS = [
  'Analyzing citation...',
  'Checking source...',
  'Reviewing evidence...',
  'Running agent analysis...',
  'Preparing verdict...',
] as const

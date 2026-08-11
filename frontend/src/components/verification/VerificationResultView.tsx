import { EvidenceCard } from '@/components/sciverify/EvidenceCard'
import { SourceCard } from '@/components/sciverify/SourceCard'
import { ConfidenceBar } from '@/components/sciverify/ConfidenceBar'
import { VerdictCard } from '@/components/sciverify/VerdictCard'
import { AgentAnalysisPanel } from '@/components/verification/AgentAnalysisPanel'
import { SuggestedCorrectionPanel } from '@/components/verification/SuggestedCorrectionPanel'
import { Panel } from '@/components/ui/Card'
import { Divider } from '@/components/ui/Divider'
import type { VerificationResult } from '@/types/verification'

export interface VerificationResultViewProps {
  result: VerificationResult
}

export function VerificationResultView({ result }: VerificationResultViewProps) {
  return (
    <div className="space-y-8">
      <VerdictCard
        verdict={result.verdict}
        title="Final verdict"
        summary={result.summary}
        confidence={result.confidence}
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <Panel padding="md">
          <p className="text-xs font-medium uppercase tracking-wide text-text-muted">
            Claim
          </p>
          <p className="mt-2 text-sm leading-relaxed text-text-primary">
            {result.claim}
          </p>
        </Panel>
        <Panel padding="md">
          <p className="text-xs font-medium uppercase tracking-wide text-text-muted">
            Citation / source
          </p>
          <p className="mt-2 text-sm leading-relaxed text-text-primary">
            {result.citation}
          </p>
        </Panel>
      </div>

      <Panel padding="md">
        <h3 className="text-base font-semibold text-text-primary">Reasoning</h3>
        <p className="mt-2 text-sm leading-relaxed text-text-secondary">
          {result.reasoning}
        </p>
        <div className="mt-4">
          <ConfidenceBar
            value={result.confidence}
            verdict={result.verdict}
            label="Confidence"
          />
        </div>
      </Panel>

      <Divider label="Agent debate results" />

      <AgentAnalysisPanel
        prosecutor={result.prosecutor}
        defender={result.defender}
        adjudicator={result.adjudicator}
      />

      {result.evidence.length > 0 ? (
        <>
          <Divider label="Evidence" />
          <div className="grid gap-4 md:grid-cols-2">
            {result.evidence.map((item) => (
              <EvidenceCard
                key={item.id}
                title={item.title}
                source={item.source}
                excerpt={item.excerpt}
                verdict={item.verdict}
                relevance={item.relevance}
              />
            ))}
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            {result.evidence.map((item) => (
              <SourceCard
                key={`${item.id}-source`}
                title={item.title}
                journal={item.source}
                year={item.year}
                doi={item.identifier}
                type={item.evidenceType}
              />
            ))}
          </div>
        </>
      ) : (
        <Panel padding="md" className="text-sm text-text-secondary">
          No mock evidence items were available for this verification demo.
        </Panel>
      )}

      <SuggestedCorrectionPanel correction={result.suggestedCorrection} />
    </div>
  )
}

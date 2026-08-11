import type { ReactNode } from 'react'
import { Check, X } from 'lucide-react'
import { AgentAnalysisPanel } from '@/components/verification/AgentAnalysisPanel'
import { SuggestedCorrectionPanel } from '@/components/verification/SuggestedCorrectionPanel'
import { VerdictExplanation } from '@/components/verification/VerdictExplanation'
import { EvidenceCard } from '@/components/sciverify/EvidenceCard'
import { Panel } from '@/components/ui/Card'
import { Divider } from '@/components/ui/Divider'
import type { VerificationResult } from '@/types/verification'

export interface VerificationReportViewProps {
  result: VerificationResult
}

function ReportSection({
  title,
  children,
}: {
  title: string
  children: ReactNode
}) {
  return (
    <section className="space-y-3">
      <Divider label={title} />
      {children}
    </section>
  )
}

function CitationAuthenticity({ status }: { status: VerificationResult['citationStatus'] }) {
  const verified = status === 'verified'
  const fabricated = status === 'fabricated'

  return (
    <Panel padding="md" className="flex items-center gap-3">
      {fabricated ? (
        <X className="h-5 w-5 shrink-0 text-danger" aria-hidden />
      ) : (
        <Check
          className={cnIcon(verified)}
          aria-hidden
        />
      )}
      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-text-muted">
          Citation authenticity
        </p>
        <p
          className={
            fabricated
              ? 'mt-1 text-sm font-semibold text-danger'
              : verified
                ? 'mt-1 text-sm font-semibold text-success'
                : 'mt-1 text-sm font-semibold text-warning'
          }
        >
          {fabricated ? 'Fabricated' : verified ? 'Verified' : 'Unverified'}
        </p>
      </div>
    </Panel>
  )
}

function cnIcon(verified: boolean) {
  return verified
    ? 'h-5 w-5 shrink-0 text-success'
    : 'h-5 w-5 shrink-0 text-warning'
}

export function VerificationReportView({ result }: VerificationReportViewProps) {
  return (
    <article className="space-y-8">
      <header className="space-y-2">
        <p className="text-xs font-semibold uppercase tracking-widest text-primary">
          Science verification report
        </p>
        <p className="text-sm text-text-muted">
          Generated {new Date(result.createdAt).toLocaleString()}
        </p>
      </header>

      <ReportSection title="Claim">
        <Panel padding="md">
          <p className="text-sm leading-relaxed text-text-primary">{result.claim}</p>
          {result.context ? (
            <p className="mt-3 text-sm text-text-secondary">
              <span className="font-medium text-text-muted">Context: </span>
              {result.context}
            </p>
          ) : null}
        </Panel>
      </ReportSection>

      <ReportSection title="Citation">
        <Panel padding="md">
          <p className="text-sm leading-relaxed text-text-primary">{result.citation}</p>
          <p className="mt-2 text-xs uppercase text-text-muted">
            Source type: {result.sourceType}
          </p>
        </Panel>
      </ReportSection>

      <ReportSection title="Citation authenticity">
        <CitationAuthenticity status={result.citationStatus} />
      </ReportSection>

      <ReportSection title="Agent debate">
        <AgentAnalysisPanel
          prosecutor={result.prosecutor}
          defender={result.defender}
          adjudicator={result.adjudicator}
        />
      </ReportSection>

      <ReportSection title="Evidence">
        {result.evidence.length > 0 ? (
          <div className="grid gap-4 lg:grid-cols-2">
            {result.evidence.map((item) => (
              <EvidenceCard
                key={item.id}
                title={item.title}
                authors={item.authors}
                source={item.source}
                year={item.year}
                excerpt={item.excerpt}
                whyItMatters={item.whyItMatters}
                strength={item.strength}
                identifier={item.identifier}
                sourceUrl={item.sourceUrl}
                verdict={item.verdict}
                relevance={item.relevance}
              />
            ))}
          </div>
        ) : (
          <Panel padding="md" className="text-sm text-text-secondary">
            No evidence items were retrieved for this verification.
          </Panel>
        )}
      </ReportSection>

      <ReportSection title="Final verdict">
        <VerdictExplanation
          verdict={result.verdict}
          confidence={result.confidence}
          summary={result.summary}
          evidenceFactors={result.evidenceFactors}
        />
      </ReportSection>

      <ReportSection title="Suggested correction">
        <SuggestedCorrectionPanel correction={result.suggestedCorrection} />
      </ReportSection>
    </article>
  )
}

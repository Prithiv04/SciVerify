import { AgentCard } from '@/components/sciverify/AgentCard'
import { Panel } from '@/components/ui/Card'
import type { AgentAnalysis } from '@/types/verification'

export interface AgentAnalysisPanelProps {
  prosecutor: AgentAnalysis
  defender: AgentAnalysis
  adjudicator: AgentAnalysis
}

export function AgentAnalysisPanel({
  prosecutor,
  defender,
  adjudicator,
}: AgentAnalysisPanelProps) {
  return (
    <div className="space-y-4">
      <p className="text-center text-xs font-semibold uppercase tracking-widest text-text-muted">
        Agent debate
      </p>

      <div className="grid gap-4 md:grid-cols-[1fr_auto_1fr] md:items-start">
        <AgentCard
          name="Prosecutor"
          role="Challenge the claim"
          status="completed"
          description={prosecutor.finding}
        />
        <p
          className="hidden self-center text-sm font-semibold text-text-muted md:block"
          aria-hidden
        >
          VS
        </p>
        <AgentCard
          name="Defender"
          role="Build the strongest supporting case"
          status="completed"
          description={defender.finding}
        />
      </div>

      <p className="text-center text-lg text-text-muted" aria-hidden>
        ↓
      </p>

      <AgentCard
        name="Adjudicator"
        role="Make the final evidence-backed decision"
        status="completed"
        description={adjudicator.finding}
      />

      <div className="grid gap-4 lg:grid-cols-3">
        <Panel padding="sm" className="text-sm">
          <p className="text-xs font-medium uppercase tracking-wide text-text-muted">
            Prosecutor summary
          </p>
          <p className="mt-2 text-text-secondary">{prosecutor.summary}</p>
        </Panel>
        <Panel padding="sm" className="text-sm">
          <p className="text-xs font-medium uppercase tracking-wide text-text-muted">
            Defender summary
          </p>
          <p className="mt-2 text-text-secondary">{defender.summary}</p>
        </Panel>
        <Panel padding="sm" className="text-sm">
          <p className="text-xs font-medium uppercase tracking-wide text-text-muted">
            Adjudicator summary
          </p>
          <p className="mt-2 text-text-secondary">{adjudicator.summary}</p>
        </Panel>
      </div>
    </div>
  )
}

import { Scale, Shield, Swords } from 'lucide-react'
import { AgentCard } from '@/components/sciverify/AgentCard'
import { Panel } from '@/components/ui/Card'
import type { AgentAnalysis } from '@/types/verification'

export interface AgentAnalysisPanelProps {
  prosecutor: AgentAnalysis
  defender: AgentAnalysis
  adjudicator: AgentAnalysis
}

function AgentConclusion({
  title,
  role,
  summary,
  finding,
  icon,
}: {
  title: string
  role: string
  summary: string
  finding: string
  icon: typeof Swords
}) {
  return (
    <Panel padding="md" className="space-y-4">
      <AgentCard
        name={title}
        role={role}
        icon={icon}
        status="completed"
        description={finding}
      />
      <div className="border-t border-border pt-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">
          Evidence summary
        </p>
        <p className="mt-2 text-sm leading-relaxed text-text-secondary">{summary}</p>
      </div>
    </Panel>
  )
}

export function AgentAnalysisPanel({
  prosecutor,
  defender,
  adjudicator,
}: AgentAnalysisPanelProps) {
  return (
    <div className="space-y-6">
      <p className="text-center text-xs font-semibold uppercase tracking-widest text-text-muted">
        Agent debate
      </p>

      <div className="grid gap-4 lg:grid-cols-[1fr_auto_1fr] lg:items-start">
        <AgentConclusion
          title="Prosecutor"
          role="Challenge the claim"
          summary={prosecutor.summary}
          finding={prosecutor.finding}
          icon={Swords}
        />
        <p
          className="hidden self-center text-sm font-semibold text-text-muted lg:block"
          aria-hidden
        >
          VS
        </p>
        <AgentConclusion
          title="Defender"
          role="Build the supporting case"
          summary={defender.summary}
          finding={defender.finding}
          icon={Shield}
        />
      </div>

      <p className="text-center text-lg text-text-muted" aria-hidden>
        ↓
      </p>

      <Panel padding="md" className="space-y-4 border-primary/15">
        <p className="text-xs font-semibold uppercase tracking-widest text-primary">
          Final assessment
        </p>
        <AgentCard
          name="Adjudicator"
          role="Make the final evidence-backed decision"
          icon={Scale}
          status="completed"
          description={adjudicator.finding}
        />
        <div className="border-t border-border pt-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">
            Adjudicator summary
          </p>
          <p className="mt-2 text-sm leading-relaxed text-text-secondary">
            {adjudicator.summary}
          </p>
        </div>
      </Panel>
    </div>
  )
}

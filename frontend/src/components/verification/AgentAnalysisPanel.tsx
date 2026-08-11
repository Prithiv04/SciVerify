import { AgentCard } from '@/components/sciverify/AgentCard'
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
    <div className="grid gap-4 lg:grid-cols-3">
      <AgentCard
        name="Prosecutor"
        role="Challenges the claim"
        status="completed"
        description={prosecutor.finding}
      />
      <AgentCard
        name="Defender"
        role="Builds the supporting case"
        status="completed"
        description={defender.finding}
      />
      <AgentCard
        name="Adjudicator"
        role="Final decision-maker"
        status="completed"
        description={adjudicator.finding}
      />
    </div>
  )
}

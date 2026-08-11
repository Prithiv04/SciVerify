import { Badge } from '@/components/ui/Badge'
import { Panel } from '@/components/ui/Card'
import type { SuggestedCorrection } from '@/types/verification'

export interface SuggestedCorrectionPanelProps {
  correction: SuggestedCorrection
}

export function SuggestedCorrectionPanel({
  correction,
}: SuggestedCorrectionPanelProps) {
  return (
    <Panel padding="md" className="space-y-4 border-warning/20">
      <div className="flex flex-wrap items-center gap-2">
        <h3 className="text-lg font-semibold text-text-primary">
          Suggested Correction
        </h3>
        <Badge variant="warning">Requires human approval</Badge>
      </div>
      <p className="text-sm text-text-secondary">
        Suggested correction — requires human approval. SciVerify does not
        automatically modify research papers.
      </p>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-lg border border-border bg-surface p-4">
          <p className="text-xs font-medium uppercase tracking-wide text-text-muted">
            Original claim
          </p>
          <p className="mt-2 text-sm text-text-secondary">
            {correction.originalClaim}
          </p>
        </div>
        <div className="rounded-lg border border-primary/20 bg-primary-muted p-4">
          <p className="text-xs font-medium uppercase tracking-wide text-primary">
            Suggested wording
          </p>
          <p className="mt-2 text-sm text-text-primary">
            {correction.suggestedWording}
          </p>
        </div>
      </div>
    </Panel>
  )
}

import { Spinner } from '@/components/ui/Spinner'
import { Panel } from '@/components/ui/Card'
import { VerificationTimeline } from '@/components/sciverify/VerificationTimeline'
import type { TimelineStepStatus } from '@/types'

export interface VerificationLoadingProps {
  currentStep: string
  stepIndex: number
}

const timelineLabels = [
  'Analyze citation',
  'Check source',
  'Review evidence',
  'Run agent debate',
  'Prepare verdict',
]

export function VerificationLoading({
  currentStep,
  stepIndex,
}: VerificationLoadingProps) {
  const items = timelineLabels.map((title, index) => {
    let status: TimelineStepStatus = 'pending'
    if (index < stepIndex) status = 'completed'
    if (index === stepIndex) status = 'active'

    return {
      id: String(index),
      title,
      description: index === stepIndex ? currentStep : undefined,
      status,
    }
  })

  return (
    <div className="space-y-6">
      <Panel padding="md" className="flex items-center gap-4">
        <Spinner size="lg" className="text-primary" />
        <div>
          <p className="font-medium text-text-primary">{currentStep}</p>
          <p className="text-sm text-text-secondary">
            Simulated verification progress for demo purposes.
          </p>
        </div>
      </Panel>
      <VerificationTimeline items={items} />
    </div>
  )
}

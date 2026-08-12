import { Link } from 'react-router-dom'
import { ArrowDown, ArrowRight, Scale, Shield, Swords } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/cn'
import { ROUTES } from '@/constants'
import { Button } from '@/components/ui/Button'
import { Panel } from '@/components/ui/Card'

const agents: Array<{
  name: string
  icon: LucideIcon
  description: string
}> = [
  {
    name: 'Claim Challenger',
    icon: Swords,
    description: 'Challenges the claim',
  },
  {
    name: 'Evidence Defender',
    icon: Shield,
    description: 'Builds the supporting case',
  },
  {
    name: 'Final Reviewer',
    icon: Scale,
    description: 'Makes the final evidence decision',
  },
]

function AgentStep({
  name,
  icon: Icon,
  description,
  className,
}: {
  name: string
  icon: LucideIcon
  description: string
  className?: string
}) {
  return (
    <div
      className={cn(
        'flex w-full min-h-[5.25rem] items-start gap-3 rounded-lg border border-border/70 bg-surface/60 p-4',
        className,
      )}
    >
      <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md border border-border bg-surface-elevated">
        <Icon className="h-4 w-4 text-primary" />
      </span>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium leading-snug text-text-primary">{name}</p>
        <p className="mt-2 text-xs leading-relaxed text-text-muted">{description}</p>
      </div>
    </div>
  )
}

function StageConnector() {
  return (
    <div className="flex justify-center py-2" aria-hidden>
      <ArrowDown className="h-4 w-4 text-text-muted" />
    </div>
  )
}

export function VerificationWorkflowCta() {
  return (
    <Panel
      padding="lg"
      className="h-full border-primary/20 bg-gradient-to-br from-primary/8 via-surface-elevated/50 to-surface"
    >
      <p className="text-xs font-semibold uppercase tracking-widest text-primary">
        Verify a scientific claim
      </p>
      <h2 className="mt-2 text-lg font-semibold text-text-primary">
        Run a multi-agent evidence check
      </h2>
      <p className="mt-2 text-sm leading-relaxed text-text-secondary">
        Compare a claim against its cited evidence using three specialized
        verification agents.
      </p>

      <div className="mt-5 flex flex-col">
        {agents.flatMap((agent, index) => [
          <AgentStep key={agent.name} {...agent} />,
          ...(index < agents.length - 1
            ? [<StageConnector key={`${agent.name}-connector`} />]
            : []),
        ])}
      </div>

      <div className="mt-6 flex justify-end">
        <Link to={ROUTES.APP_VERIFY}>
          <Button>
            Start verification
            <ArrowRight className="h-4 w-4" />
          </Button>
        </Link>
      </div>
    </Panel>
  )
}

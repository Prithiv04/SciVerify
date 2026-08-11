import { Quote } from 'lucide-react'
import { cn } from '@/lib/cn'
import { VerdictBadge } from '@/components/sciverify/VerdictBadge'
import type { VerdictKey } from '@/constants/verdicts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'

export interface EvidenceCardProps {
  title: string
  excerpt: string
  source?: string
  verdict?: VerdictKey
  relevance?: number
  className?: string
}

export function EvidenceCard({
  title,
  excerpt,
  source,
  verdict,
  relevance,
  className,
}: EvidenceCardProps) {
  return (
    <Card className={cn('h-full', className)}>
      <CardHeader>
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3">
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-border bg-surface-elevated">
              <Quote className="h-4 w-4 text-text-muted" />
            </span>
            <div>
              <CardTitle className="text-sm">{title}</CardTitle>
              {source ? <CardDescription>{source}</CardDescription> : null}
            </div>
          </div>
          {verdict ? <VerdictBadge verdict={verdict} size="sm" /> : null}
        </div>
      </CardHeader>
      <CardContent className="space-y-3 pt-0">
        <p className="text-sm leading-relaxed text-text-secondary">{excerpt}</p>
        {relevance !== undefined ? (
          <p className="text-xs text-text-muted">
            Relevance:{' '}
            <span className="font-medium text-text-primary">{relevance}%</span>
          </p>
        ) : null}
      </CardContent>
    </Card>
  )
}

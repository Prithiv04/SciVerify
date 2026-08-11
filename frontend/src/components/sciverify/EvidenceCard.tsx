import { ExternalLink, Quote } from 'lucide-react'
import { cn } from '@/lib/cn'
import { VerdictBadge } from '@/components/sciverify/VerdictBadge'
import { Badge } from '@/components/ui/Badge'
import type { VerdictKey } from '@/constants/verdicts'
import type { EvidenceStrength } from '@/types/verification'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/Card'

const strengthVariant: Record<
  EvidenceStrength,
  'success' | 'warning' | 'default'
> = {
  HIGH: 'success',
  MEDIUM: 'warning',
  LOW: 'default',
}

export interface EvidenceCardProps {
  title: string
  excerpt: string
  source?: string
  authors?: string
  year?: number
  whyItMatters?: string
  strength?: EvidenceStrength
  identifier?: string
  sourceUrl?: string
  verdict?: VerdictKey
  relevance?: number
  className?: string
}

function resolveSourceHref(identifier?: string, sourceUrl?: string) {
  if (sourceUrl) return sourceUrl
  if (identifier?.startsWith('10.')) {
    return `https://doi.org/${identifier}`
  }
  return undefined
}

export function EvidenceCard({
  title,
  excerpt,
  source,
  authors,
  year,
  whyItMatters,
  strength,
  identifier,
  sourceUrl,
  verdict,
  relevance,
  className,
}: EvidenceCardProps) {
  const href = resolveSourceHref(identifier, sourceUrl)
  const sourceLine = [authors, year?.toString(), source].filter(Boolean).join(' · ')

  return (
    <Card className={cn('h-full', className)}>
      <CardHeader className="space-y-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3">
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-border bg-surface-elevated">
              <Quote className="h-4 w-4 text-text-muted" />
            </span>
            <div className="min-w-0">
              <p className="text-xs font-medium uppercase tracking-wide text-text-muted">
                Source
              </p>
              <CardTitle className="mt-1 text-sm leading-snug">{title}</CardTitle>
              {sourceLine ? (
                <CardDescription className="mt-1">{sourceLine}</CardDescription>
              ) : null}
              {identifier ? (
                <p className="mt-1 truncate font-mono text-xs text-text-muted">
                  {identifier}
                </p>
              ) : null}
            </div>
          </div>
          {verdict ? <VerdictBadge verdict={verdict} size="sm" /> : null}
        </div>
      </CardHeader>
      <CardContent className="space-y-4 pt-0">
        <div className="rounded-lg border border-border/70 bg-surface-elevated/40 p-3">
          <p className="text-xs font-medium uppercase tracking-wide text-text-muted">
            Relevant evidence
          </p>
          <p className="mt-2 text-sm leading-relaxed text-text-secondary">
            {excerpt}
          </p>
        </div>

        {whyItMatters ? (
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-text-muted">
              Why this matters
            </p>
            <p className="mt-2 text-sm leading-relaxed text-text-secondary">
              {whyItMatters}
            </p>
          </div>
        ) : null}

        <div className="flex flex-wrap items-center gap-2">
          {strength ? (
            <Badge variant={strengthVariant[strength]} size="sm">
              Strength: {strength}
            </Badge>
          ) : null}
          {relevance !== undefined ? (
            <Badge variant="muted" size="sm">
              Relevance: {relevance}%
            </Badge>
          ) : null}
        </div>

        {href ? (
          <a
            href={href}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 text-sm text-primary hover:text-primary-hover"
          >
            Open source
            <ExternalLink className="h-3.5 w-3.5" />
          </a>
        ) : null}
      </CardContent>
    </Card>
  )
}

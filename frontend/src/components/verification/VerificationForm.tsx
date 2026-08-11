import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import {
  verificationFormSchema,
  type VerificationFormSchema,
} from '@/lib/validations/verification'
import { Button } from '@/components/ui/Button'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import { Panel } from '@/components/ui/Card'
import type { SourceType } from '@/types/verification'

const sourceTypeOptions = [
  { value: 'doi', label: 'DOI' },
  { value: 'url', label: 'URL' },
  { value: 'citation', label: 'Citation' },
  { value: 'reference', label: 'Reference text' },
]

export interface VerificationFormProps {
  onSubmit: (values: VerificationFormSchema) => void
  loading?: boolean
}

export function VerificationForm({ onSubmit, loading = false }: VerificationFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<VerificationFormSchema>({
    resolver: zodResolver(verificationFormSchema),
    defaultValues: {
      claim: '',
      citation: '',
      sourceType: 'doi' as SourceType,
      context: '',
    },
  })

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <Panel padding="md" className="space-y-4">
        <Textarea
          label="Scientific claim"
          placeholder='Example: "AI improves software development productivity."'
          hint="Enter the exact claim you want to verify."
          rows={5}
          error={errors.claim?.message}
          disabled={loading}
          {...register('claim')}
        />
      </Panel>

      <Panel padding="md" className="space-y-4">
        <Select
          label="Source type"
          options={sourceTypeOptions}
          error={errors.sourceType?.message}
          disabled={loading}
          {...register('sourceType')}
        />
        <Textarea
          label="Citation / DOI"
          placeholder="Example: 10.1145/example or paste a full citation string."
          hint="Provide the DOI, citation, or paper identifier that supposedly supports the claim."
          rows={3}
          error={errors.citation?.message}
          disabled={loading}
          {...register('citation')}
        />
        <Textarea
          label="Optional context"
          placeholder="Section, paragraph, or experimental conditions (optional)."
          hint="Add brief context if it helps interpret the claim."
          rows={2}
          error={errors.context?.message}
          disabled={loading}
          {...register('context')}
        />
      </Panel>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-xs text-text-muted">
          Demo workflow — mock verification only. No real AI or external APIs are
          called.
        </p>
        <Button
          type="submit"
          loading={loading}
          disabled={loading}
          className="w-full sm:w-auto"
        >
          {loading ? 'Verifying...' : 'Verify Citation'}
        </Button>
      </div>
    </form>
  )
}

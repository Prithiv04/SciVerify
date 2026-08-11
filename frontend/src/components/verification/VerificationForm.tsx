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
    },
  })

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <Panel padding="md" className="space-y-4">
        <Textarea
          label="Scientific Claim"
          placeholder="Example: The proposed method improves model accuracy by 20% on real-world datasets."
          hint="Enter the exact claim you want to verify."
          rows={4}
          error={errors.claim?.message}
          {...register('claim')}
        />
      </Panel>

      <Panel padding="md" className="space-y-4">
        <Select
          label="Source type"
          options={sourceTypeOptions}
          error={errors.sourceType?.message}
          {...register('sourceType')}
        />
        <Textarea
          label="Citation / Source"
          placeholder="Paste a DOI, URL, citation, or reference."
          hint="Provide the citation that supposedly supports the claim."
          rows={3}
          error={errors.citation?.message}
          {...register('citation')}
        />
      </Panel>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-xs text-text-muted">
          Demo workflow — mock verification only. No real AI or external APIs are called.
        </p>
        <Button type="submit" loading={loading} className="w-full sm:w-auto">
          {loading ? 'Verifying...' : 'Verify Citation'}
        </Button>
      </div>
    </form>
  )
}

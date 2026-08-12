import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { AppHeader } from '@/components/app/AppHeader'
import { VerificationForm } from '@/components/verification/VerificationForm'
import { VerificationLoading } from '@/components/verification/VerificationLoading'
import { VerificationResultView } from '@/components/verification/VerificationResultView'
import { verifyCitationMock } from '@/services/mockVerificationService'
import { useVerificationStore } from '@/stores/verificationStore'
import { ROUTES } from '@/constants'
import { Button } from '@/components/ui/Button'
import { Panel } from '@/components/ui/Card'
import type { VerificationFormSchema } from '@/lib/validations/verification'
import type { VerificationResult } from '@/types/verification'

type VerifyPhase = 'form' | 'loading' | 'result' | 'error'

export default function VerifyPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const getRecord = useVerificationStore((state) => state.getRecord)
  const addRecord = useVerificationStore((state) => state.addRecord)

  const initialRecordId = (location.state as { recordId?: string } | null)
    ?.recordId
  const initialRecord = initialRecordId ? getRecord(initialRecordId) : undefined

  const [phase, setPhase] = useState<VerifyPhase>(
    initialRecord ? 'result' : 'form',
  )
  const [result, setResult] = useState<VerificationResult | null>(
    initialRecord ?? null,
  )
  const [loadingStageIndex, setLoadingStageIndex] = useState(0)
  const [loadingMessage, setLoadingMessage] = useState<string>()
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const handleSubmit = async (values: VerificationFormSchema) => {
    setPhase('loading')
    setErrorMessage(null)
    setLoadingStageIndex(0)
    setLoadingMessage(undefined)

    try {
      const verificationResult = await verifyCitationMock(
        {
          claim: values.claim,
          citation: values.citation,
          sourceType: values.sourceType,
          context: values.context,
        },
        (update) => {
          setLoadingStageIndex(update.stageIndex)
          setLoadingMessage(update.message)
        },
      )

      addRecord(verificationResult)
      setResult(verificationResult)
      setPhase('result')
      toast.success('Mock verification completed.')
    } catch (error) {
      setPhase('error')
      setErrorMessage(
        error instanceof Error
          ? error.message
          : 'Verification could not be completed.',
      )
      toast.error('Verification could not be completed.')
    }
  }

  const handleNewVerification = () => {
    setPhase('form')
    setResult(null)
    setErrorMessage(null)
    navigate(ROUTES.APP_VERIFY, { replace: true, state: null })
  }

  const handleBackToForm = () => {
    if (initialRecord) {
      navigate(ROUTES.APP_HISTORY)
      return
    }
    handleNewVerification()
  }

  return (
    <div>
      {phase === 'form' ? (
        <AppHeader
          eyebrow="New verification"
          title="Evaluate a scientific claim"
          description="Evaluate whether a scientific claim is supported by its cited evidence."
        />
      ) : phase === 'result' ? (
        <AppHeader
          title="Verification report"
          description="Review the complete evidence-backed analysis for this claim."
          actions={
            <Button variant="outline" onClick={handleNewVerification}>
              New verification
            </Button>
          }
        />
      ) : (
        <AppHeader
          eyebrow="Verifying"
          title="Running verification pipeline"
          description="Prosecutor, Defender, and Adjudicator are analyzing the cited evidence."
        />
      )}

      {phase === 'form' ? (
        <VerificationForm onSubmit={handleSubmit} />
      ) : null}

      {phase === 'loading' ? (
        <VerificationLoading
          stageIndex={loadingStageIndex}
          message={loadingMessage}
        />
      ) : null}

      {phase === 'error' ? (
        <Panel padding="md" className="space-y-4 border-danger/30">
          <p className="font-medium text-text-primary">
            Verification could not be completed.
          </p>
          <p className="text-sm text-danger">{errorMessage}</p>
          <Button onClick={() => setPhase('form')}>Try again</Button>
        </Panel>
      ) : null}

      {phase === 'result' && result ? (
        <VerificationResultView result={result} onBack={handleBackToForm} />
      ) : null}
    </div>
  )
}

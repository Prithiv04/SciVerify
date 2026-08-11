import { useMemo, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { AppHeader } from '@/components/app/AppHeader'
import { VerificationForm } from '@/components/verification/VerificationForm'
import { VerificationLoading } from '@/components/verification/VerificationLoading'
import { VerificationResultView } from '@/components/verification/VerificationResultView'
import { VERIFICATION_LOADING_STEPS } from '@/mocks/verification'
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
  const [loadingStep, setLoadingStep] = useState<string>(
    VERIFICATION_LOADING_STEPS[0],
  )
  const [loadingIndex, setLoadingIndex] = useState(0)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const stepIndex = useMemo(
    () =>
      Math.max(
        0,
        VERIFICATION_LOADING_STEPS.findIndex((step) => step === loadingStep),
      ),
    [loadingStep],
  )

  const handleSubmit = async (values: VerificationFormSchema) => {
    setPhase('loading')
    setErrorMessage(null)
    setLoadingStep(VERIFICATION_LOADING_STEPS[0])
    setLoadingIndex(0)

    try {
      const verificationResult = await verifyCitationMock(values, (step) => {
        setLoadingStep(step)
        setLoadingIndex(
          VERIFICATION_LOADING_STEPS.findIndex((item) => item === step),
        )
      })

      addRecord(verificationResult)
      setResult(verificationResult)
      setPhase('result')
      toast.success('Mock verification completed.')
    } catch (error) {
      setPhase('error')
      setErrorMessage(
        error instanceof Error ? error.message : 'Verification failed.',
      )
      toast.error('Mock verification failed.')
    }
  }

  const handleNewVerification = () => {
    setPhase('form')
    setResult(null)
    setErrorMessage(null)
    navigate(ROUTES.APP_VERIFY, { replace: true, state: null })
  }

  return (
    <div>
      <AppHeader
        title="New Verification"
        description="Check whether a scientific claim is supported by its cited source."
        actions={
          phase === 'result' ? (
            <Button variant="outline" onClick={handleNewVerification}>
              New verification
            </Button>
          ) : null
        }
      />

      {phase === 'form' ? (
        <VerificationForm onSubmit={handleSubmit} />
      ) : null}

      {phase === 'loading' ? (
        <VerificationLoading
          currentStep={loadingStep}
          stepIndex={loadingIndex >= 0 ? loadingIndex : stepIndex}
        />
      ) : null}

      {phase === 'error' ? (
        <Panel padding="md" className="space-y-4 border-danger/30">
          <p className="text-sm text-danger">{errorMessage}</p>
          <Button onClick={() => setPhase('form')}>Try again</Button>
        </Panel>
      ) : null}

      {phase === 'result' && result ? <VerificationResultView result={result} /> : null}
    </div>
  )
}

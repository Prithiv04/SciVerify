import axios from 'axios'
import { extractDoi, InvalidDoiError } from '@/lib/doi'
import { apiClient } from '@/services/api'
import {
  mapBackendVerificationToResult,
  mapInsufficientEvidenceResult,
} from '@/services/verificationMapper'
import type {
  BackendVerificationResponse,
  VerificationAnalyzeRequest,
  VerificationApiErrorBody,
} from '@/types/backend-verification'
import type { VerificationFormInput, VerificationResult } from '@/types/verification'

export class VerificationServiceError extends Error {
  status?: number

  constructor(message: string, status?: number) {
    super(message)
    this.name = 'VerificationServiceError'
    this.status = status
  }
}

function parseApiError(error: unknown): VerificationServiceError {
  if (error instanceof VerificationServiceError) {
    return error
  }

  if (error instanceof InvalidDoiError) {
    return new VerificationServiceError(error.message, 400)
  }

  if (axios.isAxiosError<VerificationApiErrorBody>(error)) {
    if (!error.response) {
      return new VerificationServiceError(
        'Unable to connect to the SciVerify backend. Please make sure the backend server is running.',
      )
    }

    const status = error.response.status
    const detail = error.response.data?.detail

    if (status === 400) {
      const message =
        typeof detail === 'string'
          ? detail
          : 'Please provide a valid DOI and claim.'
      return new VerificationServiceError(message, status)
    }

    if (status === 404) {
      return new VerificationServiceError(
        'The cited paper could not be found.',
        status,
      )
    }

    if (status === 503) {
      const message =
        typeof detail === 'string'
          ? detail
          : "The cited paper's full text could not be retrieved."
      return new VerificationServiceError(message, status)
    }

    const fallback =
      typeof detail === 'string'
        ? detail
        : 'Verification could not be completed.'
    return new VerificationServiceError(fallback, status)
  }

  if (error instanceof Error) {
    return new VerificationServiceError(error.message)
  }

  return new VerificationServiceError('Verification could not be completed.')
}

function buildRequest(input: VerificationFormInput): VerificationAnalyzeRequest {
  const doi = extractDoi(input.citation)
  return {
    claim: input.claim.trim(),
    doi,
  }
}

function handleApplicationStatus(
  response: BackendVerificationResponse,
  input: VerificationFormInput,
): VerificationResult {
  if (response.status === 'insufficient_evidence') {
    return mapInsufficientEvidenceResult(response, input)
  }

  if (response.status === 'llm_unavailable') {
    throw new VerificationServiceError(
      response.detail ??
        'AI verification is currently unavailable. Configure the backend LLM provider and try again.',
    )
  }

  if (response.status === 'verification_failed') {
    throw new VerificationServiceError(
      response.detail ?? 'Verification could not be completed.',
    )
  }

  if (response.status !== 'success') {
    throw new VerificationServiceError(
      response.detail ?? 'Verification could not be completed.',
    )
  }

  if (!response.verdict) {
    throw new VerificationServiceError(
      'Verification completed without a final verdict.',
    )
  }

  return mapBackendVerificationToResult(response, input)
}

export async function verifyCitation(
  input: VerificationFormInput,
): Promise<VerificationResult> {
  const request = buildRequest(input)

  try {
    const { data } = await apiClient.post<BackendVerificationResponse>(
      '/api/verification/analyze',
      request,
    )

    return handleApplicationStatus(data, input)
  } catch (error) {
    throw parseApiError(error)
  }
}

export { extractDoi, InvalidDoiError }

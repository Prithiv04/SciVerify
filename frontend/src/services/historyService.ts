import { extractDoi } from '@/lib/doi'
import { getSupabaseClient, isSupabaseConfigured } from '@/lib/supabase'
import type {
  VerificationHistoryInsert,
  VerificationHistoryRow,
} from '@/types/history'
import type { VerificationResult } from '@/types/verification'

const GENERIC_HISTORY_ERROR = 'Unable to access verification history.'

function resolveDoi(result: VerificationResult): string {
  if (result.paperDoi?.trim()) {
    return result.paperDoi.trim()
  }

  try {
    return extractDoi(result.citation)
  } catch {
    return result.citation.trim().slice(0, 255) || 'unknown'
  }
}

function toInsertRow(
  userId: string,
  result: VerificationResult,
): VerificationHistoryInsert {
  return {
    id: result.id,
    user_id: userId,
    claim: result.claim,
    doi: resolveDoi(result),
    paper_title: result.paperTitle ?? null,
    verdict: result.verdict,
    confidence: result.confidence,
    summary: result.summary,
    result_json: result,
    created_at: result.createdAt,
  }
}

function rebuildMinimalResult(row: VerificationHistoryRow): VerificationResult {
  return {
    id: row.id,
    claim: row.claim,
    citation: row.doi,
    sourceType: 'doi',
    citationStatus: row.verdict === 'FABRICATED' ? 'fabricated' : 'verified',
    verdict: row.verdict,
    confidence: Number(row.confidence),
    summary: row.summary ?? 'Verification summary unavailable.',
    reasoning: row.summary ?? 'Verification reasoning unavailable.',
    paperTitle: row.paper_title ?? undefined,
    paperDoi: row.doi,
    evidenceFactors: [],
    prosecutor: {
      role: 'Prosecutor',
      summary: 'Analysis unavailable.',
      finding: 'Stored report did not include agent details.',
      status: 'completed',
    },
    defender: {
      role: 'Defender',
      summary: 'Analysis unavailable.',
      finding: 'Stored report did not include agent details.',
      status: 'completed',
    },
    adjudicator: {
      role: 'Adjudicator',
      summary: 'Analysis unavailable.',
      finding: 'Stored report did not include agent details.',
      status: 'completed',
    },
    evidence: [],
    suggestedCorrection: null,
    createdAt: row.created_at,
  }
}

export function parseStoredVerificationResult(
  row: VerificationHistoryRow,
): VerificationResult {
  const raw = row.result_json

  if (raw && typeof raw === 'object' && 'claim' in raw && 'verdict' in raw) {
    return {
      ...(raw as VerificationResult),
      id: row.id,
      createdAt: row.created_at,
      paperTitle: (raw as VerificationResult).paperTitle ?? row.paper_title ?? undefined,
      paperDoi: (raw as VerificationResult).paperDoi ?? row.doi,
    }
  }

  return rebuildMinimalResult(row)
}

export async function saveVerificationHistory(
  userId: string,
  result: VerificationResult,
): Promise<void> {
  if (!isSupabaseConfigured()) {
    throw new Error(GENERIC_HISTORY_ERROR)
  }

  const { error } = await getSupabaseClient()
    .from('verification_history')
    .upsert(toInsertRow(userId, result), { onConflict: 'id' })

  if (error) {
    throw new Error(GENERIC_HISTORY_ERROR)
  }
}

export async function listVerificationHistory(
  userId: string,
): Promise<VerificationResult[]> {
  if (!isSupabaseConfigured()) {
    throw new Error(GENERIC_HISTORY_ERROR)
  }

  const { data, error } = await getSupabaseClient()
    .from('verification_history')
    .select('*')
    .eq('user_id', userId)
    .order('created_at', { ascending: false })

  if (error) {
    throw new Error(GENERIC_HISTORY_ERROR)
  }

  return (data as VerificationHistoryRow[]).map(parseStoredVerificationResult)
}

export async function deleteVerificationHistory(
  userId: string,
  recordId: string,
): Promise<void> {
  if (!isSupabaseConfigured()) {
    throw new Error(GENERIC_HISTORY_ERROR)
  }

  const { error } = await getSupabaseClient()
    .from('verification_history')
    .delete()
    .eq('user_id', userId)
    .eq('id', recordId)

  if (error) {
    throw new Error(GENERIC_HISTORY_ERROR)
  }
}

import { create } from 'zustand'
import { MOCK_VERIFICATION_HISTORY } from '@/mocks/verification'
import type { VerificationResult } from '@/types/verification'

interface VerificationStoreState {
  records: VerificationResult[]
  addRecord: (record: VerificationResult) => void
  getRecord: (id: string) => VerificationResult | undefined
}

export const useVerificationStore = create<VerificationStoreState>((set, get) => ({
  records: MOCK_VERIFICATION_HISTORY,
  addRecord: (record) =>
    set((state) => ({
      records: [record, ...state.records],
    })),
  getRecord: (id) => get().records.find((record) => record.id === id),
}))

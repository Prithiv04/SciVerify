import { z } from 'zod'

export const verificationFormSchema = z.object({
  claim: z
    .string()
    .trim()
    .min(10, 'Please enter the scientific claim.')
    .max(2000, 'Claim must be 2000 characters or fewer.'),
  citation: z
    .string()
    .trim()
    .min(5, 'Please provide the citation or source.')
    .max(2000, 'Citation must be 2000 characters or fewer.'),
  sourceType: z.enum(['doi', 'url', 'citation', 'reference']),
})

export type VerificationFormSchema = z.infer<typeof verificationFormSchema>

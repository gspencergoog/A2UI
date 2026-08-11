/**
 * Copyright 2026 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * @fileoverview Dynamic ValidationResult schema and evaluator for A2UI v1.0.
 *
 * Implements dynamic form validation result parsing with fallback to legacy
 * rule.message string formats.
 */

import {z} from 'zod';

export const ValidationSeveritySchema = z.enum(['error', 'warning', 'info']);
export type ValidationSeverity = z.infer<typeof ValidationSeveritySchema>;

export const ValidationResultSchema = z.object({
  valid: z.boolean(),
  code: z.string().optional(),
  message: z.string().optional(),
  severity: ValidationSeveritySchema.optional().default('error'),
});

export type ValidationResult = z.infer<typeof ValidationResultSchema>;

export interface CheckRule {
  message?: string;
  code?: string;
}

/**
 * Normalizes rule execution outputs into a canonical ValidationResult.
 *
 * @param rawResult Raw execution output from a validation rule.
 * @param rule Fallback rule definition providing static message or code if missing.
 */
export function normalizeValidationResult(
  rawResult: boolean | Partial<ValidationResult> | undefined | null,
  rule?: CheckRule,
): ValidationResult {
  if (typeof rawResult === 'boolean') {
    return {
      valid: rawResult,
      code: rule?.code,
      message: rawResult ? undefined : (rule?.message ?? 'Validation failed.'),
      severity: 'error',
    };
  }

  if (typeof rawResult === 'object' && rawResult !== null) {
    const valid = Boolean(rawResult.valid);
    return {
      valid,
      code: rawResult.code ?? rule?.code,
      message: rawResult.message ?? (valid ? undefined : (rule?.message ?? 'Validation failed.')),
      severity: rawResult.severity ?? 'error',
    };
  }

  return {
    valid: false,
    code: rule?.code,
    message: rule?.message ?? 'Validation failed.',
    severity: 'error',
  };
}

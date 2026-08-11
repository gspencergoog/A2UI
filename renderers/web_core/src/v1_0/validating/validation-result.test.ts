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

import {describe, it} from 'node:test';
import assert from 'node:assert/strict';
import {normalizeValidationResult} from './validation-result.js';

describe('ValidationResult Evaluator Tests (v1.0)', () => {
  it('normalizes boolean result with rule message fallback', () => {
    const pass = normalizeValidationResult(true, {message: 'Field required'});
    assert.equal(pass.valid, true);
    assert.equal(pass.message, undefined);

    const fail = normalizeValidationResult(false, {message: 'Field required', code: 'REQ'});
    assert.equal(fail.valid, false);
    assert.equal(fail.message, 'Field required');
    assert.equal(fail.code, 'REQ');
  });

  it('normalizes dynamic ValidationResult object', () => {
    const res = normalizeValidationResult({
      valid: false,
      code: 'INVALID_FORMAT',
      message: 'Invalid email address',
      severity: 'warning',
    });

    assert.equal(res.valid, false);
    assert.equal(res.code, 'INVALID_FORMAT');
    assert.equal(res.message, 'Invalid email address');
    assert.equal(res.severity, 'warning');
  });

  it('falls back to rule message if dynamic object omits message on failure', () => {
    const res = normalizeValidationResult({valid: false}, {message: 'Fallback message'});
    assert.equal(res.valid, false);
    assert.equal(res.message, 'Fallback message');
    assert.equal(res.severity, 'error');
  });
});

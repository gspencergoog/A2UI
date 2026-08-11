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
